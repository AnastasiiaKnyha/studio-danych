from dataclasses import dataclass

import pandas as pd

from studio.columns import is_numeric
from studio.errors import DataError
from studio.params import parse_factor, parse_number
from studio.session import DataSession

# operation name and the kind of columns it works on
OPERATIONS = {
    "Usuń pełne duplikaty": "none",
    "Usuń rekordy z brakami": "missing",
    "Uzupełnij braki": "missing",
    "Zamień tekst na liczby": "text",
    "Wartości spoza zakresu na braki": "range",
    "Usuń rekordy spoza zakresu": "range",
    "Oznacz wartości odstające": "outlier",
    "Przytnij wartości odstające": "outlier",
}

FILL_STRATEGIES = ["median", "mean", "mode"]


@dataclass
class Choice:
    # everything the user picked in the window, numbers are still text from the fields
    operation: str
    column: str = ""
    strategy: str = "median"
    minimum: str = ""
    maximum: str = ""
    factor: str = "1.5"


def operation_kind(operation: str) -> str:
    if operation not in OPERATIONS:
        raise DataError("Wybierz operację z listy.")
    return OPERATIONS[operation]


def columns_for_operation(frame: pd.DataFrame, operation: str) -> list[str]:
    kind = operation_kind(operation)
    result = []
    for column in frame.columns:
        values = frame[column]
        if kind == "missing" and values.isna().any():
            result.append(column)
        elif kind == "text" and not pd.api.types.is_numeric_dtype(values):
            result.append(column)
        elif kind in ("range", "outlier") and is_numeric(values):
            result.append(column)
    return result


def check_column_chosen(choice: Choice) -> None:
    if operation_kind(choice.operation) != "none" and choice.column == "":
        raise DataError("Wybierz kolumnę z listy.")


def run_operation(session: DataSession, choice: Choice) -> int:
    check_column_chosen(choice)
    operation = choice.operation
    column = choice.column

    if operation == "Usuń pełne duplikaty":
        return session.remove_duplicates()
    if operation == "Usuń rekordy z brakami":
        return session.remove_missing(column)
    if operation == "Uzupełnij braki":
        return session.fill_missing(column, choice.strategy)
    if operation == "Zamień tekst na liczby":
        return session.convert_to_numbers(column)

    if operation_kind(operation) == "range":
        minimum = parse_number(choice.minimum, "min")
        maximum = parse_number(choice.maximum, "max")
        if operation == "Wartości spoza zakresu na braki":
            return session.range_to_missing(column, minimum, maximum)
        return session.remove_out_of_range(column, minimum, maximum)

    factor = parse_factor(choice.factor)
    if operation == "Oznacz wartości odstające":
        return session.flag_outliers(column, factor)
    return session.clip_outliers(column, factor)


def check_operation(session: DataSession, choice: Choice) -> int:
    # only counts records, data does not change
    check_column_chosen(choice)
    kind = operation_kind(choice.operation)
    if kind == "range":
        minimum = parse_number(choice.minimum, "min")
        maximum = parse_number(choice.maximum, "max")
        return session.count_out_of_range(choice.column, minimum, maximum)
    if kind == "outlier":
        return session.count_outliers(choice.column, parse_factor(choice.factor))
    raise DataError("Sprawdzenie bez zmian działа dla reguł zakresu i wartości odstających.")