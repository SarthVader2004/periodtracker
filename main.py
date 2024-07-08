import flet as ft
import calendar
from datetime import datetime, timedelta

cal = calendar.Calendar()

date_class = {
    0: "Mo",
    1: "Tu",
    2: "We",
    3: "Th",
    4: "Fr",
    5: "Sa",
    6: "Su",
}

month_class = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}

date_box_style = {
    "width": 30,
    "height": 30,
    "alignment": ft.alignment.center,
    "shape": ft.BoxShape("rectangle"),
    "animate": ft.Animation(400, "ease"),
    "border_radius": 5,
}

class Settings:
    year = datetime.now().year
    month = datetime.now().month

    @staticmethod
    def get_year():
        return Settings.year

    @staticmethod
    def get_month():
        return Settings.month

    @staticmethod
    def get_date(delta):
        if delta == 1:
            if Settings.month + delta > 12:
                Settings.month = 1
                Settings.year += 1
            else:
                Settings.month += 1

        if delta == -1:
            if Settings.month + delta < 1:
                Settings.month = 12
                Settings.year -= 1
            else:
                Settings.month -= 1

class DateBox(ft.Container):
    def __init__(self, day, date=None, date_instance=None, opacity_=None, is_selected=False):
        super(DateBox, self).__init__(
            **date_box_style,
            data=date,
            opacity=opacity_,
            bgcolor=ft.colors.PINK_200 if is_selected else None,
            on_click=self.toggle_select,
        )

        self.day = day
        self.date_instance = date_instance

        self.content = ft.Text(self.day, text_align="center")

    def toggle_select(self, e: ft.TapEvent):
        if self.date_instance:
            self.date_instance.handle_date_click(self)

class DateGrid(ft.Column):
    def __init__(self, year, month, task_instance, selected_days=None):
        super(DateGrid, self).__init__()

        self.year = year
        self.month = month
        self.task_manager = task_instance
        self.selected_days = selected_days or []
        self.start_date = None
        self.end_date = None

        self.date = ft.Text(f"{month_class[self.month]} {self.year}")

        self.year_and_month = ft.Container(
            bgcolor="#20303e",
            border_radius=ft.border_radius.only(top_left=10, top_right=10),
            content=ft.Row(
                alignment="center",
                controls=[
                    ft.IconButton(
                        "chevron_left",
                        on_click=lambda e: self.update_date_grid(e, -1),
                    ),
                    ft.Container(width=150, content=self.date, alignment=ft.alignment.center),
                    ft.IconButton(
                        "chevron_right",
                        on_click=lambda e: self.update_date_grid(e, 1),
                    ),
                ],
            ),
        )

        self.controls.insert(1, self.year_and_month)

        week_days = ft.Row(
            alignment="spaceEvenly",
            controls=[DateBox(day=date_class[index], opacity_=0.7) for index in range(7)],
        )

        self.controls.insert(1, week_days)
        self.populate_date_grid(self.year, self.month)

    def populate_date_grid(self, year, month):
        del self.controls[2:]

        for week in cal.monthdayscalendar(year, month):
            row = ft.Row(alignment="spaceEvenly")
            for day in week:
                if day != 0:
                    is_selected = self.format_date(day) in self.selected_days
                    row.controls.append(
                        DateBox(day, self.format_date(day), self, is_selected=is_selected)
                    )
                else:
                    row.controls.append(DateBox(" "))

            self.controls.append(row)

    def update_date_grid(self, e: ft.TapEvent, delta):
        Settings.get_date(delta)
        self.update_year_and_month(Settings.get_year(), Settings.get_month())
        self.populate_date_grid(Settings.get_year(), Settings.get_month())
        self.update()

    def update_year_and_month(self, year, month):
        self.year = year
        self.month = month
        self.date.value = f"{month_class[self.month]} {self.year}"

    def format_date(self, day):
        return f"{self.year}-{self.month:02}-{day:02}"

    def handle_date_click(self, date_box):
        date = datetime.strptime(date_box.data, "%Y-%m-%d")

        if self.start_date and self.end_date:
            self.start_date = date
            self.end_date = None
            self.selected_days = [self.format_date(date.day)]
        elif self.start_date and not self.end_date:
            if date < self.start_date:
                self.start_date = date
                self.selected_days = [self.format_date(date.day)]
            else:
                self.end_date = date
                self.selected_days = [self.format_date((self.start_date + timedelta(days=i)).day)
                                      for i in range((self.end_date - self.start_date).days + 1)]

        else:
            self.start_date = date
            self.selected_days = [self.format_date(date.day)]

        self.populate_date_grid(self.year, self.month)
        self.update()

def input_style(height):
    return {
        "height": height,
        "focused_border_color": "blue",
        "border_radius": 5,
        "cursor_height": 16,
        "cursor_color": "white",
        "content_padding": 10,
        "border_width": 1.5,
        "text_size": 12,
    }

class TaskManager(ft.Column):
    def __init__(self, on_submit):
        super(TaskManager, self).__init__()

        self.cycle_length_input = ft.TextField(label="Cycle Length", keyboard_type=ft.KeyboardType.NUMBER, **input_style(38))
        self.period_days_input = ft.TextField(label="Period Days", keyboard_type=ft.KeyboardType.NUMBER, **input_style(38))
        self.submit_button = ft.ElevatedButton(text="Submit", on_click=self.submit_input)
        self.error_message = ft.Text(color=ft.colors.RED)

        self.controls.extend([
            self.cycle_length_input,
            self.period_days_input,
            self.submit_button,
            self.error_message
        ])

        self.on_submit = on_submit

    def submit_input(self, e):
        try:
            cycle_length = int(self.cycle_length_input.value)
            period_days = int(self.period_days_input.value)
            self.on_submit(cycle_length, period_days)
        except ValueError:
            self.error_message.value = "Please enter valid numbers."
            self.update()

class CalendarView(ft.Column):
    def __init__(self, cycle_length, period_days):
        super(CalendarView, self).__init__()
        self.cycle_length = cycle_length
        self.period_days = period_days
        self.selected_days = []

        self.grid = DateGrid(
            year=Settings.get_year(), month=Settings.get_month(), task_instance=self, selected_days=self.selected_days
        )

        self.controls.extend([
            self.grid
        ])

    def update_calendar(self):
        self.grid.populate_date_grid(Settings.get_year(), Settings.get_month())
        self.grid.update()

def main(page: ft.Page):
    def on_submit(cycle_length, period_days):
        page.clean()
        page.add(CalendarView(cycle_length, period_days))

    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#1f2128"
    page.scroll = ft.ScrollMode.AUTO

    task_manager = TaskManager(on_submit)

    page.add(
        ft.Column(
            controls=[
                task_manager,
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
    )

    page.update()

ft.app(main)
