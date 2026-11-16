from pathlib import Path

import pandas as pd

from studio.errors import DataError


def load_csv(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise DataError(f"Nie znaleziono pliku: {path}. Wybierz istniejący plik CSV.")

    try:
        # sep=None lets pandas guess the separator, for example , or ;
        frame = pd.read_csv(path, sep=None, engine="python", encoding="utf-8-sig")
    except UnicodeDecodeError:
        raise DataError("Plik nie jest zapisany w kodowaniu UTF-8. Zapisz go jako UTF-8 i spróbuj ponownie.")
    except pd.errors.EmptyDataError:
        raise DataError("Plik jest pusty. Wybierz plik z danymi.")
    except pd.errors.ParserError as error:
        raise DataError(f"Plik ma wadliwy wiersz i nie da się go wczytać. Szczegóły: {error}")

    if frame.empty:
        raise DataError("Plik ma tylko nagłówek i nie zawiera żadnych rekordów.")

    return frame