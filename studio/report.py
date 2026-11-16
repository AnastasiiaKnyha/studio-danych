from datetime import datetime
from pathlib import Path

import pandas as pd

from studio.profile import basic_info, column_profile, numeric_stats
from studio.rules import iqr_bounds, out_of_range_mask, outlier_mask
from studio.session import DataSession

# a rule is a tuple: (column, minimum, maximum)
Rule = tuple[str, float | None, float | None]


def info_lines(frame: pd.DataFrame) -> list[str]:
    info = basic_info(frame)
    return [
        f"Rekordy: {info['rekordy']}",
        f"Kolumny: {info['kolumny']}",
        f"Pełne duplikaty: {info['pelne_duplikaty']}",
    ]


def rules_table(frame: pd.DataFrame, rules: list[Rule]) -> pd.DataFrame:
    rows = []
    for column, minimum, maximum in rules:
        count = int(out_of_range_mask(frame, column, minimum, maximum).sum())
        # dash means no limit on that side
        rows.append({
            "kolumna": column,
            "min": "-" if minimum is None else minimum,
            "max": "-" if maximum is None else maximum,
            "rekordy_poza_zakresem": count,
        })
    return pd.DataFrame(rows)


def outliers_table(frame: pd.DataFrame, columns: list[str], factor: float) -> pd.DataFrame:
    rows = []
    for column in columns:
        low, high = iqr_bounds(frame, column, factor)
        count = int(outlier_mask(frame, column, factor).sum())
        rows.append({"kolumna": column, "dolna_granica": round(low, 2), "gorna_granica": round(high, 2), "odstajace": count})
    return pd.DataFrame(rows)


def compare_table(before: pd.DataFrame, after: pd.DataFrame) -> pd.DataFrame:
    # only columns that exist in the raw data
    return pd.DataFrame({
        "braki_przed": before.isna().sum(),
        "braki_po": after[before.columns].isna().sum(),
    })


def build_report(session: DataSession, source: Path, rules: list[Rule], outlier_columns: list[str], factor: float) -> str:
    raw = session.raw
    clean = session.current
    lines = []

    lines.append("RAPORT JAKOŚCI DANYCH")
    lines.append(f"Plik: {source}")
    lines.append(f"Utworzono: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    lines.append("1. DANE SUROWE")
    lines.extend(info_lines(raw))
    lines.append("")
    lines.append(column_profile(raw).to_string())
    lines.append("")
    lines.append(numeric_stats(raw).to_string())
    lines.append("")

    lines.append("2. REGUŁY JAKOŚCI NA DANYCH SUROWYCH (tylko wykrycie, bez zmian)")
    lines.append("Zakresy poprawnych wartości:")
    if rules:
        lines.append(rules_table(raw, rules).to_string(index=False))
    else:
        lines.append("Brak reguł zakresu dla kolumn tego pliku.")
    lines.append("")
    lines.append(f"Wartości odstające metodą IQR, k = {factor}:")
    if outlier_columns:
        lines.append(outliers_table(raw, outlier_columns, factor).to_string(index=False))
    else:
        lines.append("Brak kolumn do sprawdzenia wartości odstających.")
    lines.append("")

    lines.append("3. WYKONANE OPERACJE")
    lines.append(session.log_table().to_string(index=False))
    lines.append("")

    lines.append("4. DANE PO CZYSZCZENIU")
    lines.extend(info_lines(clean))
    lines.append("")
    lines.append(column_profile(clean).to_string())
    lines.append("")

    lines.append("5. PORÓWNANIE BRAKÓW PRZED I PO")
    lines.append(compare_table(raw, clean).to_string())
    lines.append("")

    return "\n".join(lines)