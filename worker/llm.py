import asyncio
import base64
from typing import Any, Dict, List, Optional, Type

import instructor
from anthropic import Anthropic, AsyncAnthropic
from instructor.multimodal import PDF
from openai import AsyncOpenAI, OpenAI
from pydantic import BaseModel
from settings import settings


def create_instructor_client(provider: str = "openai") -> instructor.Instructor:
    if provider.lower() == "openai":
        openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        return instructor.from_openai(openai_client)
    elif provider.lower() == "anthropic":
        anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        return instructor.from_anthropic(anthropic_client)
    else:
        raise ValueError(
            f"Unsupported provider: {provider}. Use 'openai' or 'anthropic'."
        )


def create_async_instructor_client(provider: str = "openai") -> instructor.Instructor:
    if provider.lower() == "openai":
        openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        return instructor.from_openai(openai_client)
    elif provider.lower() == "anthropic":
        anthropic_client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        return instructor.from_anthropic(anthropic_client)
    else:
        raise ValueError(
            f"Unsupported provider: {provider}. Use 'openai' or 'anthropic'."
        )


def run_instructor(
    response_model: Type[BaseModel],
    user_message: str,
    model: str = "gpt-4o",
    provider: str = "openai",
    pdf_content: Optional[bytes] = None,
    **kwargs,
) -> BaseModel:
    """
    Run instructor with support for both OpenAI and Anthropic providers.

    Args:
        response_model: Pydantic model class for structured response
        user_message: The user's message/prompt
        model: Model name (e.g., "gpt-4o" for OpenAI, "claude-3-5-sonnet-20241022" for Anthropic)
        provider: Either "openai" or "anthropic"
        pdf_content: Optional PDF content as bytes (only supported with Anthropic)
        **kwargs: Additional arguments passed to the completion call

    Returns:
        Instance of response_model with the structured response
    """
    if provider.lower() == "openai" and pdf_content is not None:
        raise ValueError("PDF content is not supported with OpenAI provider")

    client = create_instructor_client(provider)

    # Handle message construction based on provider and content type
    if provider.lower() == "anthropic" and pdf_content:
        # For Anthropic with PDF content
        encoded_pdf = base64.b64encode(pdf_content).decode("utf-8")
        pdf = PDF(source="base64", data=encoded_pdf, media_type="application/pdf")

        messages = [
            {
                "role": "user",
                "content": [{"type": "text", "text": user_message}, pdf.to_anthropic()],
            }
        ]
    else:
        # For OpenAI or Anthropic without PDF
        messages = [
            {"role": "user", "content": user_message},
        ]

    # Add max_tokens for Anthropic if not provided
    if provider.lower() == "anthropic" and "max_tokens" not in kwargs:
        kwargs["max_tokens"] = 4096

    response = client.chat.completions.create(
        model=model,
        response_model=response_model,
        messages=messages,
        **kwargs,
    )

    return response


async def run_instructor_async(
    response_model: Type[BaseModel],
    user_message: str,
    model: str = "gpt-4o",
    provider: str = "openai",
    pdf_content: Optional[bytes] = None,
    **kwargs,
) -> BaseModel:
    """
    Run instructor asynchronously with support for both OpenAI and Anthropic providers.

    Args:
        response_model: Pydantic model class for structured response
        user_message: The user's message/prompt
        model: Model name (e.g., "gpt-4o" for OpenAI, "claude-sonnet-4-20250514" for Anthropic)
        provider: Either "openai" or "anthropic"
        pdf_content: Optional PDF content as bytes (only supported with Anthropic)
        **kwargs: Additional arguments passed to the completion call

    Returns:
        Instance of response_model with the structured response
    """
    if provider.lower() == "openai" and pdf_content is not None:
        raise ValueError("PDF content is not supported with OpenAI provider")

    client = create_async_instructor_client(provider)

    # Handle message construction based on provider and content type
    if provider.lower() == "anthropic" and pdf_content:
        # For Anthropic with PDF content
        encoded_pdf = base64.b64encode(pdf_content).decode("utf-8")
        pdf = PDF(source="base64", data=encoded_pdf, media_type="application/pdf")

        messages = [
            {
                "role": "user",
                "content": [{"type": "text", "text": user_message}, pdf.to_anthropic()],
            }
        ]
    else:
        # For OpenAI or Anthropic without PDF
        messages = [
            {"role": "user", "content": user_message},
        ]

    # Add max_tokens for Anthropic if not provided
    if provider.lower() == "anthropic" and "max_tokens" not in kwargs:
        kwargs["max_tokens"] = 4096

    response = await client.chat.completions.create(
        model=model,
        response_model=response_model,
        messages=messages,
        **kwargs,
    )

    return response


