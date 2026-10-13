import sys

from dashboard import Dashboard
from PySide6.QtWidgets import QApplication

app = QApplication(sys.argv)

window = Dashboard()
window.show()

sys.exit(app.exec())