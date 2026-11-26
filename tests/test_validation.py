"""Модульные тесты проверки введённых данных формы регистрации."""

import unittest

from course_registration.models import COURSES, STUDY_FORMATS
from course_registration.validation import (
    ValidationError,
    parse_and_validate_age,
    validate_email,
    validate_phone,
    validate_registration_data,
)


class TestValidation(unittest.TestCase):
    """Тесты функций валидации данных студента."""

    def test_valid_registration_data(self) -> None:
        result = validate_registration_data(
            full_name="  Иванов Иван Иванович  ",
            age_raw=" 20 ",
            phone_raw=" +77001234567 ",
            email_raw=" ivanov@example.com ",
            institution=" КазНУ ",
            course=COURSES[0],
            study_format=STUDY_FORMATS[0],
            additional_options=["Получение сертификата", "Доступ к видеозаписям"],
        )
        self.assertEqual(result["full_name"], "Иванов Иван Иванович")
        self.assertEqual(result["age"], 20)
        self.assertEqual(result["phone"], "+77001234567")
        self.assertEqual(result["email"], "ivanov@example.com")
        self.assertEqual(result["institution"], "КазНУ")
        self.assertEqual(result["course"], "Основы Python")
        self.assertEqual(result["study_format"], "Очное обучение")
        self.assertEqual(
            result["additional_options"],
            ["Получение сертификата", "Доступ к видеозаписям"],
        )

    def test_missing_required_fields_raises(self) -> None:
        with self.assertRaises(ValidationError):
            validate_registration_data(
                full_name="   ",
                age_raw="19",
                phone_raw="+77001112233",
                email_raw="user@mail.ru",
                institution="Школа №1",
                course=COURSES[0],
                study_format=STUDY_FORMATS[0],
                additional_options=[],
            )

    def test_age_boundaries_and_non_integer(self) -> None:
        self.assertEqual(parse_and_validate_age("14"), 14)
        self.assertEqual(parse_and_validate_age("80"), 80)

        for invalid_age in ("", "13", "81", "18.5", "двадцать", "-5"):
            with self.subTest(age=invalid_age):
                with self.assertRaises(ValidationError):
                    parse_and_validate_age(invalid_age)

    def test_phone_validation(self) -> None:
        self.assertEqual(validate_phone("+77015556677"), "+77015556677")
        self.assertEqual(validate_phone("87015556677"), "87015556677")

        for invalid_phone in ("", "+", "+7-701-555-66-77", "8 (701) 555", "abc123", "7+123"):
            with self.subTest(phone=invalid_phone):
                with self.assertRaises(ValidationError):
                    validate_phone(invalid_phone)

    def test_email_validation(self) -> None:
        self.assertEqual(validate_email("student@mail.ru"), "student@mail.ru")
        self.assertEqual(validate_email("a.b@sub.domain.kz"), "a.b@sub.domain.kz")

        for invalid_email in ("", "studentmail.ru", "student@mailru", "a b@mail.ru", "@.", "a@.ru", "a@b."):
            with self.subTest(email=invalid_email):
                with self.assertRaises(ValidationError):
                    validate_email(invalid_email)

    def test_missing_course_or_format_raises(self) -> None:
        with self.assertRaises(ValidationError):
            validate_registration_data(
                full_name="Петров Пётр",
                age_raw="22",
                phone_raw="+77001234567",
                email_raw="petrov@mail.ru",
                institution="Колледж",
                course="",
                study_format=STUDY_FORMATS[1],
                additional_options=[],
            )

        with self.assertRaises(ValidationError):
            validate_registration_data(
                full_name="Петров Пётр",
                age_raw="22",
                phone_raw="+77001234567",
                email_raw="petrov@mail.ru",
                institution="Колледж",
                course=COURSES[1],
                study_format="",
                additional_options=[],
            )


if __name__ == "__main__":
    unittest.main()
