import pytest
import pandas as pd

from app import mid_from_bins, normalize, TOTAL_PARTNERS_MAP, ACTIVE_PARTNERS_MAP

def test_mid_from_bins_basic():
    assert mid_from_bins("Less than 50", TOTAL_PARTNERS_MAP) == 25.0
    assert mid_from_bins("50 - 499", TOTAL_PARTNERS_MAP) == 275.0

def test_mid_from_bins_missing():
    assert mid_from_bins("Unknown Range", TOTAL_PARTNERS_MAP) is None

def test_mid_from_bins_alt_dash():
    # ensure en-dash vs hyphen variants work
    assert mid_from_bins("50 – 499", TOTAL_PARTNERS_MAP) == 275.0

def test_normalize():
    # normalization should strip punctuation and lowercase
    out = normalize("Company Name, Inc.")
    assert "company" in out and "name" in out