def run_openai_instructor(
    response_model: Type[BaseModel],
    user_message: str,
    model: str = "gpt-4o",
    **kwargs,
) -> BaseModel:
    """Convenience function for OpenAI-only usage."""
    return run_instructor(
        response_model=response_model,
        user_message=user_message,
        model=model,
        provider="openai",
        **kwargs,
    )


def run_anthropic_instructor(
    response_model: Type[BaseModel],
    user_message: str,
    model: str = "claude-sonnet-4-20250514",
    pdf_content: Optional[bytes] = None,
    **kwargs,
) -> BaseModel:
    """Convenience function for Anthropic usage with optional PDF support."""
    # Add max_tokens for Anthropic if not provided
    if "max_tokens" not in kwargs:
        kwargs["max_tokens"] = 16384

    return run_instructor(
        response_model=response_model,
        user_message=user_message,
        model=model,
        provider="anthropic",
        pdf_content=pdf_content,
        **kwargs,
    )


async def run_batch_completions(
    requests: List[Dict[str, Any]],
    max_concurrent: int = 10,
) -> List[BaseModel]:
    """
    Run multiple completions concurrently in batches.

    Args:
        requests: List of dictionaries containing completion parameters.
                 Each dict should have keys matching run_instructor_async parameters:
                 - response_model: Pydantic model class
                 - user_message: The user's message/prompt
                 - model: Model name (optional, defaults per provider)
                 - provider: Either "openai" or "anthropic" (optional, defaults to "openai")
                 - pdf_content: Optional PDF content (optional)
                 - **kwargs: Additional arguments
        max_concurrent: Maximum number of concurrent requests

    Returns:
        List of response model instances in the same order as requests

    Example:
        requests = [
            {
                "response_model": MyModel,
                "user_message": "Generate data 1",
                "provider": "anthropic",
                "model": "claude-sonnet-4-20250514"
            },
            {
                "response_model": MyModel,
                "user_message": "Generate data 2",
                "provider": "anthropic",
                "model": "claude-sonnet-4-20250514"
            }
        ]
        results = await run_batch_completions(requests)
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def _run_single_completion(request: Dict[str, Any]) -> BaseModel:
        async with semaphore:
            return await run_instructor_async(**request)

    # Create tasks for all requests
    tasks = [_run_single_completion(request) for request in requests]

    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks)

    return results


def run_anthropic_batch_sync(
    response_model: Type[BaseModel],
    user_messages: List[str],
    model: str = "claude-sonnet-4-20250514",
    max_concurrent: int = 10,
    **kwargs,
) -> List[BaseModel]:
    """Synchronous wrapper for Anthropic batch processing."""
    return asyncio.run(
        run_anthropic_batch(
            response_model, user_messages, model, max_concurrent, **kwargs
        )
    )


async def run_anthropic_batch(
    response_model: Type[BaseModel],
    user_messages: List[str],
    model: str = "claude-sonnet-4-20250514",
    max_concurrent: int = 10,
    **kwargs,
) -> List[BaseModel]:
    """
    Run multiple Anthropic completions concurrently.

    Args:
        response_model: Pydantic model class for structured response
        user_messages: List of user messages/prompts
        model: Model name
        max_concurrent: Maximum number of concurrent requests
        **kwargs: Additional arguments passed to each completion call

    Returns:
        List of response model instances
    """
    # Add max_tokens for Anthropic if not provided
    if "max_tokens" not in kwargs:
        kwargs["max_tokens"] = 16384

    requests = [
        {
            "response_model": response_model,
            "user_message": message,
            "model": model,
            "provider": "anthropic",
            **kwargs,
        }
        for message in user_messages
    ]

    return await run_batch_completions(requests, max_concurrent=max_concurrent)
