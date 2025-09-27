from __future__ import annotations
import os, json
import streamlit as st
import pandas as pd
from dotenv import load_dotenv


from src.io_loader import load_from_bytes, load_from_url, SUPPORTED_EXTS
from src.profiling import profile_df
from src.candidates import propose_candidates
from src.guardrails import audit_and_fix
from src.render import render_vegalite
from src.gemini_client import call_gemini, VizPlan

load_dotenv()

st.set_page_config(page_title="AutoViz with Gemini", layout="wide")
st.title("AutoViz with Gemini")

with st.sidebar:
    st.header("Data Source")
    up = st.file_uploader("Upload file", type=[e.lstrip(".") for e in SUPPORTED_EXTS])
    url = st.text_input("Or enter URL")
    sheet = st.text_input("Excel sheet name (optional)")
    task = st.text_input("Task / question (optional)", "Compare trends over time if present; otherwise show a useful overview.")
    run_btn = st.button("Run AutoViz", type="primary")

@st.cache_data(show_spinner=False)
def _load(name: str, data: bytes, sheet: str|None):
    return load_from_bytes(name, data, sheet)
    
@st.cache_data(show_spinner=False)
def _load_url(url: str, sheet: str|None):
    return load_from_url(url, sheet)

if run_btn:
    df = None
    try:
        if up is not None:
            df = _load(up.name, up.read(), sheet or None)
        elif url:
            df = _load_url(url, sheet or None)
        else:
            st.warning("Please upload a file or enter a URL.")
    except Exception as e:
        st.error(f"Failed to load data: {e}")
    
    if df is not None:
        st.success(f"Loaded data with {len(df)} rows and {len(df.columns)} columns.")
        st.dataframe(df.head(100), use_container_width=True)

        profile = profile_df(df)
        st.subheader("Data Profile")
        st.json(profile)

        candidates = propose_candidates(profile)
        st.subheader("Proposed Chart Candidates")
        st.json(candidates)

        plan = None
        with st.spinner("Calling Gemini to plan visualization..."):
            try:
                vp = call_gemini(task, profile, candidates)
                if vp is not None:
                    plan = vp.model_dump()
            except Exception as e:
                st.info(f"Gemini fallback (reason: {e})")

        if plan is None:
            if not candidates:
                st.error("No viable candidates found.")
                st.stop()
            cand = candidates[0]
            enc = cand["encodings"]
            spec = {
                "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                "mark": cand["chart_type"],
                "encoding": {},
                "data": {"name": "data"},
            }
            if enc.get("x"): spec["encoding"]["x"] = {"field": enc["x"], "type": "temporal" if str(df[enc["x"]].dtype).startswith("datetime64") else "nominal"}
            if enc.get("y"): spec["encoding"]["y"] = {"field": enc["y"], "type": "quantitative"}
            if enc.get("color"): spec["encoding"]["color"] = {"field": enc["color"], "type": "nominal"}
            plan = {
                "chart_type": cand["chart_type"],
                "encodings": enc,
                "vegalite_spec": spec,
                "rationale": "Fallback heuristic: selected first viable candidate based on detected types.",
            }

        plan, notices = audit_and_fix(plan, df)

        spec = plan["vegalite_spec"].copy()
        spec["data"] = {"values": df.to_dict(orient="records")}
        
        st.subheader("Chart ")
        chart = render_vegalite(spec)
        st.altair_chart(chart, use_container_width=True)

        st.subheader("Why this chart?")
        st.write(plan.get("rationale", ""))
        if notices:
            with st.expander("Autofixes and Notices"):
                for n in notices:
                    st.write(f"- {n}")

        st.download_button(
            "Download Vega-Lite Spec",
            data = json.dumps(spec, indent=2),
            filename = "viz.json",
            mime = "application/json"
        )