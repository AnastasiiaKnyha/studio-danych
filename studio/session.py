from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import pandas as pd

from studio import cleaning
from studio.loading import load_csv
from studio.rules import out_of_range_mask, outlier_mask


@dataclass
class Operation:
    # one line in the log of changes
    name: str
    params: str
    rows_before: int
    rows_after: int
    changed: int
    time: str


@dataclass
class DataSession:
    raw: pd.DataFrame
    current: pd.DataFrame = field(init=False)
    log: list[Operation] = field(default_factory=list)

    def __post_init__(self) -> None:
        # we work on a copy, so raw data never changes
        self.current = self.raw.copy(deep=True)

    @classmethod
    def from_csv(cls, path: Path) -> "DataSession":
        return cls(load_csv(path))

    def save(self, result: pd.DataFrame, changed: int, name: str, params: str) -> int:
        rows_before = len(self.current)
        self.current = result
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log.append(Operation(name, params, rows_before, len(result), changed, time))
        return changed

    # checks only count records and never change data

    def count_out_of_range(self, column: str, minimum: float | None, maximum: float | None) -> int:
        return int(out_of_range_mask(self.current, column, minimum, maximum).sum())

    def count_outliers(self, column: str, factor: float = 1.5) -> int:
        return int(outlier_mask(self.current, column, factor).sum())

    # operations change current data and write a line to the log

    def remove_duplicates(self) -> int:
        result, changed = cleaning.drop_duplicates(self.current)
        return self.save(result, changed, "Usunięcie pełnych duplikatów", "wszystkie kolumny")

    def remove_missing(self, column: str) -> int:
        result, changed = cleaning.drop_missing(self.current, column)
        return self.save(result, changed, "Usunięcie rekordów z brakami", f"kolumna={column}")

    def fill_missing(self, column: str, strategy: str) -> int:
        result, changed = cleaning.fill_missing(self.current, column, strategy)
        return self.save(result, changed, "Uzupełnienie braków", f"kolumna={column}, strategia={strategy}")

    def convert_to_numbers(self, column: str) -> int:
        result, changed = cleaning.convert_to_numbers(self.current, column)
        return self.save(result, changed, "Zamiana tekstu na liczby", f"kolumna={column}")

    def range_to_missing(self, column: str, minimum: float | None, maximum: float | None) -> int:
        result, changed = cleaning.range_to_missing(self.current, column, minimum, maximum)
        return self.save(result, changed, "Wartości spoza zakresu na braki", f"kolumna={column}, zakres=[{minimum}, {maximum}]")

    def remove_out_of_range(self, column: str, minimum: float | None, maximum: float | None) -> int:
        result, changed = cleaning.drop_out_of_range(self.current, column, minimum, maximum)
        return self.save(result, changed, "Usunięcie rekordów spoza zakresu", f"kolumna={column}, zakres=[{minimum}, {maximum}]")

    def flag_outliers(self, column: str, factor: float = 1.5) -> int:
        result, changed = cleaning.flag_outliers(self.current, column, factor)
        return self.save(result, changed, "Oznaczenie wartości odstających (IQR)", f"kolumna={column}, k={factor}")

    def clip_outliers(self, column: str, factor: float = 1.5) -> int:
        result, changed = cleaning.clip_outliers(self.current, column, factor)
        return self.save(result, changed, "Przycięcie wartości odstających (IQR)", f"kolumna={column}, k={factor}")

    def reset(self) -> None:
        rows_before = len(self.current)
        self.current = self.raw.copy(deep=True)
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log.append(Operation("Powrót do danych surowych", "-", rows_before, len(self.current), 0, time))

    def log_table(self) -> pd.DataFrame:
        rows = []
        for op in self.log:
            rows.append({
                "czas": op.time,
                "operacja": op.name,
                "parametry": op.params,
                "rekordy_przed": op.rows_before,
                "rekordy_po": op.rows_after,
                "zmienione_rekordy": op.changed,
            })
        return pd.DataFrame(rows)