import pandas as pd

from studio.errors import DataError
from studio.rules import iqr_bounds, out_of_range_mask, outlier_mask

# every function gets data and returns new data and the number of changed records
# the data given to a function is never changed


def check_column(frame: pd.DataFrame, column: str) -> None:
    if column not in frame.columns:
        raise DataError(f"Nie ma kolumny \"{column}\". Wybierz kolumnę z listy.")


def drop_duplicates(frame: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    # only rows that are the same in every column
    result = frame.drop_duplicates()
    return result, len(frame) - len(result)


def drop_missing(frame: pd.DataFrame, column: str) -> tuple[pd.DataFrame, int]:
    check_column(frame, column)
    result = frame.dropna(subset=[column])
    return result, len(frame) - len(result)


def fill_missing(frame: pd.DataFrame, column: str, strategy: str) -> tuple[pd.DataFrame, int]:
    check_column(frame, column)
    missing = frame[column].isna()
    count = int(missing.sum())
    if count == 0:
        return frame.copy(), 0

    is_number = pd.api.types.is_numeric_dtype(frame[column])
    if strategy in ("median", "mean") and not is_number:
        raise DataError(f"Strategia \"{strategy}\" działa tylko dla kolumn liczbowych. Dla tekstu wybierz \"mode\".")

    if strategy == "median":
        value = frame[column].median()
    elif strategy == "mean":
        value = frame[column].mean()
    elif strategy == "mode":
        # most frequent value, the first one if there is a tie
        value = frame[column].mode().iloc[0]
    else:
        raise DataError(f"Nieznana strategia \"{strategy}\". Wybierz median, mean albo mode.")

    result = frame.copy()
    result[column] = result[column].fillna(value)
    return result, count


def convert_to_numbers(frame: pd.DataFrame, column: str) -> tuple[pd.DataFrame, int]:
    check_column(frame, column)
    numbers = pd.to_numeric(frame[column], errors="coerce")
    # count text values that are not numbers, they become missing
    changed = int((numbers.isna() & frame[column].notna()).sum())
    result = frame.copy()
    result[column] = numbers
    return result, changed


def range_to_missing(frame: pd.DataFrame, column: str, minimum: float | None, maximum: float | None) -> tuple[pd.DataFrame, int]:
    mask = out_of_range_mask(frame, column, minimum, maximum)
    result = frame.copy()
    # mask puts a missing value where the rule is broken
    result[column] = result[column].mask(mask)
    return result, int(mask.sum())


def drop_out_of_range(frame: pd.DataFrame, column: str, minimum: float | None, maximum: float | None) -> tuple[pd.DataFrame, int]:
    mask = out_of_range_mask(frame, column, minimum, maximum)
    result = frame.loc[~mask].copy()
    return result, int(mask.sum())


def flag_outliers(frame: pd.DataFrame, column: str, factor: float = 1.5) -> tuple[pd.DataFrame, int]:
    mask = outlier_mask(frame, column, factor)
    result = frame.copy()
    # new column with true or false, the original values stay the same
    result[f"{column}_outlier"] = mask
    return result, int(mask.sum())


def clip_outliers(frame: pd.DataFrame, column: str, factor: float = 1.5) -> tuple[pd.DataFrame, int]:
    mask = outlier_mask(frame, column, factor)
    low, high = iqr_bounds(frame, column, factor)
    result = frame.copy()
    # values outside the bounds are moved to the nearest bound
    result[column] = pd.to_numeric(result[column], errors="coerce").clip(low, high)
    return result, int(mask.sum())