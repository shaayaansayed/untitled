import asyncio

from celery import Celery, chain
from database import PriorAuthorization, SessionLocal, UploadedFile
from llm import run_batch_completions
from pydantic import BaseModel, Field
from services.auth_service import (
    extract_and_format_statements,
    get_all_criteria,
    parse_to_boolean_structure,
    set_criterion_value,
)
from services.file_service import FileService
from settings import settings
from sqlalchemy.orm.attributes import flag_modified

app = Celery("worker")
app.conf.broker_url = settings.REDIS_URL
app.conf.result_backend = settings.REDIS_URL


class CriterionAnswer(BaseModel):
    answer: str = Field(..., description="YES, NO, or UNCLEAR")
    explanation: str = Field(..., description="Brief explanation for the decision")


@app.task
def hello_world():
    """Simple test task"""
    print("Hello from Celery worker!")
    return "Task completed successfully"


@app.task
def process_prior_auth_document(prior_auth_id: str):
    """Process prior authorization document and extract questions"""

    db = SessionLocal()
    try:
        # Get the prior authorization with its associated files
        prior_auth = (
            db.query(PriorAuthorization)
            .filter(PriorAuthorization.id == prior_auth_id)
            .first()
        )

        if not prior_auth:
            raise Exception(f"Prior authorization {prior_auth_id} not found")

        if not prior_auth.auth_document_id:
            raise Exception(
                f"No auth document associated with prior auth {prior_auth_id}"
            )

        # Get the auth document file
        auth_file = (
            db.query(UploadedFile)
            .filter(UploadedFile.id == prior_auth.auth_document_id)
            .first()
        )

        if not auth_file:
            raise Exception("Auth document file not found")

        # Read and process the file
        file_content = FileService.read_file(auth_file.file_path)
        criteria = extract_and_format_statements(file_content)
        boolean_structure = parse_to_boolean_structure(criteria)

        # Update the prior authorization with extracted questions
        prior_auth.auth_questions = boolean_structure
        db.commit()

        print(f"Processed auth questions for prior auth {prior_auth_id}")

        # Return data for next task in chain
        return {
            "prior_auth_id": prior_auth_id,
            "status": "questions_extracted",
            "questions_count": len(boolean_structure.get("children", [])),
        }

    except Exception as e:
        db.rollback()
        print(f"Error processing prior auth {prior_auth_id}: {str(e)}")
        raise
    finally:
        db.close()


