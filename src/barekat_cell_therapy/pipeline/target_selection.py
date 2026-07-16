"""انتخاب آنتی‌ژن هدف بر اساس بیان توموری."""

from barekat_cell_therapy.core.config import get_settings


def select_best_target(antigen_expression: dict[str, float]) -> str | None:
    """بازگرداندن آنتی‌ژن با بالاترین بیان بالای آستانه حداقل."""
    settings = get_settings()
    if not antigen_expression:
        return None
    filtered = {
        k: v
        for k, v in antigen_expression.items()
        if v >= settings.min_antigen_expression and k in settings.target_antigens
    }
    if not filtered:
        filtered = {k: v for k, v in antigen_expression.items() if k in settings.target_antigens}
    if not filtered:
        return max(antigen_expression, key=antigen_expression.get)
    return max(filtered, key=filtered.get)
