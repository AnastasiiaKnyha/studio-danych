import sys
from pathlib import Path

from studio.charts import build_figure, compare_histograms, correlation_figure, save_figure, strongest_correlations
from studio.errors import DataError
from studio.loading import load_csv

BEFORE = Path("dane/housing.csv")
AFTER = Path("wyniki/cleaned.csv")
OUTPUT_DIR = Path("wyniki/wykresy")


def main() -> None:
    try:
        before = load_csv(BEFORE)
        after = load_csv(AFTER)
    except DataError as error:
        print(f"Błąd: {error}")
        print("Najpierw uruchom python3 run_lab6.py, żeby powstał plik wyniki/cleaned.csv.")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # file name and chart, data before and after cleaning
    charts = {
        "1_histogram_total_bedrooms_przed_po": compare_histograms(before, after, "total_bedrooms"),
        "2_histogram_median_income": build_figure(after, "histogram", "median_income"),
        "3_punktowy_dochod_wartosc": build_figure(after, "scatter", "median_income", "median_house_value"),
        "4_pudelkowy_wartosc_ocean": build_figure(after, "box", "median_house_value", "ocean_proximity"),
        "5_slupkowy_ocean_proximity": build_figure(after, "bar", "ocean_proximity"),
        "6_slupkowy_odstajacy_dochod": build_figure(after, "bar", "median_income_outlier"),
        "7_korelacja": correlation_figure(after),
    }

    for name, fig in charts.items():
        save_figure(fig, OUTPUT_DIR / f"{name}.png")
        print(f"Zapisano: {OUTPUT_DIR / name}.png")

    # one chart also in a vector format
    save_figure(charts["7_korelacja"], OUTPUT_DIR / "7_korelacja.svg")
    print(f"Zapisano: {OUTPUT_DIR / '7_korelacja.svg'}")

    print()
    print("Najsilniejsze korelacje po czyszczeniu:")
    print(strongest_correlations(after).to_string(index=False))

    # wrong column types are blocked with a message
    print()
    print("Przykłady zablokowanych wykresów:")
    for kind, column in [("histogram", "ocean_proximity"), ("bar", "median_house_value")]:
        try:
            build_figure(after, kind, column)
        except DataError as error:
            print(f"{kind} dla {column}: {error}")


if __name__ == "__main__":
    main()