"""Load the source data of Wilhelm et al. for the figure notebooks.

Data: one workbook, Wilhelm_SourceData.xlsx (one worksheet per panel), plus per-point parquet and summary CSV files, all deposited on
figshare (https://doi.org/10.6084/m9.figshare.34601982). Files are downloaded once into ./data.

  fetch(name)   -> local path of a deposited file (downloads it if needed)
  table(name)   -> DataFrame of a source-data table, e.g. table('Fig1a'), table('Fig4e_totals'), table('ED_Fig6a_summary')
  readme(fig)   -> README rows of one figure, e.g. readme('ED_Fig8')

Set FIGSHARE_ARTICLE_ID below (or the environment variable of the same name). Before publication the article is private: set
FIGSHARE_TOKEN to a figshare personal token with access to it. SOURCE_DATA_DIR may point to a local copy of the files instead.
"""
import os
import re
from functools import lru_cache
from pathlib import Path

import pandas as pd
import requests

FIGSHARE_ARTICLE_ID = os.environ.get("FIGSHARE_ARTICLE_ID", "34601982")
WORKBOOK = "Wilhelm_SourceData.xlsx"
DATA = Path(__file__).resolve().parent / "data"


@lru_cache(None)
def _figshare_files():
    if not FIGSHARE_ARTICLE_ID or os.environ.get("SOURCE_DATA_DIR"):  # a local copy is used exclusively
        return {}
    tok = os.environ.get("FIGSHARE_TOKEN")
    url = (f"https://api.figshare.com/v2/account/articles/{FIGSHARE_ARTICLE_ID}/files?page_size=1000" if tok else
           f"https://api.figshare.com/v2/articles/{FIGSHARE_ARTICLE_ID}/files?page_size=1000")
    r = requests.get(url, headers={"Authorization": f"token {tok}"} if tok else {}, timeout=60)
    r.raise_for_status()
    return {f["name"]: f["download_url"] for f in r.json()}


@lru_cache(None)
def _local_files():
    root = os.environ.get("SOURCE_DATA_DIR")
    if not root:
        return {}
    return {p.name: p for p in Path(root).rglob("*") if p.is_file() and not any(s.startswith(("_", ".")) for s in p.parts)}


def available(name):
    return (DATA / name).exists() or name in _local_files() or name in _figshare_files()


def fetch(name):
    if name in _local_files():  # a local copy of the deposit takes precedence over the download cache
        return _local_files()[name]
    target = DATA / name
    if target.exists():
        return target
    if name in _figshare_files():
        DATA.mkdir(exist_ok=True)
        tok = os.environ.get("FIGSHARE_TOKEN")
        with requests.get(_figshare_files()[name], headers={"Authorization": f"token {tok}"} if tok else {}, stream=True,
                          timeout=600) as r:
            r.raise_for_status()
            with open(target, "wb") as fh:
                for chunk in r.iter_content(1 << 24):
                    fh.write(chunk)
        return target
    raise FileNotFoundError(f"{name}: set FIGSHARE_ARTICLE_ID (and FIGSHARE_TOKEN while private) or SOURCE_DATA_DIR")


@lru_cache(None)
def _index():
    return pd.read_excel(fetch(WORKBOOK), sheet_name="README", header=2)


def readme(fig=None):
    """README rows of the workbook; fig = 'Fig1' or 'ED_Fig8' selects one figure."""
    r = _index()
    if fig:
        lab = f"Extended Data Fig. {fig[6:]}" if fig.startswith("ED_") else f"Fig. {fig[3:]}"
        r = r[r["Figure"] == lab]
    return r.reset_index(drop=True)


def table(name):
    """One source-data table by its name (worksheet name, or worksheet name + suffix for stacked/summary tables)."""
    csv = f"Wilhelm_SourceData_{name}.csv"
    if available(csv):
        return pd.read_csv(fetch(csv))
    sheet = re.match(r"(?:ED_)?Fig\d+[a-z]", name)[0]
    raw = pd.read_excel(fetch(WORKBOOK), sheet_name=sheet, header=None)
    row = _index().loc[_index()["Worksheet"] == sheet, "Tables in worksheet (top to bottom)"]
    tables = str(row.iloc[0]).split("; ") if len(row) and pd.notna(row.iloc[0]) else [sheet]
    if len(tables) == 1:
        return _frame(raw)
    if name not in tables:
        raise KeyError(f"{name} not in worksheet {sheet}: {tables}")
    blank = raw.isna().all(axis=1)
    starts = [0] + [i + 1 for i in raw.index[blank]]
    ends = list(raw.index[blank]) + [len(raw)]
    block = raw.iloc[starts[tables.index(name)] + 1:ends[tables.index(name)]]  # skip the title row
    return _frame(block)


def _frame(block):
    block = block.loc[:, block.iloc[0].notna()]  # columns of this table (header cell present)
    df = block.iloc[1:].copy()
    df.columns = block.iloc[0].tolist()
    df = df.reset_index(drop=True)
    for c in df.columns:  # restore numeric dtypes lost by header=None
        try:
            df[c] = pd.to_numeric(df[c])
        except (ValueError, TypeError):
            pass
    return df
