import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMenu, QMessageBox
import sqlite3
from UI.mainUI import Ui_MainWindow as MainUI
from UI.addEditCoffeeForm import Ui_MainWindow as AddCoffeeFormUI


class AddEditCoffeeSHOP(QMainWindow, AddCoffeeFormUI):
    def __init__(self, parent=None, coffee_id=None):
        super().__init__(parent)
        self.setupUi(self)
        self.con = sqlite3.connect("data/coffee.sqlite")
        self.cur = self.con.cursor()
        coffee_id = coffee_id
        if coffee_id is not None:
            self.setWindowTitle("TURKISHCOFFEEEDIT")
            self.pushButton.setText("Отредактировать")
            self.pushButton.clicked.connect(lambda: self.editCoffee(coffee_id))
            self.fill_form(coffee_id)
        else:
            self.setWindowTitle("TURKISHCOFFEEADD")
            self.pushButton.setText("Добавить")
            self.pushButton.clicked.connect(self.addCoffee)

    def fill_form(self, coffee_id):
        name, roasting, typetext, description, price, volume = self.cur.execute(
            """SELECT name, roasting, type, description, price, volume FROM Coffee WHERE id = ?""",
            (coffee_id,)).fetchone()
        self.NameTextEdit.setText(name)
        self.RoastingTextEdit.setText(roasting)
        self.TypeComboBox.setCurrentText(typetext)
        self.DescriptionTextEdit.setPlainText(description)
        self.PriceSpinBox.setValue(price)
        self.VolumeSpinBox.setValue(volume)

    def checkBoxes(self) -> bool:
        if (self.NameTextEdit.text() and
                self.RoastingTextEdit.text() and
                self.PriceSpinBox.value() > 0 and
                self.VolumeSpinBox.value() > 0):
            return True
        return False

    def addCoffee(self):
        if not self.checkBoxes():
            self.statusbar.showMessage("Неправильно заполнена форма")
            return
        name = self.NameTextEdit.text()
        roasting = self.RoastingTextEdit.text()
        typetext = self.TypeComboBox.currentText()
        description = self.DescriptionTextEdit.toPlainText()
        price = self.PriceSpinBox.value()
        volume = self.VolumeSpinBox.value()
        self.cur.execute(
            """INSERT INTO Coffee (name, roasting, type, description, price, volume) VALUES(?, ?, ?, ?, ?, ?)""",
            (name, roasting, typetext, description, price, volume))
        self.con.commit()
        self.parent().update_table()
        self.close()

    def editCoffee(self, coffee_id):
        if not self.checkBoxes():
            self.statusbar.showMessage("Неправильно заполнена форма")
            return
        name = self.NameTextEdit.text()
        roasting = self.RoastingTextEdit.text()
        typetext = self.TypeComboBox.currentText()
        description = self.DescriptionTextEdit.toPlainText()
        price = self.PriceSpinBox.value()
        volume = self.VolumeSpinBox.value()
        self.cur.execute(
            """UPDATE Coffee SET
            name = ?,
            roasting = ?,
            type = ?,
             description = ?,
             price = ?,
             volume = ?
             WHERE id = ?""",
            (name, roasting, typetext, description, price, volume, coffee_id))
        self.con.commit()
        self.parent().update_table()
        self.close()


class TurkishCoffeeMakerSHOP(QMainWindow, MainUI):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon("data/daxak.jpg"))
        self.con = sqlite3.connect("data/coffee.sqlite")
        self.cur = self.con.cursor()
        self.update_table()
        self.tableWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tableWidget.customContextMenuRequested.connect(self.initMenu)

    def update_table(self):
        coffee = self.cur.execute("""SELECT * FROM Coffee""").fetchall()
        if not coffee:
            self.statusbar.showMessage("Информация не найдена!")
            return
        self.statusbar.clearMessage()
        self.tableWidget.setRowCount(len(coffee))
        self.tableWidget.setColumnCount(len(coffee[0]))
        self.tableWidget.setHorizontalHeaderLabels(["ID", "Сорт", "Обжарка", "Тип", "Описание", "Цена", "Объем"])
        for i, row in enumerate(coffee):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.tableWidget.setItem(i, j, item)
        self.tableWidget.resizeRowsToContents()

    def initMenu(self, pos):
        global_pos = self.tableWidget.mapToGlobal(pos)
        self.context_menu = QMenu()
        add_coffee_action = QAction(QIcon("data/iconplus.png"), "Добавить", self)
        add_coffee_action.triggered.connect(self.add_coffee)
        self.context_menu.addAction(add_coffee_action)
        selected_items = self.tableWidget.selectedItems()
        selected_row = self.tableWidget.currentRow()
        if selected_row >= 0:
            edit_coffee_action = QAction(QIcon("data/iconedit.png"), "Изменить", self)
            edit_coffee_action.triggered.connect(
                lambda: self.edit_coffee(int(self.tableWidget.item(selected_row, 0).text())))
            self.context_menu.addAction(edit_coffee_action)
        if selected_items:
            if len(selected_items) == 1:
                delete_coffee_action = QAction(QIcon("data/icondelete.png"), "Удалить", self)
                delete_coffee_action.triggered.connect(lambda: self.delete_coffee(selected_items))
            else:
                delete_coffee_action = QAction(QIcon("data/icondelete.png"), "Удалить выбранные", self)
                delete_coffee_action.triggered.connect(lambda: self.delete_coffee(selected_items))
            self.context_menu.addAction(delete_coffee_action)

        self.context_menu.exec(global_pos)

    def add_coffee(self):
        self.addCoffeeForm = AddEditCoffeeSHOP(self)
        self.addCoffeeForm.show()

    def edit_coffee(self, coffee_id):
        self.editCoffeeForm = AddEditCoffeeSHOP(self, coffee_id)
        self.editCoffeeForm.show()

    def delete_coffee(self, items: [QTableWidgetItem]):
        selected_ids = ", ".join(set([self.tableWidget.item(item.row(), 0).text() for item in items]))
        confirmation = QMessageBox.question(self, "Подтверждение",
                                            "Вы уверены, что хотите удалить выбранные элементы?",
                                            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel, )
        if confirmation == QMessageBox.StandardButton.Ok:
            self.cur.execute(f"""DELETE FROM Coffee WHERE id IN ({selected_ids});""")
            self.con.commit()
            self.update_table()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    shop = TurkishCoffeeMakerSHOP()
    shop.show()
    sys.exit(app.exec())
