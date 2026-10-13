from database import add_plant
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)


class AddPlantDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Add Plant")
        self.setFixedWidth(400)

        self.create_form()

    def create_form(self):

        main_layout = QVBoxLayout()

        #--------------title------------------

        title = QLabel("🌱 Add New Plant")

        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #31572c;
        """)

        main_layout.addWidget(title)

        main_layout.addSpacing(15)

        #---------------form---------------------

        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Example: Monstera")

        self.species_input = QLineEdit()
        self.species_input.setPlaceholderText(
            "Example: Monstera deliciosa"
        )

        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText(
            "Example: Bedroom"
        )

        self.interval_input = QSpinBox()
        self.interval_input.setMinimum(1)
        self.interval_input.setMaximum(365)
        self.interval_input.setValue(7)

        form_layout.addRow(
            "Plant Name:",
            self.name_input
        )

        form_layout.addRow(
            "Species:",
            self.species_input
        )

        form_layout.addRow(
            "Location:",
            self.location_input
        )

        form_layout.addRow(
            "Water Every:",
            self.interval_input
        )

        main_layout.addLayout(form_layout)

        main_layout.addWidget(
            QLabel("days")
        )

        main_layout.addSpacing(15)

        #-------------------buttons-------------------

        buttons_layout = QHBoxLayout()

        cancel_button = QPushButton("Cancel")
        save_button = QPushButton("Save Plant")

        cancel_button.clicked.connect(
            self.reject
        )

        save_button.clicked.connect(
            self.save_plant
        )

        save_button.setStyleSheet("""
            QPushButton {
                background-color: #31572c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
            }

            QPushButton:hover {
                background-color: #4f772d;
            }
        """)

        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(save_button)

        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

        #--------------------save plant-----------------

    def save_plant(self):

        plant_name = self.name_input.text().strip()
        species = self.species_input.text().strip()
        location = self.location_input.text().strip()
        watering_interval = self.interval_input.value()

        #--------------------validation------------------

        if not plant_name:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter the plant name."
            )
            return

        if not species:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter the species."
            )
            return

        if not location:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter the location."
            )
            return

        try:
            add_plant(
                plant_name=plant_name,
                species=species,
                location=location,
                watering_interval=watering_interval
            )

            QMessageBox.information(
                self,
                "Success",
                f"{plant_name} was successfully added!"
            )

            self.accept()

        except Exception as error:  # noqa: BLE001
            QMessageBox.critical(
                self,
                "Save Error",
                f"Could not save the plant.\n\n{error}"
            )