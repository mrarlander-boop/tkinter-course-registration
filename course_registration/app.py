"""Графический интерфейс приложения «Регистрация на учебные курсы» на Tkinter."""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .models import ADDITIONAL_OPTIONS, COURSES, STUDY_FORMATS, Student
from .storage import filter_students, save_students_to_file
from .validation import ValidationError, validate_registration_data


WINDOW_TITLE = "Регистрация на учебные курсы"
WINDOW_WIDTH = 1020
WINDOW_HEIGHT = 780
MIN_WIDTH = 650
MIN_HEIGHT = 500

BG_MAIN = "#F3F6FA"
BG_CARD = "#FFFFFF"
BG_INPUT = "#FFFFFF"
BG_STRIPE = "#F8FAFC"
BG_TABLE_HEAD = "#E8EEF7"
BORDER_COLOR = "#CBD5E1"

TEXT_PRIMARY = "#0F172A"
TEXT_SECONDARY = "#475569"

BTN_PRIMARY_BG = "#2563EB"
BTN_PRIMARY_ACTIVE = "#1D4ED8"
BTN_SECONDARY_BG = "#E2E8F0"
BTN_SECONDARY_ACTIVE = "#CBD5E1"
BTN_DANGER_BG = "#DC2626"
BTN_DANGER_ACTIVE = "#B91C1C"
BTN_SUCCESS_BG = "#0F766E"
BTN_SUCCESS_ACTIVE = "#115E59"

FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_SUBTITLE = ("Segoe UI", 9)
FONT_SECTION = ("Segoe UI", 10, "bold")
FONT_BASE = ("Segoe UI", 10)
FONT_BUTTON = ("Segoe UI", 9, "bold")
FONT_SMALL = ("Segoe UI", 9)


