import sys
from pathlib import Path

import pandas as pd

from studio.errors import DataError
from studio.report import build_report
from studio.session import DataSession

DEFAULT_INPUT = Path("dane/housing.csv")
OUTPUT_DIR = Path("wyniki")

# correct values for california housing: (column, minimum, maximum)
# None means no limit on that side
RANGE_RULES = [
    ("longitude", -125, -114),
    ("latitude", 32, 42),
    ("housing_median_age", 1, 100),
    ("total_rooms", 1, None),
    ("total_bedrooms", 0, None),
    ("population", 1, None),
    ("households", 1, None),
    ("median_income", 0, None),
    ("median_house_value", 0, 500001),
        # rule for the small test file samples/braki.csv
    ("wiek", 0, 120),
]

# outliers in these columns are only marked, not removed
OUTLIER_COLUMNS = ["median_income", "total_rooms", "population", "dochod"]
IQR_FACTOR = 1.5


def run_pipeline(session: DataSession, rules: list, outlier_columns: list) -> None:
    # 1. full duplicates
    session.remove_duplicates()

    # 2. numeric columns saved as text: words that are not numbers become missing
    for column, minimum, maximum in rules:
        if not pd.api.types.is_numeric_dtype(session.current[column]):
            session.convert_to_numbers(column)

    # 3. impossible values become missing, the rest of the record stays
    for column, minimum, maximum in rules:
        session.range_to_missing(column, minimum, maximum)

    # 4. missing values: median for numbers, remove record for text
    for column in session.current.columns:
        if session.current[column].isna().sum() == 0:
            continue
        if pd.api.types.is_numeric_dtype(session.current[column]):
            session.fill_missing(column, "median")
        else:
            session.remove_missing(column)

    # 5. outliers are marked in a new column
    for column in outlier_columns:
        session.flag_outliers(column, IQR_FACTOR)


def main() -> None:
    # optional path to another csv file and another output folder
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else OUTPUT_DIR

    try:
        session = DataSession.from_csv(source)
    except DataError as error:
        print(f"Błąd: {error}")
        sys.exit(1)

    # use only rules for columns that exist in this file
    columns = list(session.raw.columns)
    rules = [rule for rule in RANGE_RULES if rule[0] in columns]
    outlier_columns = [column for column in OUTLIER_COLUMNS if column in columns]

    try:
        run_pipeline(session, rules, outlier_columns)
    except DataError as error:
        print(f"Błąd: {error}")
        sys.exit(1)

    output_dir.mkdir(exist_ok=True)
    cleaned_path = output_dir / "cleaned.csv"
    report_path = output_dir / "raport.txt"

    session.current.to_csv(cleaned_path, index=False)
    report = build_report(session, source, rules, outlier_columns, IQR_FACTOR)
    report_path.write_text(report, encoding="utf-8")

    print(f"Rekordy przed: {len(session.raw)}, po: {len(session.current)}")
    print(f"Zapisano: {cleaned_path}")
    print(f"Zapisano: {report_path}")


if __name__ == "__main__":
    main()