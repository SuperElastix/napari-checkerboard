from qtpy.QtWidgets import QMessageBox


def error(message):
    e = QMessageBox()
    label = QMessageBox()
    e.setText(message)
    e.setIcon(QMessageBox.Critical)
    e.setWindowTitle("Error")
    e.show()
    return e
