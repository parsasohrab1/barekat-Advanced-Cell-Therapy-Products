"""روایت بالینی قابل‌فهم برای پزشک."""

from __future__ import annotations


def build_clinical_narrative(
    target_antigen: str,
    car_version: str,
    response_probability: float,
    predicted_response: bool,
    crs_grade: int,
    neurotoxicity_risk: float,
    explanation: dict,
) -> str:
    outcome = "پاسخ‌دهنده محتمل" if predicted_response else "پاسخ‌دهنده غیرمحتمل"
    top = explanation.get("top_features") or []
    drivers = ", ".join(
        f"{f.get('feature')} ({f.get('direction')})" for f in top[:3]
    ) or "داده‌های ناکافی"

    crs_note = {
        0: "خطر CRS ناچیز",
        1: "CRS خفیف محتمل؛ پایش سرپایی کافی است",
        2: "CRS متوسط؛ آمادگی Tocilizumab توصیه می‌شود",
        3: "CRS شدید محتمل؛ بستری ICU را در نظر بگیرید",
        4: "CRS تهدیدکننده حیات؛ پروتکل اورژانس فعال شود",
    }.get(crs_grade, "درجه CRS نامشخص")

    neuro = (
        "خطر سمیت عصبی بالاست؛ ارزیابی نورولوژیک روزانه لازم است."
        if neurotoxicity_risk >= 0.25
        else "خطر سمیت عصبی در محدوده قابل‌قبول است."
    )

    return (
        f"برای هدف {target_antigen} با {car_version}، بیمار به‌عنوان «{outcome}» "
        f"با احتمال پاسخ {response_probability:.0%} پیش‌بینی شده است. "
        f"عوامل اصلی مدل: {drivers}. "
        f"{crs_note}. {neuro}"
    )