@app.task
def answer_questions_with_notes(previous_result):
    """Answer extracted questions using RAG on vectorized clinical notes"""

    # Extract prior_auth_id from previous task result
    prior_auth_id = previous_result["prior_auth_id"]

    db = SessionLocal()
    try:
        # Get the prior authorization with its associated files
        prior_auth = (
            db.query(PriorAuthorization)
            .filter(PriorAuthorization.id == prior_auth_id)
            .first()
        )

        if not prior_auth:
            raise Exception(f"Prior authorization {prior_auth_id} not found")

        if not prior_auth.clinical_notes_id:
            raise Exception(
                f"No clinical notes associated with prior auth {prior_auth_id}"
            )

        # Get the clinical notes file
        clinical_notes_file = (
            db.query(UploadedFile)
            .filter(UploadedFile.id == prior_auth.clinical_notes_id)
            .first()
        )

        if not clinical_notes_file:
            raise Exception("Clinical notes file not found")

        # Read the clinical notes file
        clinical_notes_content = FileService.read_file(clinical_notes_file.file_path)

        # Get the boolean structure with questions
        boolean_structure = prior_auth.auth_questions

        # Extract all individual criteria that need to be answered
        criteria_to_answer = get_all_criteria(boolean_structure)

        if not criteria_to_answer:
            print(f"No criteria found to answer for prior auth {prior_auth_id}")
            return {
                "prior_auth_id": prior_auth_id,
                "status": "completed",
                "questions_count": previous_result.get("questions_count", 0),
                "answers_generated": 0,
            }

        # Prepare prompts for all criteria
        prompts = []
        for criterion in criteria_to_answer:
            prompt = f"""Based on the provided clinical notes, determine if the following medical criterion is met:

CRITERION: {criterion["description"]}

Please analyze the clinical notes thoroughly and respond with either:
- "YES" if the criterion is clearly met based on the clinical documentation
- "NO" if the criterion is clearly not met based on the clinical documentation  
- "UNCLEAR" if there is insufficient information in the clinical notes to make a determination

Provide a brief explanation for your decision based on specific information found (or not found) in the clinical notes."""
            prompts.append(prompt)

        print(
            f"Processing {len(criteria_to_answer)} criteria in batch for prior auth {prior_auth_id}"
        )

        # Process all criteria in batch
        try:
            # Create request dictionaries for batch processing
            requests = []
            for prompt in prompts:
                requests.append(
                    {
                        "response_model": CriterionAnswer,
                        "user_message": prompt,
                        "model": "claude-sonnet-4-20250514",
                        "provider": "anthropic",
                        "pdf_content": clinical_notes_content,
                        "max_tokens": 16384,
                    }
                )

            # Use the async batch function with asyncio.run
            batch_responses = asyncio.run(
                run_batch_completions(requests, max_concurrent=5)
            )

            # Update the boolean structure with all answers
            answers_generated = 0
            for i, (criterion, response) in enumerate(
                zip(criteria_to_answer, batch_responses)
            ):
                try:
                    # Convert to boolean (YES = True, NO/UNCLEAR = False)
                    is_met = response.answer.upper() == "YES"

                    # Update the boolean structure with the answer and justification
                    value_data = {
                        "is_met": is_met,
                        "justification": response.explanation,
                        "answer": response.answer.upper(),
                    }
                    set_criterion_value(boolean_structure, criterion["id"], value_data)
                    answers_generated += 1

                    print(
                        f"✓ Answered criterion {criterion['id']}: {response.answer} - {response.explanation}"
                    )

                except Exception as e:
                    print(
                        f"✗ Error processing response for criterion {criterion['id']}: {str(e)}"
                    )
                    # Set to False if we can't process the response
                    fallback_data = {
                        "is_met": False,
                        "justification": f"Error processing response: {str(e)}",
                        "answer": "UNCLEAR",
                    }
                    set_criterion_value(
                        boolean_structure, criterion["id"], fallback_data
                    )

        except Exception as e:
            print(f"✗ Error in batch processing: {str(e)}")
            # Fallback: set all criteria to False if batch processing fails
            for criterion in criteria_to_answer:
                fallback_data = {
                    "is_met": False,
                    "justification": f"Batch processing failed: {str(e)}",
                    "answer": "UNCLEAR",
                }
                set_criterion_value(boolean_structure, criterion["id"], fallback_data)

        # Update the prior authorization with answered questions
        prior_auth.auth_questions = boolean_structure
        flag_modified(prior_auth, "auth_questions")
        db.commit()

        print(
            f"Completed answering {answers_generated} questions for prior auth {prior_auth_id}"
        )

        # Return final result
        return {
            "prior_auth_id": prior_auth_id,
            "status": "completed",
            "questions_count": previous_result.get("questions_count", 0),
            "answers_generated": answers_generated,
        }

    except Exception as e:
        db.rollback()
        print(f"Error answering questions for prior auth {prior_auth_id}: {str(e)}")
        raise
    finally:
        db.close()


# Helper function to create the processing workflow chain
def create_processing_workflow(prior_auth_id: str):
    """Create a Celery chain for processing a prior authorization"""
    return chain(
        process_prior_auth_document.s(prior_auth_id),
        answer_questions_with_notes.s(),
    )


@app.task
def start_processing_workflow(prior_auth_id: str):
    """Start the complete processing workflow for a prior authorization"""
    try:
        workflow = create_processing_workflow(prior_auth_id)
        result = workflow.apply_async()

        print(
            f"✓ Started processing workflow for prior auth {prior_auth_id} (chain ID: {result.id})"
        )
        return {
            "status": "workflow_started",
            "prior_auth_id": prior_auth_id,
            "chain_id": result.id,
        }
    except Exception as e:
        print(f"✗ Failed to start workflow for {prior_auth_id}: {str(e)}")
        raise
