from typing import List

from database import (
    MedicalNecessityQuestion,
    PriorAuthorization,
    get_db,
)
from fastapi import APIRouter, Depends, HTTPException
from schemas import (
    MedicalNecessityQuestionResponse,
    QuestionAnswerUpdate,
)
from sqlalchemy.orm import Session

router = APIRouter()


@router.get(
    "/prior-authorizations/{auth_id}/questions",
    response_model=List[MedicalNecessityQuestionResponse],
)
def get_medical_necessity_questions(auth_id: str, db: Session = Depends(get_db)):
    """Get medical necessity questions for prior authorization"""
    prior_auth = (
        db.query(PriorAuthorization).filter(PriorAuthorization.id == auth_id).first()
    )
    if not prior_auth:
        raise HTTPException(status_code=404, detail="Prior authorization not found")

    questions = (
        db.query(MedicalNecessityQuestion)
        .filter(MedicalNecessityQuestion.prior_auth_id == auth_id)
        .all()
    )
    return questions


@router.put("/prior-authorizations/{auth_id}/questions")
def update_question_answers(
    auth_id: str, answers: List[QuestionAnswerUpdate], db: Session = Depends(get_db)
):
    """Update answers to medical necessity questions"""
    prior_auth = (
        db.query(PriorAuthorization).filter(PriorAuthorization.id == auth_id).first()
    )
    if not prior_auth:
        raise HTTPException(status_code=404, detail="Prior authorization not found")

    for answer_update in answers:
        question = (
            db.query(MedicalNecessityQuestion)
            .filter(
                MedicalNecessityQuestion.id == answer_update.question_id,
                MedicalNecessityQuestion.prior_auth_id == auth_id,
            )
            .first()
        )

        if question:
            question.answer = answer_update.answer

    db.commit()
    return {"message": "Answers updated successfully"}
