from pathlib import Path

import pytest

from studio.errors import DataError
from studio.loading import load_csv

SAMPLES = Path(__file__).parent.parent / "samples"


def test_comma_and_semicolon_give_the_same_columns():
    comma = load_csv(SAMPLES / "przecinek.csv")
    semicolon = load_csv(SAMPLES / "srednik.csv")
    assert list(comma.columns) == ["miasto", "wiek", "dochod", "kategoria"]
    assert list(semicolon.columns) == list(comma.columns)
    assert comma.shape == semicolon.shape == (4, 4)


def test_bad_line_gives_clear_error():
    with pytest.raises(DataError, match="wadliwy wiersz"):
        load_csv(SAMPLES / "zly_wiersz.csv")


def test_missing_file(tmp_path):
    with pytest.raises(DataError, match="Nie znaleziono pliku"):
        load_csv(tmp_path / "brak.csv")


def test_file_with_only_header(tmp_path):
    path = tmp_path / "naglowek.csv"
    path.write_text("a,b,c\n", encoding="utf-8")
    with pytest.raises(DataError, match="nie zawiera żadnych rekordów"):
        load_csv(path)