def configure_styles(root: tk.Tk) -> ttk.Style:
    """Настраивает светлую тему и стили виджетов ttk."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(
        "App.TCombobox",
        fieldbackground=BG_INPUT,
        background=BTN_SECONDARY_BG,
        foreground=TEXT_PRIMARY,
        arrowcolor=TEXT_PRIMARY,
        bordercolor=BORDER_COLOR,
        padding=4,
    )
    style.map(
        "App.TCombobox",
        fieldbackground=[("readonly", BG_INPUT)],
        selectbackground=[("readonly", BG_INPUT)],
        selectforeground=[("readonly", TEXT_PRIMARY)],
    )

    style.configure(
        "Students.Treeview",
        background=BG_CARD,
        fieldbackground=BG_CARD,
        foreground=TEXT_PRIMARY,
        rowheight=26,
        font=FONT_BASE,
        bordercolor=BORDER_COLOR,
    )
    style.configure(
        "Students.Treeview.Heading",
        background=BG_TABLE_HEAD,
        foreground=TEXT_PRIMARY,
        font=FONT_SECTION,
        relief="flat",
        padding=(6, 6),
    )
    style.map(
        "Students.Treeview",
        background=[("selected", "#DBEAFE")],
        foreground=[("selected", TEXT_PRIMARY)],
    )
    style.map(
        "Students.Treeview.Heading",
        background=[("active", "#DCE6F5")],
    )

    return style


def center_window(root: tk.Tk, width: int, height: int) -> None:
    """Устанавливает размер окна и центрирует его на экране."""
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    pos_x = max(0, (screen_width - width) // 2)
    pos_y = max(0, (screen_height - height) // 2)
    root.geometry(f"{width}x{height}+{pos_x}+{pos_y}")


def create_header(parent: tk.Widget) -> tk.Frame:
    """Создаёт верхний заголовок приложения."""
    header = tk.Frame(parent, bg=BG_MAIN)
    header.pack(fill="x", padx=16, pady=(10, 6))

    tk.Label(
        header,
        text=WINDOW_TITLE,
        font=FONT_TITLE,
        bg=BG_MAIN,
        fg=TEXT_PRIMARY,
        anchor="w",
    ).pack(anchor="w")

    tk.Label(
        header,
        text="Заполните данные студента, выберите учебный курс, форму обучения и дополнительные возможности.",
        font=FONT_SUBTITLE,
        bg=BG_MAIN,
        fg=TEXT_SECONDARY,
        anchor="w",
    ).pack(anchor="w", pady=(1, 0))

    return header


def create_labeled_entry(
    parent: tk.Widget,
    row: int,
    label_text: str,
    variable: tk.StringVar,
) -> tk.Entry:
    """Создаёт пару Label + Entry в сетке формы."""
    label = tk.Label(
        parent,
        text=label_text,
        font=FONT_BASE,
        bg=BG_CARD,
        fg=TEXT_PRIMARY,
        anchor="w",
    )
    label.grid(row=row, column=0, sticky="w", padx=(10, 10), pady=4)

    entry = tk.Entry(
        parent,
        textvariable=variable,
        font=FONT_BASE,
        bg=BG_INPUT,
        fg=TEXT_PRIMARY,
        insertbackground=TEXT_PRIMARY,
        relief="solid",
        bd=1,
        highlightthickness=1,
        highlightcolor=BTN_PRIMARY_BG,
        highlightbackground=BORDER_COLOR,
    )
    entry.grid(row=row, column=1, sticky="ew", padx=(0, 10), pady=4, ipady=2)
    return entry


class CourseRegistrationApp:
    """Главное окно и логика взаимодействия приложения регистрации на курсы."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.students: list[Student] = []
        self._next_record_id = 1

        self.full_name_var = tk.StringVar()
        self.age_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.institution_var = tk.StringVar()
        self.course_var = tk.StringVar(value="")
        self.study_format_var = tk.StringVar(value="")
        self.option_vars: dict[str, tk.BooleanVar] = {
            option: tk.BooleanVar(value=False) for option in ADDITIONAL_OPTIONS
        }
        self.search_var = tk.StringVar()
        self.count_var = tk.StringVar(value="Всего записей: 0")

        self._configure_window()
        self._build_interface()

    def _configure_window(self) -> None:
        """Настраивает параметры главного окна."""
        self.root.title(WINDOW_TITLE)
        self.root.configure(bg=BG_MAIN)
        self.root.minsize(MIN_WIDTH, MIN_HEIGHT)
        center_window(self.root, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.style = configure_styles(self.root)

    def _build_interface(self) -> None:
        """Собирает все логические блоки графического интерфейса."""
        create_header(self.root)

        top_container = tk.Frame(self.root, bg=BG_MAIN)
        top_container.pack(fill="x", padx=16, pady=(0, 8))
        top_container.columnconfigure(0, weight=3, uniform="top")
        top_container.columnconfigure(1, weight=2, uniform="top")

        self._build_student_info_frame(top_container)
        self._build_study_settings_column(top_container)
        self._build_form_actions_frame(self.root)
        # Нижняя панель кнопок размещается до расширяемой таблицы, чтобы никогда не обрезалась
        self._build_bottom_actions_frame(self.root)
        self._build_students_table_frame(self.root)

        self.search_var.trace_add("write", self._on_search_changed)

    def _build_student_info_frame(self, parent: tk.Widget) -> None:
        """Создаёт блок ввода данных студента (Label и Entry)."""
        student_frame = tk.LabelFrame(
            parent,
            text=" Данные студента ",
            font=FONT_SECTION,
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            bd=1,
            relief="groove",
            padx=6,
            pady=8,
        )
        student_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        student_frame.columnconfigure(1, weight=1)

        self.full_name_entry = create_labeled_entry(
            student_frame, 0, "Ф. И. О.: *", self.full_name_var
        )
        self.age_entry = create_labeled_entry(
            student_frame, 1, "Возраст (14–80): *", self.age_var
        )
        self.phone_entry = create_labeled_entry(
            student_frame, 2, "Номер телефона: *", self.phone_var
        )
        self.email_entry = create_labeled_entry(
            student_frame, 3, "Электронная почта: *", self.email_var
        )
        self.institution_entry = create_labeled_entry(
            student_frame, 4, "Учебное заведение: *", self.institution_var
        )

        hint_label = tk.Label(
            student_frame,
            text="* — обязательные поля. Телефон: только цифры и символ «+».",
            font=FONT_SMALL,
            bg=BG_CARD,
            fg=TEXT_SECONDARY,
            anchor="w",
        )
        hint_label.grid(row=5, column=0, columnspan=2, sticky="w", padx=10, pady=(6, 2))

    def _build_study_settings_column(self, parent: tk.Widget) -> None:
        """Создаёт блоки выбора курса, формы обучения и дополнительных возможностей."""
        right_column = tk.Frame(parent, bg=BG_MAIN)
        right_column.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        right_column.columnconfigure(0, weight=1)

        course_frame = tk.LabelFrame(
            right_column,
            text=" Выбор курса и формы обучения ",
            font=FONT_SECTION,
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            bd=1,
            relief="groove",
            padx=10,
            pady=5,
        )
        course_frame.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        course_frame.columnconfigure(0, weight=1)

        tk.Label(
            course_frame,
            text="Учебный курс: *",
            font=FONT_BASE,
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=(0, 2))

        self.course_combobox = ttk.Combobox(
            course_frame,
            textvariable=self.course_var,
            values=COURSES,
            state="readonly",
            font=FONT_BASE,
            style="App.TCombobox",
        )
        self.course_combobox.grid(row=1, column=0, sticky="ew", pady=(0, 6))

        tk.Label(
            course_frame,
            text="Форма обучения: *",
            font=FONT_BASE,
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            anchor="w",
        ).grid(row=2, column=0, sticky="w", pady=(0, 1))

        self.format_radiobuttons: list[tk.Radiobutton] = []
        for idx, fmt in enumerate(STUDY_FORMATS, start=3):
            rb = tk.Radiobutton(
                course_frame,
                text=fmt,
                variable=self.study_format_var,
                value=fmt,
                font=FONT_BASE,
                bg=BG_CARD,
                fg=TEXT_PRIMARY,
                activebackground=BG_CARD,
                activeforeground=TEXT_PRIMARY,
                selectcolor=BG_CARD,
                anchor="w",
                cursor="hand2",
            )
            rb.grid(row=idx, column=0, sticky="w", pady=0)
            self.format_radiobuttons.append(rb)

        options_frame = tk.LabelFrame(
            right_column,
            text=" Дополнительные возможности ",
            font=FONT_SECTION,
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            bd=1,
            relief="groove",
            padx=10,
            pady=5,
        )
        options_frame.grid(row=1, column=0, sticky="nsew")

        self.option_checkbuttons: list[tk.Checkbutton] = []
        for idx, option_text in enumerate(ADDITIONAL_OPTIONS):
            cb = tk.Checkbutton(
                options_frame,
                text=option_text,
                variable=self.option_vars[option_text],
                font=FONT_BASE,
                bg=BG_CARD,
                fg=TEXT_PRIMARY,
                activebackground=BG_CARD,
                activeforeground=TEXT_PRIMARY,
                selectcolor=BG_CARD,
                anchor="w",
                cursor="hand2",
            )
            cb.grid(row=idx, column=0, sticky="w", pady=1)
            self.option_checkbuttons.append(cb)

    def _build_form_actions_frame(self, parent: tk.Widget) -> None:
        """Создаёт панель кнопок отправки и очистки формы регистрации."""
        actions_frame = tk.Frame(parent, bg=BG_MAIN)
        actions_frame.pack(fill="x", padx=16, pady=(2, 8))

        self.register_button = tk.Button(
            actions_frame,
            text="Зарегистрироваться",
            command=self.register_student,
            font=FONT_BUTTON,
            bg=BTN_PRIMARY_BG,
            fg="#FFFFFF",
            activebackground=BTN_PRIMARY_ACTIVE,
            activeforeground="#FFFFFF",
            relief="flat",
            padx=16,
            pady=7,
            cursor="hand2",
        )
        self.register_button.pack(side="left", padx=(0, 8))

        self.clear_button = tk.Button(
            actions_frame,
            text="Очистить форму",
            command=self.clear_form,
            font=FONT_BUTTON,
            bg=BTN_SECONDARY_BG,
            fg=TEXT_PRIMARY,
            activebackground=BTN_SECONDARY_ACTIVE,
            activeforeground=TEXT_PRIMARY,
            relief="flat",
            padx=14,
            pady=7,
            cursor="hand2",
        )
        self.clear_button.pack(side="left")

    def _build_bottom_actions_frame(self, parent: tk.Widget) -> None:
        """Создаёт нижнюю панель управления записями, экспорта и выхода."""
        bottom_frame = tk.Frame(parent, bg=BG_MAIN)
        bottom_frame.pack(side="bottom", fill="x", padx=16, pady=(0, 12))

        self.details_button = tk.Button(
            bottom_frame,
            text="Показать подробности",
            command=self.show_selected_details,
            font=FONT_BUTTON,
            bg=BTN_SECONDARY_BG,
            fg=TEXT_PRIMARY,
            activebackground=BTN_SECONDARY_ACTIVE,
            activeforeground=TEXT_PRIMARY,
            relief="flat",
            padx=12,
            pady=7,
            cursor="hand2",
        )
        self.details_button.pack(side="left", padx=(0, 8))

        self.delete_button = tk.Button(
            bottom_frame,
            text="Удалить выбранную запись",
            command=self.delete_selected_student,
            font=FONT_BUTTON,
            bg=BTN_DANGER_BG,
            fg="#FFFFFF",
            activebackground=BTN_DANGER_ACTIVE,
            activeforeground="#FFFFFF",
            relief="flat",
            padx=12,
            pady=7,
            cursor="hand2",
        )
        self.delete_button.pack(side="left", padx=(0, 8))

        self.save_button = tk.Button(
            bottom_frame,
            text="Сохранить в файл",
            command=self.save_to_file,
            font=FONT_BUTTON,
            bg=BTN_SUCCESS_BG,
            fg="#FFFFFF",
            activebackground=BTN_SUCCESS_ACTIVE,
            activeforeground="#FFFFFF",
            relief="flat",
            padx=12,
            pady=7,
            cursor="hand2",
        )
        self.save_button.pack(side="left", padx=(0, 8))

        self.close_button = tk.Button(
            bottom_frame,
            text="Закрыть программу",
            command=self.close_application,
            font=FONT_BUTTON,
            bg=BTN_SECONDARY_BG,
            fg=TEXT_PRIMARY,
            activebackground=BTN_SECONDARY_ACTIVE,
            activeforeground=TEXT_PRIMARY,
            relief="flat",
            padx=12,
            pady=7,
            cursor="hand2",
        )
        self.close_button.pack(side="right")

    def _build_students_table_frame(self, parent: tk.Widget) -> None:
        """Создаёт блок поиска и таблицу Treeview зарегистрированных студентов."""
        table_section = tk.LabelFrame(
            parent,
            text=" Зарегистрированные студенты ",
            font=FONT_SECTION,
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            bd=1,
            relief="groove",
            padx=10,
            pady=8,
        )
        table_section.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        search_frame = tk.Frame(table_section, bg=BG_CARD)
        search_frame.pack(fill="x", pady=(0, 8))

        tk.Label(
            search_frame,
            text="Поиск (по Ф. И. О. или курсу):",
            font=FONT_BASE,
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
        ).pack(side="left", padx=(0, 8))

        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=FONT_BASE,
            bg=BG_INPUT,
            fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY,
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightcolor=BTN_PRIMARY_BG,
            highlightbackground=BORDER_COLOR,
            width=36,
        )
        self.search_entry.pack(side="left", ipady=2, padx=(0, 8))

        self.reset_search_button = tk.Button(
            search_frame,
            text="Сбросить поиск",
            command=self.reset_search,
            font=FONT_SMALL,
            bg=BTN_SECONDARY_BG,
            fg=TEXT_PRIMARY,
            activebackground=BTN_SECONDARY_ACTIVE,
            activeforeground=TEXT_PRIMARY,
            relief="flat",
            padx=10,
            pady=3,
            cursor="hand2",
        )
        self.reset_search_button.pack(side="left")

        tk.Label(
            search_frame,
            textvariable=self.count_var,
            font=FONT_SMALL,
            bg=BG_CARD,
            fg=TEXT_SECONDARY,
        ).pack(side="right")

        tree_container = tk.Frame(table_section, bg=BG_CARD)
        tree_container.pack(fill="both", expand=True)
        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)

        columns = ("full_name", "age", "course", "study_format", "phone")
        self.tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=7,
            style="Students.Treeview",
        )

        column_specs = (
            ("full_name", "Ф. И. О.", 220, "w", True),
            ("age", "Возраст", 75, "center", False),
            ("course", "Курс", 220, "w", True),
            ("study_format", "Форма обучения", 160, "w", True),
            ("phone", "Телефон", 145, "w", True),
        )
        for col_id, heading_text, width, anchor, stretch in column_specs:
            self.tree.heading(col_id, text=heading_text, anchor=anchor)
            self.tree.column(
                col_id,
                width=width,
                minwidth=70,
                anchor=anchor,
                stretch=stretch,
            )

        self.tree.tag_configure("evenrow", background=BG_CARD)
        self.tree.tag_configure("oddrow", background=BG_STRIPE)
        self.tree.bind("<Double-1>", lambda _event: self.show_selected_details())

        y_scroll = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

    def get_selected_options(self) -> list[str]:
        """Возвращает список выбранных дополнительных возможностей."""
        return [
            option_name
            for option_name, var in self.option_vars.items()
            if var.get()
        ]

    def register_student(self) -> bool:
        """Проверяет форму, регистрирует студента и обновляет таблицу."""
        try:
            validated = validate_registration_data(
                full_name=self.full_name_var.get(),
                age_raw=self.age_var.get(),
                phone_raw=self.phone_var.get(),
                email_raw=self.email_var.get(),
                institution=self.institution_var.get(),
                course=self.course_var.get(),
                study_format=self.study_format_var.get(),
                additional_options=self.get_selected_options(),
            )
        except ValidationError as exc:
            messagebox.showerror("Ошибка ввода данных", str(exc))
            return False
        except Exception as exc:  # pragma: no cover - защитный обработчик
            messagebox.showerror(
                "Непредвиденная ошибка",
                f"Не удалось выполнить регистрацию: {exc}",
            )
            return False

        student = Student(record_id=self._next_record_id, **validated)
        self._next_record_id += 1
        self.students.append(student)
        self.refresh_table()

        summary_message = (
            "Студент успешно зарегистрирован!\n\n"
            f"{student.format_summary()}"
        )
        messagebox.showinfo("Успешная регистрация", summary_message)
        self.clear_form()
        return True

    def clear_form(self) -> None:
        """Очищает все поля ввода и сбрасывает выбор курса, формы и опций."""
        self.full_name_var.set("")
        self.age_var.set("")
        self.phone_var.set("")
        self.email_var.set("")
        self.institution_var.set("")
        self.course_var.set("")
        self.course_combobox.set("")
        self.study_format_var.set("")
        for var in self.option_vars.values():
            var.set(False)
        self.full_name_entry.focus_set()

    def reset_search(self) -> None:
        """Сбрасывает строку поиска и отображает все записи."""
        self.search_var.set("")
        self.search_entry.focus_set()

    def _on_search_changed(self, *_args: object) -> None:
        """Обновляет таблицу при изменении поискового запроса."""
        self.refresh_table()

    def refresh_table(self) -> None:
        """Перезаполняет Treeview с учётом текущего поискового фильтра."""
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)

        query = self.search_var.get()
        visible_students = filter_students(self.students, query)

        for idx, student in enumerate(visible_students):
            row_tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert(
                "",
                "end",
                iid=str(student.record_id),
                values=student.to_table_row(),
                tags=(row_tag,),
            )

        total = len(self.students)
        shown = len(visible_students)
        if query.strip():
            self.count_var.set(f"Найдено: {shown} из {total}")
        else:
            self.count_var.set(f"Всего записей: {total}")

    def _get_selected_student(self) -> Student | None:
        """Возвращает объект Student для выбранной строки таблицы или None."""
        selection = self.tree.selection()
        if not selection:
            return None

        try:
            selected_id = int(selection[0])
        except ValueError:
            return None

        for student in self.students:
            if student.record_id == selected_id:
                return student
        return None

    def show_selected_details(self) -> None:
        """Показывает подробную информацию о выбранном в таблице студенте."""
        student = self._get_selected_student()
        if student is None:
            messagebox.showwarning(
                "Запись не выбрана",
                "Выберите запись в таблице для просмотра подробностей.",
            )
            return

        messagebox.showinfo("Подробная информация о студенте", student.format_summary())

    def delete_selected_student(self) -> bool:
        """Удаляет выбранную запись из списка после подтверждения пользователя."""
        student = self._get_selected_student()
        if student is None:
            messagebox.showwarning(
                "Запись не выбрана",
                "Выберите запись в таблице, которую хотите удалить.",
            )
            return False

        confirmed = messagebox.askyesno(
            "Подтверждение удаления",
            f"Вы действительно хотите удалить запись студента «{student.full_name}»?",
        )
        if not confirmed:
            return False

        self.students = [
            item for item in self.students if item.record_id != student.record_id
        ]
        self.refresh_table()
        return True

    def save_to_file(self) -> bool:
        """Сохраняет список зарегистрированных студентов в CSV- или текстовый файл."""
        if not self.students:
            messagebox.showwarning(
                "Список пуст",
                "Нет зарегистрированных студентов для сохранения в файл.",
            )
            return False

        file_path = filedialog.asksaveasfilename(
            title="Сохранить список студентов",
            defaultextension=".csv",
            initialfile="registered_students.csv",
            filetypes=[
                ("CSV-файлы (*.csv)", "*.csv"),
                ("Текстовые файлы (*.txt)", "*.txt"),
                ("Все файлы (*.*)", "*.*"),
            ],
        )
        if not file_path:
            return False

        try:
            save_students_to_file(file_path, self.students)
        except OSError as exc:
            messagebox.showerror(
                "Ошибка сохранения",
                f"Не удалось сохранить данные в файл:\n{exc}",
            )
            return False

        messagebox.showinfo(
            "Сохранение выполнено",
            f"Список студентов (записей: {len(self.students)}) успешно сохранён в файл:\n{file_path}",
        )
        return True

    def close_application(self) -> None:
        """Корректно закрывает главное окно приложения."""
        self.root.destroy()


def create_app() -> tuple[tk.Tk, CourseRegistrationApp]:
    """Создаёт и инициализирует экземпляр приложения."""
    root = tk.Tk()
    app = CourseRegistrationApp(root)
    return root, app


def run_app() -> None:
    """Запускает главный цикл приложения."""
    root, _app = create_app()
    root.mainloop()
