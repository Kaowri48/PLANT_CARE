from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class SettingsWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "PlantCare - Settings"
        )

        self.resize(700, 500)

        self.setMinimumSize(
            600,
            400
        )

        self.create_ui()

    # =========================
    # CREATE USER INTERFACE
    # =========================

    def create_ui(self):

        layout = QVBoxLayout()

        layout.setContentsMargins(
            35,
            30,
            35,
            30
        )

        layout.setSpacing(20)

        # =========================
        # TITLE
        # =========================

        title = QLabel(
            "⚙ Settings"
        )

        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #31572c;
        """)

        layout.addWidget(
            title
        )

        subtitle = QLabel(
            "Manage your PlantCare preferences."
        )

        subtitle.setStyleSheet("""
            font-size: 15px;
            color: #666666;
        """)

        layout.addWidget(
            subtitle
        )

        layout.addSpacing(10)

        # =========================
        # APPLICATION
        # =========================

        application_frame = QFrame()

        application_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 10px;
            }
        """)

        application_layout = QVBoxLayout()

        application_layout.setContentsMargins(
            20,
            18,
            20,
            18
        )

        application_title = QLabel(
            "Application"
        )

        application_title.setStyleSheet("""
            font-size: 19px;
            font-weight: bold;
            color: #31572c;
        """)

        application_layout.addWidget(
            application_title
        )

        version = QLabel(
            "PlantCare v1.0"
        )

        version.setStyleSheet("""
            font-size: 15px;
            color: #333333;
        """)

        application_layout.addWidget(
            version
        )

        application_name = QLabel(
            "Plant Care Management System"
        )

        application_name.setStyleSheet("""
            font-size: 14px;
            color: #666666;
        """)

        application_layout.addWidget(
            application_name
        )

        application_frame.setLayout(
            application_layout
        )

        layout.addWidget(
            application_frame
        )

        # =========================
        # ABOUT
        # =========================

        about_frame = QFrame()

        about_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 10px;
            }
        """)

        about_layout = QVBoxLayout()

        about_layout.setContentsMargins(
            20,
            18,
            20,
            18
        )

        about_title = QLabel(
            "About PlantCare"
        )

        about_title.setStyleSheet("""
            font-size: 19px;
            font-weight: bold;
            color: #31572c;
        """)

        about_layout.addWidget(
            about_title
        )

        about_text = QLabel(
            "PlantCare helps you manage your plants, "
            "watering schedule, and care history "
            "in one place."
        )

        about_text.setWordWrap(
            True
        )

        about_text.setStyleSheet("""
            font-size: 14px;
            color: #666666;
        """)

        about_layout.addWidget(
            about_text
        )

        about_frame.setLayout(
            about_layout
        )

        layout.addWidget(
            about_frame
        )

        layout.addStretch()

        self.setLayout(
            layout
        )