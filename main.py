import sys

from PyQt6 import uic
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
import sqlite3


class AddEditCoffeeSHOP(QMainWindow):
    ...


class TurkishCoffeeMakerSHOP(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("daxak.jpg"))
        uic.loadUi("main.ui", self)
        self.con = sqlite3.connect("coffee.sqlite")
        self.cur = self.con.cursor()
        self.update_table()

    def update_table(self):
        coffee = self.cur.execute("""SELECT * FROM Coffee""").fetchall()
        if not coffee:
            self.statusbar.showMessage("Информация не найдена")
            return
        self.statusbar.clear()
        self.tableWidget.setRowCount(len(coffee))
        self.tableWidget.setColumnCount(len(coffee[0]))
        self.tableWidget.setHorizontalHeaderLabels(["ID", "Сорт", "Обжарка", "Тип", "Описание", "Цена", "Объем"])
        for i, row in enumerate(coffee):
            for j, value in enumerate(row):
                self.tableWidget.setItem(i, j, QTableWidgetItem(value))

    def add_coffee(self):
        ...

    def edit_coffee(self):
        ...

    def delete_coffee(self):
        ...


if __name__ == "__main__":
    app = QApplication(sys.argv)
    shop = TurkishCoffeeMakerSHOP()
    shop.show()
    sys.exit(app.exec())
