import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QLabel, QFrame, QGraphicsDropShadowEffect, QDesktopWidget,
    QDateEdit, QCalendarWidget
)
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt, QDate
from datetime import datetime
import subprocess

class ToDoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Elegant To-Do List")
        self.setMinimumSize(700, 750)
        self.init_ui()
        self.center_window()
        self.load_tasks()

    def center_window(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def init_ui(self):
        # Main horizontal layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)

        # Calendar Widget on the left
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.selectionChanged.connect(self.filter_tasks_by_date)
        self.calendar.setFixedWidth(300)
        main_layout.addWidget(self.calendar)

        # Card Container on the right
        card = QFrame()
        card.setObjectName("MainCard")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(15)
    
        # Drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 50))
        card.setGraphicsEffect(shadow)
    
        # Section Label
        title = QLabel("📝 Your Tasks")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: 600;")
    
        # Input Layout: Task + Due Date + Add Button
        input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Add a new task...")
    
        self.due_date_input = QDateEdit()
        self.due_date_input.setCalendarPopup(True)
        self.due_date_input.setDate(QDate.currentDate())
    
        add_button = QPushButton("Add")
        add_button.setObjectName("AddTask")
        add_button.clicked.connect(self.add_task)
    
        input_layout.addWidget(self.task_input)
        input_layout.addWidget(self.due_date_input)
        input_layout.addWidget(add_button)
    
        # Task List
        self.task_list = QListWidget()
        self.task_list.itemChanged.connect(self.update_task_status)
    
        # Buttons: Complete / Incomplete / Edit / Delete
        buttons_layout = QHBoxLayout()
    
        mark_all_button = QPushButton("Mark All Completed")
        mark_all_button.setObjectName("MarkAllCompleted")
        mark_all_button.clicked.connect(self.mark_all_completed)
    
        unmark_all_button = QPushButton("Mark All Incomplete")
        unmark_all_button.setObjectName("MarkAllIncomplete")
        unmark_all_button.clicked.connect(self.mark_all_incomplete)
    
        delete_button = QPushButton("Delete")
        delete_button.setObjectName("DeleteTask")
        delete_button.clicked.connect(self.delete_task)
    
        edit_button = QPushButton("Edit")
        edit_button.setObjectName("EditTask")
        edit_button.clicked.connect(self.edit_task)
    
        buttons_layout.addWidget(mark_all_button)
        buttons_layout.addWidget(unmark_all_button)
        buttons_layout.addWidget(edit_button)
        buttons_layout.addWidget(delete_button)
    
        # Assemble Card Layout
        card_layout.addWidget(title)
        card_layout.addLayout(input_layout)
        card_layout.addWidget(self.task_list)
        card_layout.addLayout(buttons_layout)
    
        # Add the card to the main layout
        main_layout.addWidget(card)
    
        # Apply stylesheet
        try:
            self.setStyleSheet(open("style.qss").read())
        except Exception:
            print("No stylesheet found or failed to load.")

    def add_task(self):
        task_text = self.task_input.text().strip()
        due_date = self.due_date_input.date().toString("yyyy-MM-dd")
        if task_text:
            display_text = f"{task_text} (Due: {due_date})"
            item = QListWidgetItem(display_text)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, {"task": task_text, "due": due_date})

            if QDate.fromString(due_date, "yyyy-MM-dd") < QDate.currentDate():
                item.setForeground(QColor("red"))

            self.task_list.addItem(item)
            self.task_input.clear()
            self.save_tasks()
            self.filter_tasks_by_date()

    def delete_task(self):
        selected = self.task_list.currentRow()
        if selected >= 0:
            self.task_list.takeItem(selected)
            self.save_tasks()

    def edit_task(self):
        selected = self.task_list.currentItem()
        if selected:
            new_task_text = self.task_input.text().strip()
            if new_task_text:
                data = selected.data(Qt.UserRole)
                data["task"] = new_task_text
                selected.setData(Qt.UserRole, data)
                selected.setText(f"{new_task_text} (Due: {data['due']})")

                # Restore visual indicators
                if data["due"] < QDate.currentDate().toString("yyyy-MM-dd") and selected.checkState() != Qt.Checked:
                    selected.setForeground(Qt.red)
                else:
                    selected.setForeground(Qt.black)

                self.task_input.clear()
                self.save_tasks()
                self.filter_tasks_by_date()

    def update_task_status(self, item):
        font = item.font()
        font.setStrikeOut(item.checkState() == Qt.Checked)
        item.setFont(font)
        self.save_tasks()

    def save_tasks(self, filename="tasks.json"):
        tasks_data = []
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            data = item.data(Qt.UserRole)
            if data:
                task_entry = {
                    "task": data["task"],
                    "due": data["due"],
                    "completed": item.checkState() == Qt.Checked
                }
                tasks_data.append(task_entry)
        with open(filename, "w") as file:
            json.dump(tasks_data, file, indent=4)

    def mark_all_completed(self):
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            item.setCheckState(Qt.Checked)
            font = item.font()
            font.setStrikeOut(True)
            item.setFont(font)
        self.save_tasks()

    def mark_all_incomplete(self):
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            item.setCheckState(Qt.Unchecked)
            font = item.font()
            font.setStrikeOut(False)
            item.setFont(font)
        self.save_tasks()
    
    def load_notified_log(self, filename="notified.json"):
        try:
            with open(filename, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_notified_log(self, log, filename="notified.json"):
        with open(filename, "w") as file:
            json.dump(log, file)
    
    def send_notification(self, title, message):
        script = f'display notification "{message}" with title "{title}"'
        subprocess.run(["osascript", "-e", script])

    def load_tasks(self, filename="tasks.json"):
        try:
            with open(filename, "r") as file:
                tasks_data = json.load(file)

            today_str = datetime.today().strftime("%Y-%m-%d")
            notified_log = self.load_notified_log()

            for entry in tasks_data:
                task = entry["task"]
                due = entry["due"]
                completed = entry["completed"]

                display_text = f"{task} (Due: {due})"
                item = QListWidgetItem(display_text)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)
                item.setCheckState(Qt.Checked if completed else Qt.Unchecked)
                item.setData(Qt.UserRole, {"task": task, "due": due})
            
                if due < today_str and not completed:
                    item.setForeground(Qt.red)

                self.task_list.addItem(item)

                # Send notification only once per day
                if due <= today_str and not completed:
                    task_id = f"{task}_{due}"
                    if notified_log.get(task_id) != today_str:
                        self.send_notification(
                            title="Task Reminder",
                            message=f"'{task}' is due{' today!' if due == today_str else ' and overdue!'}"
                        )
                        notified_log[task_id] = today_str

            self.save_notified_log(notified_log)

        except FileNotFoundError:
            pass

    def filter_tasks_by_date(self):
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            data = item.data(Qt.UserRole)
            item.setHidden(data["due"] != selected_date)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ToDoApp()
    window.show()
    sys.exit(app.exec_())


