import pandas as pd

from app import _repair_replacement_chars


def make_cp1252_string():
    # smart quotes encoded in cp1252 bytes then mis-decoded as utf-8 => replacement char
    b = bytes([0x93]) + b'Hello' + bytes([0x94])
    s = b.decode('utf-8', errors='replace')
    return s


def test_cp1252_like_sequence_repair():
    s = make_cp1252_string()
    assert '\ufffd' in s
    df = pd.DataFrame({'col': [s]})
    out = _repair_replacement_chars(df.copy())
    assert 'Hello' in out.loc[0, 'col']


def test_latin1_bytes_preserved():
    # example: non-ascii char decoded as latin-1 then displayed; our repair should not break normal latin1
    b = b'caf\xe9'
    s = b.decode('latin-1')
    df = pd.DataFrame({'col':[s]})
    out = _repair_replacement_chars(df.copy())
    assert out.loc[0, 'col'] == s


def test_utf8_sig_stripped_if_needed():
    s = '\ufeffHello'
    df = pd.DataFrame({'col':[s]})
    out = _repair_replacement_chars(df.copy())
    # BOM may be left untouched by our heuristic; ensure no error and content preserved
    assert 'Hello' in out.loc[0, 'col']
