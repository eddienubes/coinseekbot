from decimal import Decimal


def round_if(n: float | Decimal, scale: int = 3) -> float:
    """
    Round a number to decimal places.
    """

    if n > 10 ** -scale:
        return round(n, scale)

    return n
