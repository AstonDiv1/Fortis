import secrets
import string


def generate_password(
    length: int = 20,
    use_upper: bool = True,
    use_lower: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
) -> str:
    charset = ""
    mandatory = []

    if use_lower:
        charset += string.ascii_lowercase
        mandatory.append(secrets.choice(string.ascii_lowercase))
    if use_upper:
        charset += string.ascii_uppercase
        mandatory.append(secrets.choice(string.ascii_uppercase))
    if use_digits:
        charset += string.digits
        mandatory.append(secrets.choice(string.digits))
    if use_symbols:
        symbols = "!@#$%^&*()-_=+[]{}|;:,.<>?"
        charset += symbols
        mandatory.append(secrets.choice(symbols))

    if not charset:
        charset = string.ascii_letters + string.digits

    remaining = length - len(mandatory)
    password_chars = mandatory + [secrets.choice(charset) for _ in range(remaining)]
    secrets.SystemRandom().shuffle(password_chars)
    return "".join(password_chars)


def password_strength(password: str) -> tuple[int, str]:
    """Returns (score 0-100, label)."""
    score = 0
    if len(password) >= 8:
        score += 15
    if len(password) >= 12:
        score += 15
    if len(password) >= 20:
        score += 10
    if any(c.islower() for c in password):
        score += 10
    if any(c.isupper() for c in password):
        score += 10
    if any(c.isdigit() for c in password):
        score += 15
    if any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?" for c in password):
        score += 25

    if score < 30:
        return score, "Faible"
    elif score < 55:
        return score, "Moyen"
    elif score < 75:
        return score, "Fort"
    else:
        return score, "Très fort"
