def format_number_k_m(n: int) -> str:
    """Format numbers like 1200 to '1.2K' or 52000 to '52K'."""
    if n >= 1_000_000:
        val = n / 1_000_000
        return f"{val:.1f}M".replace(".0M", "M")
    if n >= 1_000:
        val = n / 1_000
        return f"{val:.1f}K".replace(".0K", "K")
    return str(n)

def format_currency(amount: float) -> str:
    """Format amount like 500.0 to 'PKR 500'."""
    if amount == int(amount):
        return f"PKR {int(amount)}"
    return f"PKR {amount:.2f}"
