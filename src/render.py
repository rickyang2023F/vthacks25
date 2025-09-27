from __future__ import annotations
import altair as alt
from typing import Dict, Any

def render_vegalite(spec: Dict[str, Any]):
    return alt.Chart.from_dict(spec)