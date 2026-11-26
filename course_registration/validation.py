"""Функции проверки введённых данных формы регистрации."""

from typing import Sequence

from .models import COURSES, MAX_AGE, MIN_AGE, STUDY_FORMATS


class ValidationError(ValueError):
    """Исключение, возникающее при некорректных данных формы."""


def parse_and_validate_age(age_raw: str) -> int:
    """Преобразует строку возраста в целое число и проверяет допустимый диапазон."""
    cleaned = age_raw.strip()
    if not cleaned:
        raise ValidationError("Поле «Возраст» обязательно для заполнения.")

    try:
        age = int(cleaned)
    except ValueError as exc:
        raise ValidationError("Возраст должен быть целым числом.") from exc

    if age < MIN_AGE or age > MAX_AGE:
        raise ValidationError(
            f"Возраст должен находиться в диапазоне от {MIN_AGE} до {MAX_AGE} лет."
        )

    return age


def validate_phone(phone_raw: str) -> str:
    """Проверяет, что номер телефона состоит только из цифр и символа '+'."""
    phone = phone_raw.strip()
    if not phone:
        raise ValidationError("Поле «Номер телефона» обязательно для заполнения.")

    allowed_chars = set("0123456789+")
    if any(ch not in allowed_chars for ch in phone):
        raise ValidationError(
            "Номер телефона должен содержать только цифры и символ «+»."
        )

    if phone.count("+") > 1 or ("+" in phone and not phone.startswith("+")):
        raise ValidationError(
            "Символ «+» в номере телефона может указываться только в начале."
        )

    digits_only = phone.lstrip("+")
    if not digits_only:
        raise ValidationError(
            "Номер телефона должен содержать цифры."
        )

    return phone


def validate_email(email_raw: str) -> str:
    """Проверяет наличие символов '@' и '.' в адресе электронной почты."""
    email = email_raw.strip()
    if not email:
        raise ValidationError(
            "Поле «Адрес электронной почты» обязательно для заполнения."
        )

    if " " in email or "@" not in email or "." not in email:
        raise ValidationError(
            "Адрес электронной почты должен содержать символы «@» и «.» без пробелов."
        )

    local_part, separator, domain_part = email.partition("@")
    if (
        not separator
        or not local_part
        or not domain_part
        or "@" in domain_part
        or "." not in domain_part
        or domain_part.startswith(".")
        or domain_part.endswith(".")
    ):
        raise ValidationError(
            "Введите корректный адрес электронной почты (например, student@example.com)."
        )

    return email


def validate_registration_data(
    full_name: str,
    age_raw: str,
    phone_raw: str,
    email_raw: str,
    institution: str,
    course: str,
    study_format: str,
    additional_options: Sequence[str],
) -> dict:
    """Выполняет полную проверку всех полей формы регистрации."""
    cleaned_name = full_name.strip()
    cleaned_institution = institution.strip()
    cleaned_course = course.strip()
    cleaned_format = study_format.strip()

    required_text_fields = (
        ("Ф. И. О.", cleaned_name),
        ("Возраст", age_raw.strip()),
        ("Номер телефона", phone_raw.strip()),
        ("Адрес электронной почты", email_raw.strip()),
        ("Учебное заведение", cleaned_institution),
    )
    missing_fields = [label for label, value in required_text_fields if not value]
    if missing_fields:
        joined = ", ".join(missing_fields)
        raise ValidationError(
            f"Заполните все обязательные поля: {joined}."
        )

    age = parse_and_validate_age(age_raw)
    phone = validate_phone(phone_raw)
    email = validate_email(email_raw)

    if not cleaned_course or cleaned_course not in COURSES:
        raise ValidationError("Выберите учебный курс из списка.")

    if not cleaned_format or cleaned_format not in STUDY_FORMATS:
        raise ValidationError("Выберите форму обучения.")

    return {
        "full_name": cleaned_name,
        "age": age,
        "phone": phone,
        "email": email,
        "institution": cleaned_institution,
        "course": cleaned_course,
        "study_format": cleaned_format,
        "additional_options": list(additional_options),
    }
