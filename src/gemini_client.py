from __future__ import annotations
import os, json
from typing import Dict, Any
from pydantic import BaseModel, Field


try:
    import google.generativeai as genai
except Exception:
    genai = None


DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")


class VizPlan(BaseModel):
    chart_type: str
    encodings: Dict[str, Any]
    vegalite_spec: Dict[str, Any]
    rationale: str = Field(min_length=10)


SYSTEM_PROMPT = (
    "You are an Auto-Visualization Planner. Choose the best chart for the user’s task "
    "from provided valid candidates, improve encodings if needed, and output a Vega-Lite v5 spec plus a brief rationale. "
    "Use only provided column names; respect data types; keep spec minimal; return JSON matching the schema."
)


SCHEMA = {
    "type": "object",
    "properties": {
        "chart_type": {"type": "string"},
        "encodings": {"type": "object"},
        "vegalite_spec": {"type": "object"},
        "rationale": {"type": "string"}
},
    "required": ["chart_type", "encodings", "vegalite_spec", "rationale"]
}




def call_gemini(task: str, profile: Dict[str, Any], candidates: Any) -> VizPlan | None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or genai is None:
        return None
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(DEFAULT_MODEL)
    payload = {"task": task, "profile": profile, "candidates": candidates, "json_schema": SCHEMA}
    resp = model.generate_content(
        [
        {"role": "system", "parts": [SYSTEM_PROMPT]},
        {"role": "user", "parts": [json.dumps(payload)]},
        ],
        generation_config={"response_mime_type": "application/json"}
    )
    return VizPlan.model_validate_json(resp.text)