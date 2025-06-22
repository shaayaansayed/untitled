from pydantic import BaseModel, Field
from utils.instructor import run_anthropic_instructor

PROMPT = """The document contains medical necessity criteria. Your task is to extract approval criteria from the document and format it.

Use this hierarchical bullet format:

<format>
- [OPERATOR] Group Name
  - Statement 1
  - Statement 2
  - [OPERATOR] Nested Group Name
    - Nested Statement 1
    - Nested Statement 2
</format>

Here are some guidelines to follow: 

<guidelines>
- Place operators at the beginning of group headers. Use 'AND' or 'OR' as the operator. 
- Use 2 spaces for each level of nesting. 
- Only extract approval criteria. Do not extract non-approval criteria. 
</guidelines> 
"""


class Criteria(BaseModel):
    criteria: str = Field(
        ..., description="The extracted criteria in the format specified above."
    )


def extract_and_format_statements(pdf_bytes: bytes) -> str:
    response = run_anthropic_instructor(
        Criteria,
        PROMPT,
        pdf_content=pdf_bytes,
    )
    return response.criteria
