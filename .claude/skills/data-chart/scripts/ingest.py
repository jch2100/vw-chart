#!/usr/bin/env python3
"""Normalize pasted/imported tabular data into a clean data.csv.

Accepts a CSV/TSV file, an .xlsx/.xls file, or text on stdin (paste). Cleans
up empty rows/columns, strips whitespace, and coerces numeric-looking columns
to numbers (handling thousands separators and currency/percent signs), then
writes a tidy data.csv the renderer can consume.

Usage:
    python3 ingest.py --in raw.xlsx --out charts/sales/data.csv [--sheet 0]
    pbpaste | python3 ingest.py --out charts/sales/data.csv         # from stdin
"""
from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

import pandas as pd


def _read(in_path: str | None, sheet) -> pd.DataFrame:
    if in_path:
        suffix = Path(in_path).suffix.lower()
        if suffix in (".xlsx", ".xls"):
            return pd.read_excel(in_path, sheet_name=sheet if sheet is not None else 0)
        if suffix in (".tsv", ".txt"):
            return pd.read_csv(in_path, sep="\t")
        return pd.read_csv(in_path)
    # stdin: sniff tab vs comma.
    text = sys.stdin.read()
    if not text.strip():
        raise SystemExit("[ingest] no input given (provide --in or pipe data on stdin)")
    sep = "\t" if text.count("\t") >= text.count(",") else ","
    return pd.read_csv(io.StringIO(text), sep=sep)


def _coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """Turn numeric-looking object columns into real numbers."""
    for col in df.columns:
        if df[col].dtype == object:
            cleaned = (df[col].astype(str)
                       .str.replace(",", "", regex=False)
                       .str.replace(r"[$€£₩%]", "", regex=True)
                       .str.strip())
            converted = pd.to_numeric(cleaned, errors="coerce")
            # Only adopt the numeric version if (almost) everything converted.
            if converted.notna().mean() >= 0.8:
                df[col] = converted
    return df


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(axis=0, how="all").dropna(axis=1, how="all")
    df.columns = [str(c).strip() for c in df.columns]
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()
    df = _coerce_numeric(df)
    return df.reset_index(drop=True)


def main():
    p = argparse.ArgumentParser(description="Normalize tabular data into data.csv")
    p.add_argument("--in", dest="in_path", help="input .csv/.tsv/.xlsx (omit to read stdin)")
    p.add_argument("--out", required=True, help="output data.csv path")
    p.add_argument("--sheet", default=None, help="xlsx sheet name or index")
    args = p.parse_args()

    sheet = args.sheet
    if sheet is not None and str(sheet).isdigit():
        sheet = int(sheet)

    df = normalize(_read(args.in_path, sheet))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"[ingest] wrote {out}  ({len(df)} rows, {len(df.columns)} cols)")
    print(f"[ingest] columns: {list(df.columns)}")


if __name__ == "__main__":
    main()
