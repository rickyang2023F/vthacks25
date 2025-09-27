from __future__ import annotations
import pandas as pd
from typing import Dict, Any

def profile_df(df: pd.DataFrame) -> Dict[str, Any]:
    prof = {"n_rows": int(len(df)), "columns": []}
    for c in df.columns:
        s = df[c]
        col = {
        "name": c,
        "dtype": str(s.dtype),
        "is_temporal": pd.api.types.is_datetime64_any_dtype(s),
        "is_numeric": pd.api.types.is_numeric_dtype(s),
        "cardinality": int(s.nunique(dropna=True)),
        "pct_missing": float(s.isna().mean()),
        }
        prof["columns"].append(col)
# try to coerce likely dates
    for col in prof["columns"]:
        if not col["is_temporal"]:
            try:
                pd.to_datetime(df[col["name"]])
                col["coercible_to_datetime"] = True
            except Exception:
                col["coercible_to_datetime"] = False
    return prof