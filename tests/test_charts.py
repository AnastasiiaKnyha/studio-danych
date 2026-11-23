import pandas as pd
import pytest

from studio import charts
from studio.columns import category_columns, numeric_columns
from studio.errors import DataError


def small_frame() -> pd.DataFrame:
    # small data with a number, a category, a constant and a true or false column
    return pd.DataFrame({
        "wiek": [34, 28, 45, 51, 29, 42],
        "dochod": [5200, 6100, 7300, 4800, 5100, 5900],
        "kategoria": ["A", "B", "A", "C", "C", "B"],
        "stala": [1, 1, 1, 1, 1, 1],
        "odstajacy": [False, False, True, False, False, False],
    })


def test_histogram_has_title_and_axis_labels():
    fig = charts.histogram_figure(small_frame(), "wiek")
    ax = fig.axes[0]
    assert ax.get_title() == "Rozkład: wiek"
    assert ax.get_xlabel() == "wiek"
    assert ax.get_ylabel() == "Liczba rekordów"


def test_histogram_of_text_column_is_blocked():
    with pytest.raises(DataError, match="nie jest liczbowa"):
        charts.histogram_figure(small_frame(), "kategoria")


def test_constant_column_is_blocked():
    with pytest.raises(DataError, match="tylko jedną wartość"):
        charts.histogram_figure(small_frame(), "stala")


def test_true_false_column_is_not_a_number():
    with pytest.raises(DataError, match="nie jest liczbowa"):
        charts.histogram_figure(small_frame(), "odstajacy")


def test_scatter_shows_correlation_in_title():
    fig = charts.scatter_figure(small_frame(), "wiek", "dochod")
    assert "r = " in fig.axes[0].get_title()


def test_scatter_needs_two_different_columns():
    with pytest.raises(DataError, match="dwóch różnych kolumn"):
        charts.scatter_figure(small_frame(), "wiek", "wiek")


def test_bar_of_column_with_many_values_is_blocked():
    frame = pd.DataFrame({"x": range(30)})
    with pytest.raises(DataError, match="różnych wartości"):
        charts.bar_figure(frame, "x")


def test_box_with_groups():
    fig = charts.box_figure(small_frame(), "dochod", "kategoria")
    assert fig.axes[0].get_xlabel() == "kategoria"


def test_build_figure_chooses_the_right_chart():
    fig = charts.build_figure(small_frame(), "bar", "kategoria")
    assert fig.axes[0].get_title() == "Liczba rekordów w kategoriach: kategoria"


def test_build_figure_unknown_kind():
    with pytest.raises(DataError, match="Nieznany rodzaj wykresu"):
        charts.build_figure(small_frame(), "pie", "wiek")


def test_scatter_without_second_column():
    with pytest.raises(DataError, match="dwóch kolumn"):
        charts.build_figure(small_frame(), "scatter", "wiek")


def test_correlation_needs_two_numeric_columns():
    frame = pd.DataFrame({"x": [1, 2, 3], "tekst": ["a", "b", "c"]})
    with pytest.raises(DataError, match="co najmniej dwie kolumny liczbowe"):
        charts.correlation_figure(frame)


def test_strongest_correlations():
    frame = pd.DataFrame({"x": [1, 2, 3, 4], "y": [2, 4, 6, 8], "z": [4, 1, 3, 2]})
    table = charts.strongest_correlations(frame, count=1)
    assert table.loc[0, "kolumna_1"] == "x"
    assert table.loc[0, "kolumna_2"] == "y"
    assert table.loc[0, "r"] == 1.0


def test_column_lists_for_charts():
    frame = small_frame()
    assert numeric_columns(frame) == ["wiek", "dochod"]
    assert "kategoria" in category_columns(frame)
    assert "stala" not in category_columns(frame)


def test_save_png_and_svg(tmp_path):
    fig = charts.histogram_figure(small_frame(), "wiek")
    charts.save_figure(fig, tmp_path / "wykres.png")
    charts.save_figure(fig, tmp_path / "wykres.svg")
    assert (tmp_path / "wykres.png").stat().st_size > 0
    assert (tmp_path / "wykres.svg").stat().st_size > 0


def test_save_in_wrong_format_is_refused(tmp_path):
    fig = charts.histogram_figure(small_frame(), "wiek")
    with pytest.raises(DataError, match="Nieobsługiwany format"):
        charts.save_figure(fig, tmp_path / "wykres.jpg")