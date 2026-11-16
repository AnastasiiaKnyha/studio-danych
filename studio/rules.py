import pandas as pd

from studio.errors import DataError


def numeric_column(frame: pd.DataFrame, column: str) -> pd.Series:
    if column not in frame.columns:
        raise DataError(f"Nie ma kolumny \"{column}\". Wybierz kolumnę z listy.")

    # text that is not a number becomes missing
    values = pd.to_numeric(frame[column], errors="coerce")
    if values.notna().sum() == 0:
        raise DataError(f"Kolumna \"{column}\" nie zawiera liczb. Wybierz kolumnę liczbową.")
    return values


def out_of_range_mask(frame: pd.DataFrame, column: str, minimum: float | None, maximum: float | None) -> pd.Series:
    if minimum is None and maximum is None:
        raise DataError("Podaj co najmniej jedną granicę zakresu.")
    if minimum is not None and maximum is not None and minimum > maximum:
        raise DataError(f"Dolna granica ({minimum}) jest większa niż górna ({maximum}). Popraw zakres.")

    values = numeric_column(frame, column)
    # start with all false, missing values are never out of range
    mask = pd.Series(False, index=frame.index)
    if minimum is not None:
        mask = mask | (values < minimum)
    if maximum is not None:
        mask = mask | (values > maximum)
    return mask


def iqr_bounds(frame: pd.DataFrame, column: str, factor: float = 1.5) -> tuple[float, float]:
    if factor <= 0:
        raise DataError("Współczynnik IQR musi być większy od zera.")

    values = numeric_column(frame, column)
    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)
    iqr = q3 - q1
    return q1 - factor * iqr, q3 + factor * iqr


def outlier_mask(frame: pd.DataFrame, column: str, factor: float = 1.5) -> pd.Series:
    low, high = iqr_bounds(frame, column, factor)
    values = numeric_column(frame, column)
    # constant column has iqr 0, so nothing is an outlier
    if low == high:
        return pd.Series(False, index=frame.index)
    return (values < low) | (values > high)