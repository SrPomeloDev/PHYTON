def format_currency(value: float, symbol: str = "Bs") -> str:
    if abs(value) >= 1_000_000:
        return f"{symbol}{value / 1_000_000:,.2f}M"
    if abs(value) >= 1_000:
        return f"{symbol}{value / 1_000:,.2f}K"
    return f"{symbol}{value:,.2f}"


def format_number(value: float, decimals: int = 0) -> str:
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:,.{decimals}f}M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:,.{decimals}f}K"
    return f"{value:,.{decimals}f}"


def format_percent(value: float, decimals: int = 1) -> str:
    return f"{value * 100:.{decimals}f}%"


def format_date_short(value) -> str:
    from datetime import date as _date_cls
    if isinstance(value, _date_cls):
        return value.strftime("%b %Y")
    return str(value)
