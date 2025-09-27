from __future__ import annotations
from typing import List, Dict, Any


def propose_candidates(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    cols = profile["columns"]
    numerics = [c["name"] for c in cols if c["is_numeric"]]
    temporals = [c["name"] for c in cols if c["is_temporal"]]
    cats = [c["name"] for c in cols if not c["is_numeric"] and not c["is_temporal"]]


    cands = []
    if temporals and numerics:
        cands.append({
        "chart_type": "line",
        "encodings": {"x": temporals[0], "y": numerics[0], "color": cats[0] if cats else None,
        "aggregate": {"y": "sum"}}
        })
    if numerics and cats:
        cands.append({
        "chart_type": "bar",
        "encodings": {"x": cats[0], "y": numerics[0], "aggregate": {"y": "sum"}}
        })
    if len(numerics) >= 2:
        cands.append({
        "chart_type": "scatter",
        "encodings": {"x": numerics[0], "y": numerics[1], "color": cats[0] if cats else None}
        })
    if not cands and numerics:
        cands.append({"chart_type": "hist", "encodings": {"x": numerics[0]}})
    return cands[:3]