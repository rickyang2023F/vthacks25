from __future__ import annotations
import io
import os
import pandas as pd
from typing import Optional


SUPPORTED_EXTS = {".csv", ".tsv", ".txt", ".xlsx", ".xls", ".json", ".parquet", ".xml"}



def _ext(path: str) -> str:
    return os.path.splitext(path.lower())[1]


def load_from_bytes(name: str, data: bytes, sheet: Optional[str] = None) -> pd.DataFrame:
    ext = _ext(name)
    bio = io.BytesIO(data)
    if ext in {".csv", ".tsv", ".txt"}:
        sep = "\t" if ext == ".tsv" else None
        return pd.read_csv(bio, sep=sep)
    if ext in {".xlsx", ".xls"}:
        return pd.read_excel(bio, sheet_name=sheet)
    if ext == ".json":
        try:
            return pd.read_json(bio, orient="records")
        except ValueError:
            bio.seek(0)
            return pd.read_json(bio, lines=True)
    if ext == ".parquet":
        return pd.read_parquet(bio)
    if ext == ".xml":
        bio.seek(0)
        return pd.read_xml(bio)
    raise ValueError(f"Unsupported file type: {ext}")




def load_from_url(url: str, sheet: Optional[str] = None) -> pd.DataFrame:
    import urllib.request
    with urllib.request.urlopen(url) as resp:
        data = resp.read()
        name = url.split("?")[0].split("#")[0]
        return load_from_bytes(name, data, sheet)