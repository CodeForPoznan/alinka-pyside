from datetime import date


def extract_date_of_birth_from_pesel(pesel: str) -> date:
    year_part, month_part, day = int(pesel[0:2]), int(pesel[2:4]), int(pesel[4:6])
    year = 2000 + year_part if month_part > 20 else 1900 + year_part
    month = month_part - 20 if month_part > 20 else month_part
    return date(year, month, day)


def is_valid_pesel(pesel: str) -> bool:
    if len(pesel) != 11 or not pesel.isdigit():
        return False
    weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
    digits = [int(ch) for ch in pesel]
    checksum = (10 - sum(w * d for w, d in zip(weights, digits)) % 10) % 10
    if checksum != digits[-1]:
        return False
    year_part, month_part, day = int(pesel[0:2]), int(pesel[2:4]), int(pesel[4:6])
    if 1 <= month_part <= 12:
        month = month_part
        year = 1900 + year_part
    elif 21 <= month_part <= 32:
        month = month_part - 20
        year = 2000 + year_part
    else:
        return False

    try:
        return bool(date(year, month, day))
    except ValueError:
        return False
