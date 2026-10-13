from database import update_plant
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)


class EditPlantDialog(QDialog):
    def __init__(self, plant, parent=None):
        super().__init__(parent)

        self.plant = plant

        self.setWindowTitle("Edit Plant")
        self.setMinimumWidth(350)

        layout = QVBoxLayout()
        form = QFormLayout()

        #plant name
        self.name_input = QLineEdit()
        self.name_input.setText(plant[1])
        form.addRow("Plant Name:", self.name_input)

        #species
        self.species_input = QLineEdit()
        self.species_input.setText(plant[2])
        form.addRow("Species:", self.species_input)

        #location
        self.location_input = QLineEdit()
        self.location_input.setText(plant[3])
        form.addRow("Location:", self.location_input)

        #watering interval
        self.water_input = QSpinBox()
        self.water_input.setMinimum(1)
        self.water_input.setMaximum(365)

        if len(plant) > 4 and plant[4]:
            self.water_input.setValue(plant[4])
        else:
            self.water_input.setValue(7)

        form.addRow("Water Every (days):", self.water_input)

        layout.addLayout(form)

        #save button
        save_button = QPushButton("Save Changes")
        save_button.clicked.connect(self.save_plant)

        #cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        layout.addWidget(save_button)
        layout.addWidget(cancel_button)

        self.setLayout(layout)

    def save_plant(self):
        plant_id = self.plant[0]

        plant_name = self.name_input.text().strip()
        species = self.species_input.text().strip()
        location = self.location_input.text().strip()
        watering_interval = self.water_input.value()

        if not plant_name:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter a plant name."
            )
            return

        try:
            update_plant(
                plant_id=plant_id,
                plant_name=plant_name,
                species=species,
                location=location,
                watering_interval=watering_interval,
            )

            QMessageBox.information(
                self,
                "Success",
                f"{plant_name} was successfully updated!"
            )

            self.accept()

        except Exception as error:  # noqa: BLE001
            QMessageBox.critical(
                self,
                "Save Error",
                f"Could not update the plant.\n\n{error}"
            )