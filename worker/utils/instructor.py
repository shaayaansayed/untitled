import base64
from typing import Optional, Type

import instructor
from anthropic import Anthropic
from config.settings import settings
from instructor.multimodal import PDF
from openai import OpenAI
from pydantic import BaseModel


def create_instructor_client(provider: str = "openai") -> instructor.Instructor:
    """
    Create an instructor client using API key from settings.

    Args:
        provider: Either "openai" or "anthropic"

    Returns:
        Instructor client instance
    """
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


# Example usage functions for convenience
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
