import pandas as pd

from app import _repair_replacement_chars


def test_repair_removes_replacement_marker():
    df = pd.DataFrame({"col": ["Hello\ufffdWorld", "Normal"]})
    out = _repair_replacement_chars(df.copy())
    assert out.loc[0, "col"] == "HelloWorld" or "HelloWorld" in out.loc[0, "col"]
    assert out.loc[1, "col"] == "Normal"


def test_repair_leaves_clean_rows():
    df = pd.DataFrame({"col": ["A – B", "C"]})
    out = _repair_replacement_chars(df.copy())
    assert out.loc[0, "col"] in ("A – B", "A - B", "A – B")
    assert out.loc[1, "col"] == "C"
