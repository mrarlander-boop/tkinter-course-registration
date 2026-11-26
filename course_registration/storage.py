"""Функции фильтрации и сохранения данных о зарегистрированных студентах."""

import csv
from pathlib import Path
from typing import Iterable, Sequence

from .models import Student


CSV_HEADERS: tuple[str, ...] = (
    "Ф. И. О.",
    "Возраст",
    "Телефон",
    "Электронная почта",
    "Учебное заведение",
    "Курс",
    "Форма обучения",
    "Дополнительные возможности",
)


def filter_students(students: Iterable[Student], query: str) -> list[Student]:
    """Фильтрует список студентов по Ф. И. О. или названию учебного курса."""
    normalized = query.strip().casefold()
    if not normalized:
        return list(students)

    return [
        student
        for student in students
        if normalized in student.full_name.casefold()
        or normalized in student.course.casefold()
    ]


def save_students_to_csv(file_path: str | Path, students: Sequence[Student]) -> None:
    """Сохраняет список студентов в CSV-файл в кодировке UTF-8 с BOM."""
    target = Path(file_path)
    with target.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.writer(csv_file, delimiter=";")
        writer.writerow(CSV_HEADERS)
        for student in students:
            writer.writerow(
                [
                    student.full_name,
                    student.age,
                    student.phone,
                    student.email,
                    student.institution,
                    student.course,
                    student.study_format,
                    student.options_text(),
                ]
            )


def save_students_to_txt(file_path: str | Path, students: Sequence[Student]) -> None:
    """Сохраняет список студентов в читаемый текстовый файл в кодировке UTF-8."""
    target = Path(file_path)
    lines: list[str] = [
        "Список зарегистрированных студентов на учебные курсы",
        "=" * 56,
        "",
    ]

    for index, student in enumerate(students, start=1):
        lines.append(f"Запись №{index}")
        lines.append(f"Ф. И. О.: {student.full_name}")
        lines.append(f"Возраст: {student.age}")
        lines.append(f"Телефон: {student.phone}")
        lines.append(f"Электронная почта: {student.email}")
        lines.append(f"Учебное заведение: {student.institution}")
        lines.append(f"Курс: {student.course}")
        lines.append(f"Форма обучения: {student.study_format}")
        lines.append(f"Дополнительные возможности: {student.options_text()}")
        lines.append("-" * 56)

    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def save_students_to_file(file_path: str | Path, students: Sequence[Student]) -> None:
    """Сохраняет список студентов в CSV- или текстовый файл в зависимости от расширения."""
    target = Path(file_path)
    if target.suffix.lower() == ".txt":
        save_students_to_txt(target, students)
    else:
        save_students_to_csv(target, students)
