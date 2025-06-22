import re
import uuid
from typing import Any, Dict, List


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
        # Leaf criterion
        return structure["value"] if structure["value"] is not None else False

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
    structure: Dict[str, Any], criterion_id: str, value: bool
) -> None:
    """
    Set the value for a specific criterion by ID

    Args:
        structure: Boolean logic structure
        criterion_id: ID of the criterion to set
        value: True/False value for the criterion
    """
    if structure["id"] == criterion_id:
        structure["value"] = value
        return

    if "children" in structure:
        for child in structure["children"]:
            set_criterion_value(child, criterion_id, value)


def get_all_criteria(structure: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Extract all individual criteria from the structure for UI display

    Returns:
        List of dicts with id, description, and current value
    """
    criteria = []

    def extract_criteria(node):
        if node["type"] == "criterion":
            criteria.append(
                {
                    "id": node["id"],
                    "description": node["description"],
                    "value": node["value"],
                }
            )
        elif "children" in node:
            for child in node["children"]:
                extract_criteria(child)

    extract_criteria(structure)
    return criteria
