import re
import uuid
from typing import Any, Dict, List

from llm import run_anthropic_instructor
from pydantic import BaseModel, Field

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


def parse_to_boolean_structure(content: str) -> Dict[str, Any]:
    lines = [line for line in content.split("\n") if line.strip()]

    parsed_items = parse_hierarchy(lines)

    if len(parsed_items) == 1:
        return convert_to_boolean_logic(parsed_items[0])
    else:
        return {
            "id": generate_id(),
            "operator": "and",
            "description": "Root criteria evaluation",
            "children": [convert_to_boolean_logic(item) for item in parsed_items],
            "value": None,
        }


def parse_hierarchy(lines: List[str]) -> List[Dict[str, Any]]:
    result = []
    stack = []

    for line in lines:
        if not line.strip():
            continue

        match = re.match(r"^(\s*)([-*•]\s*)(.*)", line)
        if not match:
            continue

        indent, bullet, text = match.groups()
        level = len(indent) // 2
        clean_text = text.strip()

        # Create item
        item = {"text": clean_text, "level": level, "children": []}

        # Find correct parent
        while stack and stack[-1]["level"] >= level:
            stack.pop()

        if not stack:
            result.append(item)
        else:
            stack[-1]["children"].append(item)

        stack.append(item)

    return result


def convert_to_boolean_logic(item: Dict[str, Any]) -> Dict[str, Any]:
    """Convert hierarchical item to boolean logic structure"""
    text = item["text"]
    children = item.get("children", [])

    # Detect boolean operators in the text
    operator = detect_operator(text)

    # Clean the text (remove operator keywords)
    clean_text = clean_operator_text(text)

    if not children:
        # Leaf node - individual criterion
        return {
            "id": generate_id(),
            "operator": None,
            "description": clean_text,
            "statement": clean_text,
            "value": None,
            "type": "criterion",
        }
    else:
        # Parent node - boolean operation
        return {
            "id": generate_id(),
            "operator": operator,
            "description": clean_text,
            "children": [convert_to_boolean_logic(child) for child in children],
            "value": None,
            "type": "operation",
        }


def detect_operator(text: str) -> str:
    """Detect boolean operator from text"""
    text_upper = text.upper()

    if text_upper.startswith("AND ") or " AND " in text_upper:
        return "and"
    elif text_upper.startswith("OR ") or " OR " in text_upper:
        return "or"
    elif text_upper.startswith("NOT ") or " NOT " in text_upper:
        return "not"
    else:
        # Default operator based on context
        return "and"  # Most criteria lists are AND by default


def clean_operator_text(text: str) -> str:
    """Remove operator keywords from text"""
    # Remove leading AND/OR/NOT keywords
    text = re.sub(r"^(AND|OR|NOT)\s+", "", text, flags=re.IGNORECASE)
    return text.strip()


def generate_id() -> str:
    """Generate unique identifier"""
    return str(uuid.uuid4())[:8]


def evaluate_boolean_structure(structure: Dict[str, Any]) -> bool:
    """
    Evaluate the boolean structure to get final result

    Args:
        structure: Boolean logic structure with values filled in

    Returns:
        bool: Final evaluation result
    """
    if structure["type"] == "criterion":
        # Leaf criterion - handle both old format (direct boolean) and new format (dict)
        value_data = structure["value"]
        if isinstance(value_data, dict):
            return value_data.get("is_met", False)
        else:
            return value_data if value_data is not None else False

    elif structure["type"] == "operation":
        # Boolean operation
        operator = structure["operator"]
        children_results = [
            evaluate_boolean_structure(child) for child in structure["children"]
        ]

        if operator == "and":
            return all(children_results)
        elif operator == "or":
            return any(children_results)
        elif operator == "not":
            # For NOT, typically applied to a single child or all children
            return not all(children_results)
        else:
            # Default to AND
            return all(children_results)

    return False


def set_criterion_value(
    structure: Dict[str, Any], criterion_id: str, value_data: Dict[str, Any]
) -> None:
    """
    Set the value and metadata for a specific criterion by ID

    Args:
        structure: Boolean logic structure
        criterion_id: ID of the criterion to set
        value_data: Dictionary containing criterion data (e.g., {"is_met": bool, "justification": str, "citation": str})
    """
    if structure["id"] == criterion_id:
        structure["value"] = value_data
        return

    if "children" in structure:
        for child in structure["children"]:
            set_criterion_value(child, criterion_id, value_data)


def get_all_criteria(structure: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract all individual criteria from the structure for UI display

    Returns:
        List of dicts with id, description, and current value data
    """
    criteria = []

    def extract_criteria(node):
        if node["type"] == "criterion":
            value_data = node["value"]
            criteria.append(
                {
                    "id": node["id"],
                    "description": node["description"],
                    "value": value_data,
                }
            )
        elif "children" in node:
            for child in node["children"]:
                extract_criteria(child)

    extract_criteria(structure)
    return criteria
