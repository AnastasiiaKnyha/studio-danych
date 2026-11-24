from pathlib import Path

import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

from studio.columns import category_columns, category_values, numeric_columns, numeric_values
from studio.errors import DataError

# every function returns a Figure, so the same chart can be saved to a file or shown in the window later
CHART_KINDS = ["histogram", "scatter", "box", "bar"]
SAVE_FORMATS = [".png", ".pdf", ".svg"]
SIZE = (7, 4.5)


def histogram_figure(frame: pd.DataFrame, column: str) -> Figure:
    values = numeric_values(frame, column)
    fig = Figure(figsize=SIZE, dpi=100)
    ax = fig.add_subplot()
    ax.hist(values, bins=30, edgecolor="white")
    ax.set(title=f"Rozkład: {column}", xlabel=column, ylabel="Liczba rekordów")
    fig.tight_layout()
    return fig


def scatter_figure(frame: pd.DataFrame, x: str, y: str) -> Figure:
    numeric_values(frame, x)
    numeric_values(frame, y)
    if x == y:
        raise DataError("Wykres punktowy potrzebuje dwóch różnych kolumn.")

    # only records that have both values
    data = frame[[x, y]].dropna()
    correlation = data[x].corr(data[y])

    fig = Figure(figsize=SIZE, dpi=100)
    ax = fig.add_subplot()
    # small and transparent points, so dense areas are visible
    ax.scatter(data[x], data[y], s=6, alpha=0.3)
    ax.set(title=f"{y} względem {x} (r = {correlation:.2f})", xlabel=x, ylabel=y)
    fig.tight_layout()
    return fig


def box_figure(frame: pd.DataFrame, column: str, group: str | None = None) -> Figure:
    numeric_values(frame, column)
    fig = Figure(figsize=SIZE, dpi=100)
    ax = fig.add_subplot()

    if group is None:
        sns.boxplot(y=frame[column], ax=ax)
        ax.set(title=f"Rozkład i wartości odstające: {column}", ylabel=column)
    else:
        category_values(frame, group)
        sns.boxplot(data=frame, x=group, y=column, ax=ax)
        ax.set(title=f"{column} w grupach {group}", xlabel=group, ylabel=column)
        ax.tick_params(axis="x", labelrotation=20)

    fig.tight_layout()
    return fig


def bar_figure(frame: pd.DataFrame, column: str) -> Figure:
    values = category_values(frame, column)
    # value_counts sorts from the biggest group
    counts = values.value_counts()

    fig = Figure(figsize=SIZE, dpi=100)
    ax = fig.add_subplot()
    bars = ax.bar(counts.index.astype(str), counts.values)
    # number above every bar
    ax.bar_label(bars)
    ax.set(title=f"Liczba rekordów w kategoriach: {column}", xlabel=column, ylabel="Liczba rekordów")
    ax.tick_params(axis="x", labelrotation=20)
    fig.tight_layout()
    return fig


def correlation_figure(frame: pd.DataFrame) -> Figure:
    columns = numeric_columns(frame)
    if len(columns) < 2:
        raise DataError("Do macierzy korelacji potrzebne są co najmniej dwie kolumny liczbowe.")

    correlation = frame[columns].corr()
    fig = Figure(figsize=(9, 7), dpi=100)
    ax = fig.add_subplot()
    sns.heatmap(
        correlation, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, ax=ax,
        cbar_kws={"label": "Współczynnik korelacji Pearsona"},
    )
    ax.set(title="Korelacja między kolumnami liczbowymi")
    fig.tight_layout()
    return fig


def strongest_correlations(frame: pd.DataFrame, count: int = 5) -> pd.DataFrame:
    columns = numeric_columns(frame)
    correlation = frame[columns].corr()
    rows = []
    # every pair only once
    for i in range(len(columns)):
        for j in range(i + 1, len(columns)):
            first = columns[i]
            second = columns[j]
            rows.append({"kolumna_1": first, "kolumna_2": second, "r": round(correlation.loc[first, second], 2)})

    table = pd.DataFrame(rows)
    # the strongest first, no matter if positive or negative
    table = table.reindex(table["r"].abs().sort_values(ascending=False).index)
    return table.head(count).reset_index(drop=True)


def compare_histograms(before: pd.DataFrame, after: pd.DataFrame, column: str) -> Figure:
    before_values = numeric_values(before, column)
    after_values = numeric_values(after, column)
    # the same range on both charts, so they can be compared
    low = min(before_values.min(), after_values.min())
    high = max(before_values.max(), after_values.max())

    fig = Figure(figsize=(10, 4.5), dpi=100)
    left, right = fig.subplots(1, 2, sharey=True)
    left.hist(before_values, bins=30, range=(low, high), edgecolor="white")
    left.set(title=f"Przed czyszczeniem ({len(before_values)} wartości)", xlabel=column, ylabel="Liczba rekordów")
    right.hist(after_values, bins=30, range=(low, high), edgecolor="white")
    right.set(title=f"Po czyszczeniu ({len(after_values)} wartości)", xlabel=column)
    fig.suptitle(f"Rozkład {column} przed i po czyszczeniu")
    fig.tight_layout()
    return fig

def columns_for_chart(frame: pd.DataFrame, kind: str) -> tuple[list[str], list[str]]:
    # lists for the first and the second column of every chart
    numbers = numeric_columns(frame)
    categories = category_columns(frame)
    if kind == "histogram":
        return numbers, []
    if kind == "scatter":
        return numbers, numbers
    if kind == "box":
        return numbers, categories
    if kind == "bar":
        return categories, []
    raise DataError(f"Nieznany rodzaj wykresu \"{kind}\". Wybierz jeden z: {', '.join(CHART_KINDS)}.")


def build_figure(frame: pd.DataFrame, kind: str, x: str, y: str | None = None) -> Figure:
    # one function for every chart, the window will call only this one
    if kind == "histogram":
        return histogram_figure(frame, x)
    if kind == "scatter":
        if y is None:
            raise DataError("Wykres punktowy potrzebuje dwóch kolumn. Wybierz kolumnę dla osi Y.")
        return scatter_figure(frame, x, y)
    if kind == "box":
        # for a box chart the second column is an optional group
        return box_figure(frame, x, y)
    if kind == "bar":
        return bar_figure(frame, x)
    raise DataError(f"Nieznany rodzaj wykresu \"{kind}\". Wybierz jeden z: {', '.join(CHART_KINDS)}.")


def save_figure(fig: Figure, path: Path) -> None:
    if path.suffix.lower() not in SAVE_FORMATS:
        raise DataError(f"Nieobsługiwany format \"{path.suffix}\". Wybierz PNG, PDF albo SVG.")
    fig.savefig(path, dpi=150, bbox_inches="tight")