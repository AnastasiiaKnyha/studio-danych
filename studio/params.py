from studio.errors import DataError


def parse_number(text: str, name: str) -> float | None:
    # empty field means no limit on that side
    text = text.strip().replace(",", ".")
    if text == "":
        return None
    try:
        return float(text)
    except ValueError:
        raise DataError(f"Pole \"{name}\" musi być liczbą, na przykład 0 albo 120. Teraz jest w nim \"{text}\".")


def parse_factor(text: str) -> float:
    value = parse_number(text, "k")
    if value is None or value <= 0:
        raise DataError("Współczynnik k musi być liczbą większą od zera. Zwykle używa się 1.5.")
    return value