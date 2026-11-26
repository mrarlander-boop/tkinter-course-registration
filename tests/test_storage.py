"""Модульные тесты фильтрации и сохранения данных о студентах."""

import csv
from pathlib import Path
import tempfile
import unittest

from course_registration.models import Student
from course_registration.storage import (
    CSV_HEADERS,
    filter_students,
    save_students_to_file,
)


class TestStorageAndFilter(unittest.TestCase):
    """Тесты поиска и экспорта зарегистрированных студентов."""

    def setUp(self) -> None:
        self.students = [
            Student(
                record_id=1,
                full_name="Иванов Алексей Сергеевич",
                age=19,
                phone="+77001112233",
                email="ivanov@example.com",
                institution="Колледж информационных технологий",
                course="Основы Python",
                study_format="Очное обучение",
                additional_options=["Получение сертификата", "Доступ к видеозаписям"],
            ),
            Student(
                record_id=2,
                full_name="Смирнова Анна Павловна",
                age=24,
                phone="87019998877",
                email="smirnova@example.com",
                institution="Университет",
                course="Веб-разработка",
                study_format="Дистанционное обучение",
                additional_options=[],
            ),
        ]

    def test_filter_by_name_and_course_case_insensitive(self) -> None:
        self.assertEqual(len(filter_students(self.students, "")), 2)
        self.assertEqual(len(filter_students(self.students, "иванов")), 1)
        self.assertEqual(filter_students(self.students, "веб")[0].record_id, 2)
        self.assertEqual(filter_students(self.students, "PYTHON")[0].record_id, 1)
        self.assertEqual(filter_students(self.students, "графика"), [])

    def test_save_students_to_csv(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = Path(tmp_dir) / "students.csv"
            save_students_to_file(csv_path, self.students)

            with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
                rows = list(csv.reader(file, delimiter=";"))

            self.assertEqual(tuple(rows[0]), CSV_HEADERS)
            self.assertEqual(len(rows), 3)
            self.assertEqual(rows[1][0], "Иванов Алексей Сергеевич")
            self.assertEqual(rows[1][1], "19")
            self.assertEqual(rows[1][2], "+77001112233")
            self.assertEqual(rows[1][3], "ivanov@example.com")
            self.assertEqual(rows[1][5], "Основы Python")
            self.assertEqual(rows[1][6], "Очное обучение")
            self.assertEqual(
                rows[1][7],
                "Получение сертификата, Доступ к видеозаписям",
            )
            self.assertEqual(rows[2][7], "Не выбраны")

    def test_save_students_to_txt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            txt_path = Path(tmp_dir) / "students.txt"
            save_students_to_file(txt_path, self.students)

            content = txt_path.read_text(encoding="utf-8")
            self.assertIn("Иванов Алексей Сергеевич", content)
            self.assertIn("Смирнова Анна Павловна", content)
            self.assertIn("Основы Python", content)
            self.assertIn("Веб-разработка", content)
            self.assertIn("Получение сертификата, Доступ к видеозаписям", content)
            self.assertIn("Не выбраны", content)


if __name__ == "__main__":
    unittest.main()
