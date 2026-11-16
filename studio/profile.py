import pandas as pd


def basic_info(frame: pd.DataFrame) -> dict:
    return {
        "rekordy": len(frame),
        "kolumny": len(frame.columns),
        # duplicated marks every repeated row, the first copy stays unmarked
        "pelne_duplikaty": int(frame.duplicated().sum()),
    }


def column_profile(frame: pd.DataFrame) -> pd.DataFrame:
    # one row for every column of the data
    return pd.DataFrame({
        "typ": frame.dtypes.astype(str),
        "braki": frame.isna().sum(),
        "braki_proc": frame.isna().mean().mul(100).round(2),
        "unikalne": frame.nunique(dropna=True),
    })


def numeric_stats(frame: pd.DataFrame) -> pd.DataFrame:
    numbers = frame.select_dtypes(include="number")
    if numbers.empty:
        return pd.DataFrame()
    # .T turns the table so every column becomes a row
    return numbers.describe().T.round(2)