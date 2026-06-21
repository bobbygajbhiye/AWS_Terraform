from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import requests
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lambda_src.agent import invoke_calculator_agent

def _call_lambda(api_url: str, question: str) -> dict[str, Any]:
    if not api_url:
        return {"error": "Set the API URL."}

    response = requests.post(api_url, json={"question": question}, timeout=15)
    try:
        payload = response.json()
    except ValueError:
        return {"error": response.text}

    if response.status_code >= 400 and "error" not in payload:
        payload["error"] = f"HTTP {response.status_code}"
    return payload


st.set_page_config(page_title="Calculator Agent", page_icon=":material/calculate:", layout="centered")

st.title("Calculator Agent")

api_url_from_env = os.getenv("LAMBDA_API_URL", "")
backend_options = ["Local LangGraph", "Lambda API"]
default_backend_index = 1 if api_url_from_env else 0

backend = st.segmented_control(
    "Backend",
    backend_options,
    default=backend_options[default_backend_index],
)

api_url = api_url_from_env
if backend == "Lambda API":
    api_url = st.text_input("API URL", value=api_url_from_env, placeholder="https://example.execute-api.us-east-1.amazonaws.com/calculate")

with st.form("calculator_form", clear_on_submit=False):
    question = st.text_input("Expression", value="12 * (7 + 5)")
    submitted = st.form_submit_button("Calculate", type="primary")

if submitted:
    with st.spinner("Calculating"):
        if backend == "Lambda API":
            result = _call_lambda(api_url, question)
        else:
            result = invoke_calculator_agent(question)

    if "error" in result:
        st.error(result["error"])
    else:
        st.metric("Result", result["result"])
        st.code(result["answer"], language="text")


