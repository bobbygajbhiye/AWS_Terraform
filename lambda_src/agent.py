from __future__ import annotations

from typing import TypedDict

from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph

try:
    from .calculator_core import CalculatorError, calculate_expression, extract_expression
except ImportError:  # Lambda zip places modules at the package root.
    from calculator_core import CalculatorError, calculate_expression, extract_expression


class CalculatorState(TypedDict, total=False):
    question: str
    expression: str
    result: str
    answer: str
    error: str


@tool("calculator", description="Evaluate a basic arithmetic expression.")
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression."""
    return calculate_expression(expression)


def _plan(state: CalculatorState) -> CalculatorState:
    question = state.get("question", "")
    return {"expression": extract_expression(question)}


def _calculate(state: CalculatorState) -> CalculatorState:
    result = calculator.invoke({"expression": state["expression"]})
    return {"result": str(result)}


def _respond(state: CalculatorState) -> CalculatorState:
    expression = state["expression"]
    result = state["result"]
    return {"answer": f"{expression} = {result}"}


def _build_agent():
    graph = StateGraph(CalculatorState)
    graph.add_node("plan", _plan)
    graph.add_node("calculate", _calculate)
    graph.add_node("respond", _respond)
    graph.add_edge(START, "plan")
    graph.add_edge("plan", "calculate")
    graph.add_edge("calculate", "respond")
    graph.add_edge("respond", END)
    return graph.compile()


agent = _build_agent()


def invoke_calculator_agent(question: str) -> dict[str, str]:
    """Invoke the LangGraph calculator agent and return JSON-safe fields."""
    try:
        state = agent.invoke({"question": question})
    except CalculatorError as exc:
        return {
            "input": question,
            "error": str(exc),
        }

    return {
        "input": question,
        "expression": state["expression"],
        "result": state["result"],
        "answer": state["answer"],
    }

