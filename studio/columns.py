import pandas as pd

from studio.errors import DataError

# more categories than this make a bar or box chart unreadable
MAX_CATEGORIES = 20


def check_column(frame: pd.DataFrame, column: str) -> None:
    if column not in frame.columns:
        raise DataError(f"Nie ma kolumny \"{column}\". Wybierz kolumnę z listy.")


def is_numeric(series: pd.Series) -> bool:
    # true or false columns are categories, not numbers
    return pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_bool_dtype(series)


def numeric_values(frame: pd.DataFrame, column: str) -> pd.Series:
    check_column(frame, column)
    if not is_numeric(frame[column]):
        raise DataError(f"Kolumna \"{column}\" nie jest liczbowa. Ten wykres wymaga kolumny liczbowej.")

    values = frame[column].dropna()
    if values.empty:
        raise DataError(f"Kolumna \"{column}\" nie ma żadnych wartości.")
    if values.nunique() < 2:
        raise DataError(f"Kolumna \"{column}\" ma tylko jedną wartość, więc wykres niczego nie pokaże.")
    return values


def category_values(frame: pd.DataFrame, column: str) -> pd.Series:
    check_column(frame, column)
    values = frame[column].dropna()
    if values.empty:
        raise DataError(f"Kolumna \"{column}\" nie ma żadnych wartości.")

    count = values.nunique()
    if count < 2:
        raise DataError(f"Kolumna \"{column}\" ma tylko jedną kategorię, więc wykres niczego nie pokaże.")
    if count > MAX_CATEGORIES:
        raise DataError(
            f"Kolumna \"{column}\" ma {count} różnych wartości. "
            f"Wybierz kolumnę z najwyżej {MAX_CATEGORIES} kategoriami."
        )
    return values


def numeric_columns(frame: pd.DataFrame) -> list[str]:
    # columns that can be used in histogram, scatter and box charts
    result = []
    for column in frame.columns:
        if is_numeric(frame[column]) and frame[column].nunique() >= 2:
            result.append(column)
    return result


def category_columns(frame: pd.DataFrame) -> list[str]:
    # columns that can be used in bar charts and as groups in box charts
    result = []
    for column in frame.columns:
        if 2 <= frame[column].nunique() <= MAX_CATEGORIES:
            result.append(column)
    return result