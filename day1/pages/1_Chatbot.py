"""Chatbot page: chat with an LLM that has live access to the EPL dataset.

The model answers any data question by writing a single pandas expression over
the dataframe `df`. We execute it in a restricted namespace (read-only access to
`df`, no builtins), show the resulting table, then feed the result back to the
model to produce the natural-language answer.

Configuration is read from environment variables (see the project `.env`):
    LLM_CHAT_API_KEY - bearer token for the gateway
    LLM_CHAT_URL     - chat completions endpoint
    LLM_CHAT_MODEL   - model name
"""

import os
import re
import sys
from pathlib import Path

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

# Make the sibling data.py importable when run from the pages/ subdir.
sys.path.append(str(Path(__file__).resolve().parent.parent))
from data import load_data  # noqa: E402

load_dotenv()

LLM_API_KEY = os.getenv("LLM_CHAT_API_KEY")
LLM_BASE_URL = os.getenv("LLM_CHAT_URL", "https://llm.alem.ai/v1/chat/completions")
LLM_MODEL = os.getenv("LLM_CHAT_MODEL", "gemma4")

st.set_page_config(page_title="EPL Chatbot", page_icon="💬", layout="wide")
st.title("💬 Chat with the EPL data")
st.caption(f"Model: `{LLM_MODEL}` · runs pandas over `final_dataset.csv`")

if not LLM_API_KEY:
    st.error(
        "No LLM API key found. Set `LLM_CHAT_API_KEY` in your environment or the "
        "project `.env` file."
    )
    st.stop()

df = load_data()

TEAMS = sorted(set(df["HomeTeam"]) | set(df["AwayTeam"]))

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------
SCHEMA_DESC = f"""A pandas DataFrame `df` with one row per match. Columns:
- Date (datetime): match date
- Season (int): season start year (Aug-Jul)
- HomeTeam, AwayTeam (str): team names
- FTHG, FTAG (int): full-time home / away goals
- FTR (str): 'H' = home win, 'NH' = draw or away win
- TotalGoals (int): FTHG + FTAG
- Result (str): 'Home win' or 'Draw / Away win'
There are also form/streak columns (HTP, ATP, HTGD, ATGD, etc.) — usually not needed.

Team names are exact, e.g.: {', '.join(TEAMS)}.
A team's matches = rows where it is HomeTeam OR AwayTeam.
"""

CODE_SYSTEM_PROMPT = f"""You translate a user's question about an English Premier League
dataset into ONE Python pandas expression that evaluates against `df`.

{SCHEMA_DESC}

Rules:
- Output ONLY the expression, no explanation, no markdown fences, no assignment.
- It must be a single expression that returns a DataFrame, Series, or scalar.
- Use only `df` and pandas. No imports, no file/network access, no loops.
- For "top N games of team X by goals":
  df[(df.HomeTeam=='X')|(df.AwayTeam=='X')].nlargest(N, 'TotalGoals')[['Date','HomeTeam','FTHG','FTAG','AwayTeam']]
- Prefer selecting readable columns (Date, HomeTeam, FTHG, FTAG, AwayTeam) for match listings.
"""

ANSWER_SYSTEM_PROMPT = """You are a helpful assistant for an English Premier League dataset.
You asked a question, ran a pandas query, and got a result. Answer the user's question
in plain language based ONLY on that result. Be concise. The result table is also shown
to the user separately, so summarize rather than repeat every row."""


def call_llm(messages: list[dict]) -> str:
    resp = requests.post(
        LLM_BASE_URL,
        headers={"Authorization": f"Bearer {LLM_API_KEY}"},
        json={"model": LLM_MODEL, "messages": messages},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def clean_code(raw: str) -> str:
    """Strip markdown fences / stray prose the model may add."""
    raw = raw.strip()
    fence = re.search(r"```(?:python)?\s*(.*?)```", raw, re.DOTALL)
    if fence:
        raw = fence.group(1).strip()
    # Keep only the first non-empty line (expression).
    for line in raw.splitlines():
        if line.strip():
            return line.strip()
    return raw


# Patterns that must never appear in generated code (read-only enforcement).
FORBIDDEN = re.compile(
    r"\b(import|exec|eval|open|__|os\.|sys\.|subprocess|to_csv|to_pickle|"
    r"drop|delete|setattr|getattr|globals|locals|input)\b"
)


def run_query(code: str):
    if FORBIDDEN.search(code):
        raise ValueError(f"Query rejected for safety: contains a forbidden token.\n{code}")
    # Restricted namespace: only df and pd, no builtins.
    env = {"__builtins__": {}, "df": df, "pd": pd}
    return eval(code, env)  # noqa: S307 -- sandboxed: no builtins, vetted tokens


def result_to_text(result) -> str:
    if isinstance(result, pd.DataFrame):
        return result.head(50).to_string(index=False)
    if isinstance(result, pd.Series):
        return result.head(50).to_string()
    return str(result)


# ---------------------------------------------------------------------------
# Chat UI
# ---------------------------------------------------------------------------
with st.expander("Dataset schema (what the model knows)"):
    st.text(SCHEMA_DESC)

if "messages" not in st.session_state:
    st.session_state.messages = []  # list of {role, content, table?, code?}

if st.sidebar.button("Clear chat"):
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("code"):
            with st.expander("pandas query"):
                st.code(msg["code"], language="python")
        if msg.get("table") is not None:
            st.dataframe(msg["table"], use_container_width=True, hide_index=True)


def answer_question(question: str) -> dict:
    """Two-step: generate pandas code, run it, then narrate the result."""
    code_raw = call_llm(
        [
            {"role": "system", "content": CODE_SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ]
    )
    code = clean_code(code_raw)

    try:
        result = run_query(code)
    except Exception as exc:  # noqa: BLE001
        return {
            "role": "assistant",
            "content": f"⚠️ Could not run a query for that. ({exc})",
            "code": code,
        }

    result_text = result_to_text(result)
    narration = call_llm(
        [
            {"role": "system", "content": ANSWER_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Question: {question}\n\n"
                    f"pandas query: {code}\n\n"
                    f"Result:\n{result_text}"
                ),
            },
        ]
    )

    table = result if isinstance(result, (pd.DataFrame, pd.Series)) else None
    if isinstance(table, pd.Series):
        table = table.reset_index()
    return {"role": "assistant", "content": narration, "code": code, "table": table}


if prompt := st.chat_input("e.g. top 5 Man United games by goals"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Querying the data..."):
            try:
                reply = answer_question(prompt)
            except Exception as exc:  # noqa: BLE001
                reply = {"role": "assistant", "content": f"⚠️ LLM request failed: {exc}"}
        st.markdown(reply["content"])
        if reply.get("code"):
            with st.expander("pandas query"):
                st.code(reply["code"], language="python")
        if reply.get("table") is not None:
            st.dataframe(reply["table"], use_container_width=True, hide_index=True)

    st.session_state.messages.append(reply)
