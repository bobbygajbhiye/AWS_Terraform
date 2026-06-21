from __future__ import annotations

import ast
import operator
import re
from decimal import Decimal, DivisionByZero, InvalidOperation, getcontext
from typing import Callable


getcontext().prec = 28

MAX_EXPRESSION_LENGTH = 160
MAX_POWER = 12

_BINARY_OPERATORS: dict[type[ast.operator], Callable[[Decimal, Decimal], Decimal]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_UNARY_OPERATORS: dict[type[ast.unaryop], Callable[[Decimal], Decimal]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

_ALLOWED_EXPR_CHARS = re.compile(r"^[0-9+\-*/().% \t]+$")
_EXPR_CANDIDATE = re.compile(r"[0-9][0-9+\-*/().% \t]*")
_HAS_OPERATOR = re.compile(r"[+\-*/%]")


class CalculatorError(ValueError):
    """Raised when an expression cannot be safely calculated."""


def extract_expression(text: str) -> str:
    """Extract a simple arithmetic expression from user text."""
    cleaned = " ".join(str(text or "").strip().split())
    if not cleaned:
        raise CalculatorError("Enter an arithmetic expression.")

    if len(cleaned) > MAX_EXPRESSION_LENGTH:
        raise CalculatorError(f"Expression is too long. Limit is {MAX_EXPRESSION_LENGTH} characters.")

    if _ALLOWED_EXPR_CHARS.fullmatch(cleaned) and _HAS_OPERATOR.search(cleaned):
        return cleaned

    candidates = [match.group(0).strip() for match in _EXPR_CANDIDATE.finditer(cleaned)]
    candidates = [candidate for candidate in candidates if _HAS_OPERATOR.search(candidate)]
    if not candidates:
        raise CalculatorError("I could not find a supported arithmetic expression.")

    expression = max(candidates, key=len)
    if len(expression) > MAX_EXPRESSION_LENGTH:
        raise CalculatorError(f"Expression is too long. Limit is {MAX_EXPRESSION_LENGTH} characters.")
    return expression


def calculate_expression(expression: str) -> str:
    """Safely evaluate arithmetic with +, -, *, /, //, %, **, and parentheses."""
    normalized = extract_expression(expression)
    try:
        parsed = ast.parse(normalized, mode="eval")
        result = _eval_node(parsed.body)
    except CalculatorError:
        raise
    except (SyntaxError, DivisionByZero, InvalidOperation, ZeroDivisionError) as exc:
        raise CalculatorError(f"Invalid calculation: {exc}") from exc
    except Exception as exc:
        raise CalculatorError(f"Unsupported expression: {exc}") from exc

    return _format_decimal(result)


def _eval_node(node: ast.AST) -> Decimal:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return Decimal(str(node.value))

    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPERATORS:
        return _UNARY_OPERATORS[type(node.op)](_eval_node(node.operand))

    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPERATORS:
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > MAX_POWER:
            raise CalculatorError(f"Exponent is too large. Limit is +/-{MAX_POWER}.")
        return _BINARY_OPERATORS[type(node.op)](left, right)

    raise CalculatorError("Only basic arithmetic expressions are supported.")


def _format_decimal(value: Decimal) -> str:
    if value == value.to_integral_value():
        return str(value.quantize(Decimal(1)))
    return format(value.normalize(), "f")

