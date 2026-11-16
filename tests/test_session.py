from pathlib import Path

import pandas as pd

from studio.session import DataSession

SAMPLES = Path(__file__).parent.parent / "samples"


def test_log_records_rows_before_and_after():
    session = DataSession.from_csv(SAMPLES / "braki.csv")
    session.remove_duplicates()
    entry = session.log[0]
    assert entry.rows_before == 9
    assert entry.rows_after == 8
    assert entry.changed == 1


def test_reset_brings_back_raw_data():
    session = DataSession.from_csv(SAMPLES / "braki.csv")
    session.remove_duplicates()
    session.fill_missing("wiek", "median")
    session.reset()
    pd.testing.assert_frame_equal(session.current, session.raw)
    assert session.log[-1].name == "Powrót do danych surowych"


def test_raw_data_never_changes():
    session = DataSession.from_csv(SAMPLES / "braki.csv")
    before = session.raw.copy()
    session.remove_duplicates()
    session.range_to_missing("wiek", 0, 120)
    pd.testing.assert_frame_equal(session.raw, before)


def test_checks_do_not_change_data():
    session = DataSession.from_csv(SAMPLES / "braki.csv")
    count = session.count_out_of_range("wiek", 0, 120)
    assert count == 1
    pd.testing.assert_frame_equal(session.current, session.raw)
    assert session.log == []


def test_same_steps_give_the_same_result():
    first = DataSession.from_csv(SAMPLES / "braki.csv")
    second = DataSession.from_csv(SAMPLES / "braki.csv")
    for session in (first, second):
        session.remove_duplicates()
        session.fill_missing("wiek", "median")
        session.remove_missing("kategoria")
    pd.testing.assert_frame_equal(first.current, second.current)