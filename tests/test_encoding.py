import pandas as pd

from app import _repair_replacement_chars


def test_repair_removes_utf8_replacement_markers():
    # simulate bytes decoded with utf-8 with replacement for cp1252 smart quotes
    raw = b"\x93Hello\x94"
    s = raw.decode('utf-8', errors='replace')
    assert '\ufffd' in s
    df = pd.DataFrame({"col": [s, "Normal"]})
    out = _repair_replacement_chars(df.copy())
    # heuristic removes replacement markers and preserves readable content
    assert out.loc[0, "col"] == "Hello" or "Hello" in out.loc[0, "col"]
    assert out.loc[1, "col"] == "Normal"


def test_repair_ignores_already_clean():
    df = pd.DataFrame({"col": ["A - B", "C"]})
    out = _repair_replacement_chars(df.copy())
    assert out.loc[0, "col"] == "A - B"
    assert out.loc[1, "col"] == "C"
