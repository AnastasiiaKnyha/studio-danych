import pandas as pd
import pytest

from studio import cleaning
from studio.errors import DataError


def small_frame() -> pd.DataFrame:
    # small data where every problem is known
    return pd.DataFrame({
        "miasto": ["Opole", "Wrocław", "Kraków", "Łódź", "Lublin", "Lublin"],
        "wiek": [34, None, 45, 150, 29, 29],
        "dochod": [5200, 6100, 7300, 4800, 5100, 5100],
        "kategoria": ["A", "B", None, "C", "C", "C"],
    })


def test_only_full_duplicates_are_removed():
    frame = small_frame()
    # same city but different income is not a duplicate
    frame.loc[6] = ["Opole", 34, 9999, "A"]
    result, changed = cleaning.drop_duplicates(frame)
    assert changed == 1
    assert len(result) == 6


def test_fill_missing_with_median_changes_only_that_column():
    frame = small_frame()
    result, changed = cleaning.fill_missing(frame, "wiek", "median")
    assert changed == 1
    assert result.loc[1, "wiek"] == 34
    # other columns are the same as before
    pd.testing.assert_frame_equal(result.drop(columns="wiek"), frame.drop(columns="wiek"))


def test_fill_text_with_mode():
    result, changed = cleaning.fill_missing(small_frame(), "kategoria", "mode")
    assert changed == 1
    assert result.loc[2, "kategoria"] == "C"


def test_median_on_text_column_is_refused():
    with pytest.raises(DataError, match="tylko dla kolumn liczbowych"):
        cleaning.fill_missing(small_frame(), "kategoria", "median")


def test_drop_missing_removes_records():
    result, changed = cleaning.drop_missing(small_frame(), "kategoria")
    assert changed == 1
    assert "Kraków" not in result["miasto"].values


def test_range_rule_turns_bad_value_into_missing():
    frame = small_frame()
    result, changed = cleaning.range_to_missing(frame, "wiek", 0, 120)
    assert changed == 1
    assert pd.isna(result.loc[3, "wiek"])
    pd.testing.assert_frame_equal(result.drop(columns="wiek"), frame.drop(columns="wiek"))


def test_wrong_range_is_refused():
    with pytest.raises(DataError, match="większa niż górna"):
        cleaning.range_to_missing(small_frame(), "wiek", 100, 10)


def test_flag_outliers_adds_column_and_keeps_values():
    frame = pd.DataFrame({"x": [10, 11, 12, 13, 14, 100]})
    result, changed = cleaning.flag_outliers(frame, "x")
    assert changed == 1
    assert result["x_outlier"].tolist() == [False, False, False, False, False, True]
    assert result["x"].tolist() == frame["x"].tolist()


def test_constant_column_has_no_outliers():
    frame = pd.DataFrame({"x": [5, 5, 5, 5]})
    result, changed = cleaning.flag_outliers(frame, "x")
    assert changed == 0


def test_original_frame_is_not_changed():
    frame = small_frame()
    copy = frame.copy()
    cleaning.fill_missing(frame, "wiek", "median")
    cleaning.range_to_missing(frame, "wiek", 0, 120)
    cleaning.drop_duplicates(frame)
    pd.testing.assert_frame_equal(frame, copy)


def test_text_in_number_column_becomes_missing():
    frame = pd.DataFrame({"x": ["10", "abc", "12", None]})
    result, changed = cleaning.convert_to_numbers(frame, "x")
    assert changed == 1
    assert result["x"].tolist()[0] == 10
    assert pd.isna(result.loc[1, "x"])