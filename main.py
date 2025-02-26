import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout, QLineEdit, \
    QComboBox, QPushButton, QToolBar, QStatusBar, QGridLayout, QLabel, QMessageBox
import sqlite3


class DatabaseConnection:
    def __init__(self, db_filename="database.db"):
        self.db_filename = db_filename

    def connect(self):
        connection = sqlite3.connect(self.db_filename)
        return connection


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800, 600)
        self.init_ui()

    def init_ui(self):
        self.create_menus()
        self.create_toolbar()
        self.create_status_bar()
        self.create_table()

    def create_menus(self):
        menu_bar = self.menuBar()

        file_menu_item = menu_bar.addMenu("&File")
        help_menu_item = menu_bar.addMenu("&Help")
        edit_menu_item = menu_bar.addMenu("&Edit")

        add_student_action = self.create_action("icons/add.png", "Add Student", self.insert)
        search_action = self.create_action("icons/search.png", "Search", self.search)
        about_action = QAction("About", self)
        about_action.setMenuRole(QAction.MenuRole.NoRole)
        about_action.triggered.connect(self.about)

        file_menu_item.addAction(add_student_action)
        edit_menu_item.addAction(search_action)
        help_menu_item.addAction(about_action)

    def create_action(self, icon_path, text, slot):
        action = QAction(QIcon(icon_path), text, self)
        action.triggered.connect(slot)
        return action

    def create_toolbar(self):
        """Create the toolbar and add actions."""
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)

        toolbar.addAction(self.create_action("icons/add.png", "Add Student", self.insert))
        toolbar.addAction(self.create_action("icons/search.png", "Search", self.search))

    def create_status_bar(self):
        """Create the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def create_table(self):
        """Create the main table widget."""
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Course", "Mobile"])
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)
        self.table.cellClicked.connect(self.cell_clicked) # Detect a cell click

    def cell_clicked(self):
        edit_button = QPushButton("Edit record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete record")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.status_bar.removeWidget(child)

        self.status_bar.addWidget(edit_button)
        self.status_bar.addWidget(delete_button)

    def load_data(self):
        connection = DatabaseConnection().connect()
        result = connection.execute("SELECT * FROM students")
        self.table.setRowCount(0)

        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        This is an about section
        """
        self.setText(content)


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Edit student data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # get student name from selected row
        index = main_window.table.currentRow()
        student_name = main_window.table.item(index, 1).text()

        # get id from selected row
        self.student_id = main_window.table.item(index, 0).text()

        # add student name widget
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        course_name = main_window.table.item(index, 2).text()

        # add courses combobox
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        mobile_phone = main_window.table.item(index, 3).text()

        # add mobile number
        self.mobile = QLineEdit(mobile_phone)
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # add update button
        button = QPushButton("Update record")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE students SET name = ?, course = ?, mobile = ? WHERE id = ?",
            (
                self.student_name.text(),
                self.course_name.itemText(self.course_name.currentIndex()),
                self.mobile.text(),
                self.student_id
            )
        )
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete student data")
        index = main_window.table.currentRow()
        # get id from selected row
        self.student_id = main_window.table.item(index, 0).text()

        layout = QGridLayout()
        confirmation_message = QLabel('Are you sure you want to delete?')
        confirm = QPushButton("Confirm")
        cancel = QPushButton("Cancel")

        layout.addWidget(confirmation_message, 0, 0, 1, 2)
        layout.addWidget(confirm, 1, 0)
        layout.addWidget(cancel, 1, 1)
        self.setLayout(layout)

        confirm.clicked.connect(self.delete_student)

    def delete_student(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute(
            'DELETE from students WHERE id = ?', (self.student_id,)
        )
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()
        self.close()

        acknowledge_widget = QMessageBox()
        acknowledge_widget.setWindowTitle('Success')
        acknowledge_widget.setText("Record was deleted")
        acknowledge_widget.exec()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # add search box widget
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search criteria")
        layout.addWidget(self.search_box)

        # add search button
        button = QPushButton("Search")
        button.clicked.connect(self.search_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def search_student(self):
        name = self.search_box.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()

        result = cursor.execute("SELECT * FROM students WHERE name = ?", (name,))
        rows = list(result)
        items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            main_window.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert student data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()
        # add student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # add courses combobox
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # add mobile number
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # add submit button
        button = QPushButton("Submit")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()
        connection = sqlite3.connect(database="database.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())
