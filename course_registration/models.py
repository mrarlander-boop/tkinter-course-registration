"""Модели данных и константы для приложения «Регистрация на учебные курсы»."""

from dataclasses import dataclass, field


COURSES: tuple[str, ...] = (
    "Основы Python",
    "Разработка приложений в Tkinter",
    "Веб-разработка",
    "Работа с базами данных",
    "Компьютерная графика",
)

STUDY_FORMATS: tuple[str, ...] = (
    "Очное обучение",
    "Дистанционное обучение",
    "Смешанный формат",
)

ADDITIONAL_OPTIONS: tuple[str, ...] = (
    "Получение сертификата",
    "Доступ к видеозаписям",
    "Дополнительные практические занятия",
)

MIN_AGE = 14
MAX_AGE = 80


@dataclass
class Student:
    """Представляет зарегистрированного на учебный курс студента."""

    record_id: int
    full_name: str
    age: int
    phone: str
    email: str
    institution: str
    course: str
    study_format: str
    additional_options: list[str] = field(default_factory=list)

    def options_text(self) -> str:
        """Возвращает строку с выбранными дополнительными возможностями."""
        if not self.additional_options:
            return "Не выбраны"
        return ", ".join(self.additional_options)

    def to_table_row(self) -> tuple[str, int, str, str, str]:
        """Возвращает кортеж значений для отображения в таблице Treeview."""
        return (
            self.full_name,
            self.age,
            self.course,
            self.study_format,
            self.phone,
        )

    def format_summary(self) -> str:
        """Формирует подробную итоговую информацию о регистрации студента."""
        return (
            f"Ф. И. О.: {self.full_name}\n"
            f"Возраст: {self.age}\n"
            f"Телефон: {self.phone}\n"
            f"Электронная почта: {self.email}\n"
            f"Учебное заведение: {self.institution}\n"
            f"Учебный курс: {self.course}\n"
            f"Форма обучения: {self.study_format}\n"
            f"Дополнительные возможности: {self.options_text()}"
        )
