from __future__ import annotations
from typing import Dict, Any
import pandas as pd


MAX_CATS = 40

def coerce_temporal(df: pd.DataFrame, enc: Dict[str, Any]) -> None:
    x = enc.get("x")
    if x and x in df.columns:
        try:
            df[x] = pd.to_datetime(df[x])
        except Exception:
            pass




def cap_cardinality(df: pd.DataFrame, field: str) -> tuple[pd.DataFrame, str | None]:
    if field is None or field not in df.columns:
        return df, None
    card = df[field].nunique(dropna=True)
    if card <= MAX_CATS:
        return df, None
    # top-K + Other
    counts = df[field].value_counts().nlargest(MAX_CATS)
    keep = set(counts.index)
    new = df.copy()
    new[field] = new[field].where(new[field].isin(keep), other="Other")
    return new, f"Reduced '{field}' cardinality to top-{MAX_CATS} + Other."




def audit_and_fix(plan: Dict[str, Any], df: pd.DataFrame) -> tuple[Dict[str, Any], list[str]]:
    notices = []
    enc = plan.get("encodings", {})
    # ensure referenced fields exist
    for key in ["x", "y", "color", "facet"]:
        col = enc.get(key)
        if col and col not in df.columns:
            notices.append(f"Removed unknown field '{col}' from {key}.")
            enc[key] = None
    # temporal coercion
    coerce_temporal(df, enc)
    # cardinality cap on category/color/facet
    for key in ["x", "color", "facet"]:
        df, msg = cap_cardinality(df, enc.get(key))
        if msg:
            notices.append(msg)
    plan["encodings"] = enc
    return plan, notices