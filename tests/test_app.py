"""Интеграционные тесты графического интерфейса Tkinter."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from course_registration.app import MIN_HEIGHT, MIN_WIDTH, WINDOW_TITLE, create_app
from course_registration.models import ADDITIONAL_OPTIONS, COURSES, STUDY_FORMATS


class TestCourseRegistrationApp(unittest.TestCase):
    """Тесты основных сценариев работы интерфейса."""

    def setUp(self) -> None:
        self.root, self.app = create_app()
        self.root.withdraw()
        self.root.update_idletasks()

    def tearDown(self) -> None:
        if self.root.winfo_exists():
            self.root.destroy()

    def _fill_valid_form(
        self,
        name: str = "Сидоров Дмитрий Олегович",
        age: str = "21",
        phone: str = "+77051234567",
        email: str = "sidorov@mail.ru",
        institution: str = "Политехнический колледж",
        course: str = COURSES[1],
        study_format: str = STUDY_FORMATS[2],
    ) -> None:
        self.app.full_name_var.set(name)
        self.app.age_var.set(age)
        self.app.phone_var.set(phone)
        self.app.email_var.set(email)
        self.app.institution_var.set(institution)
        self.app.course_var.set(course)
        self.app.study_format_var.set(study_format)
        self.app.option_vars[ADDITIONAL_OPTIONS[0]].set(True)
        self.app.option_vars[ADDITIONAL_OPTIONS[2]].set(True)

    def test_window_configuration_and_columns(self) -> None:
        self.assertEqual(self.root.title(), WINDOW_TITLE)
        self.assertGreaterEqual(MIN_WIDTH, 650)
        self.assertGreaterEqual(MIN_HEIGHT, 500)
        self.assertEqual(tuple(self.app.course_combobox["values"]), COURSES)

        headings = [
            self.app.tree.heading(col, "text")
            for col in self.app.tree["columns"]
        ]
        self.assertEqual(
            headings,
            ["Ф. И. О.", "Возраст", "Курс", "Форма обучения", "Телефон"],
        )

    @patch("course_registration.app.messagebox.showerror")
    def test_register_invalid_shows_error(self, mock_error) -> None:
        result = self.app.register_student()
        self.assertFalse(result)
        mock_error.assert_called_once()
        self.assertEqual(len(self.app.students), 0)

    @patch("course_registration.app.messagebox.showinfo")
    def test_register_student_adds_to_table_and_clears_form(self, mock_info) -> None:
        self._fill_valid_form()
        result = self.app.register_student()

        self.assertTrue(result)
        mock_info.assert_called_once()
        self.assertEqual(len(self.app.students), 1)
        items = self.app.tree.get_children()
        self.assertEqual(len(items), 1)

        values = self.app.tree.item(items[0], "values")
        self.assertEqual(values[0], "Сидоров Дмитрий Олегович")
        self.assertEqual(str(values[1]), "21")
        self.assertEqual(values[2], COURSES[1])
        self.assertEqual(values[3], STUDY_FORMATS[2])
        self.assertEqual(values[4], "+77051234567")

        # Форма должна быть очищена после успешной регистрации
        self.assertEqual(self.app.full_name_var.get(), "")
        self.assertEqual(self.app.course_var.get(), "")
        self.assertEqual(self.app.study_format_var.get(), "")

    @patch("course_registration.app.messagebox.showinfo")
    def test_live_search_filters_treeview(self, _mock_info) -> None:
        self._fill_valid_form(name="Алексеев Игорь", course="Основы Python")
        self.app.register_student()

        self._fill_valid_form(name="Белова Мария", course="Компьютерная графика")
        self.app.register_student()

        self.assertEqual(len(self.app.tree.get_children()), 2)

        self.app.search_var.set("мария")
        self.assertEqual(len(self.app.tree.get_children()), 1)

        self.app.search_var.set("python")
        self.assertEqual(len(self.app.tree.get_children()), 1)

        self.app.reset_search()
        self.assertEqual(len(self.app.tree.get_children()), 2)

    @patch("course_registration.app.messagebox.askyesno", return_value=True)
    @patch("course_registration.app.messagebox.showinfo")
    def test_show_details_and_delete_student(self, mock_info, mock_confirm) -> None:
        self._fill_valid_form()
        self.app.register_student()
        item_id = self.app.tree.get_children()[0]
        self.app.tree.selection_set(item_id)

        mock_info.reset_mock()
        self.app.show_selected_details()
        mock_info.assert_called_once()
        self.assertIn("Сидоров Дмитрий Олегович", mock_info.call_args[0][1])

        deleted = self.app.delete_selected_student()
        self.assertTrue(deleted)
        mock_confirm.assert_called_once()
        self.assertEqual(len(self.app.students), 0)
        self.assertEqual(len(self.app.tree.get_children()), 0)

    @patch("course_registration.app.messagebox.showinfo")
    @patch("course_registration.app.filedialog.asksaveasfilename")
    def test_save_to_file_dialog_flow(self, mock_save_dialog, mock_info) -> None:
        self._fill_valid_form()
        self.app.register_student()
        mock_info.reset_mock()

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = str(Path(tmp_dir) / "export.csv")
            mock_save_dialog.return_value = output_file

            saved = self.app.save_to_file()
            self.assertTrue(saved)
            self.assertTrue(Path(output_file).exists())
            mock_info.assert_called_once()


if __name__ == "__main__":
    unittest.main()
