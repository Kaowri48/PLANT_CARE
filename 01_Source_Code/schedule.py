from datetime import date, timedelta

from database import get_schedule_plants, mark_as_watered
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ScheduleWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PlantCare - Watering Schedule")
        self.resize(960, 640)
        self.setMinimumSize(780, 520)

        self.all_schedule_data = []
        self.current_filter = "all"

        self.create_ui()
        self.load_schedule()


    def create_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(32, 28, 32, 26)
        main_layout.setSpacing(18)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(14)

        header_text_layout = QVBoxLayout()
        header_text_layout.setSpacing(3)

        title = QLabel("Watering Schedule 📅")
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: 800;
            color: #15371c;
        """)

        subtitle = QLabel("Upcoming hydration deadlines and care forecasts for your collection.")
        subtitle.setStyleSheet("""
            font-size: 13px;
            color: #64748b;
        """)

        header_text_layout.addWidget(title)
        header_text_layout.addWidget(subtitle)
        header_layout.addLayout(header_text_layout)

        header_layout.addStretch()

        # Date Chip
        today_formatted = date.today().strftime("%a, %b %d, %Y")
        date_chip = QLabel(f"📅  {today_formatted}")
        date_chip.setFixedHeight(36)
        date_chip.setStyleSheet("""
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 18px;
            padding: 0px 16px;
            font-size: 12px;
            font-weight: 600;
            color: #475569;
        """)
        header_layout.addWidget(date_chip)

        # Refresh button
        refresh_btn = QPushButton("↻ Refresh")
        refresh_btn.setFixedHeight(36)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #334155;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 0px 14px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
                border-color: #64748b;
                color: #0f172a;
            }
            QPushButton:pressed {
                background-color: #e2e8f0;
            }
        """)
        refresh_btn.clicked.connect(self.load_schedule)
        header_layout.addWidget(refresh_btn)

        main_layout.addLayout(header_layout)

        # -------------------------
        # TOOLBAR (SEARCH & FILTERS)
        # -------------------------
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(12)

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Filter by plant or location...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setFixedWidth(280)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 7px 12px;
                font-size: 13px;
                color: #1e293b;
            }
            QLineEdit:hover {
                border: 1px solid #94a3b8;
            }
            QLineEdit:focus {
                border: 1px solid #2d6a4f;
                background-color: #ffffff;
            }
        """)
        self.search_input.textChanged.connect(self.filter_schedule)
        toolbar_layout.addWidget(self.search_input)

        # Filter Pills
        self.filter_buttons = {}
        filters_spec = [
            ("all", "All"),
            ("today", "💧 Due Today"),
            ("overdue", "⚠️ Overdue"),
            ("upcoming", "✓ Upcoming"),
        ]

        for key, label_text in filters_spec:
            btn = QPushButton(label_text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, f=key: self.set_filter(f))
            self.filter_buttons[key] = btn
            toolbar_layout.addWidget(btn)

        self.update_filter_button_styles()

        toolbar_layout.addStretch()

        self.summary_badge = QLabel("0 plants scheduled")
        self.summary_badge.setStyleSheet("""
            background-color: #e2ece3;
            color: #24582f;
            border-radius: 10px;
            padding: 5px 12px;
            font-size: 11px;
            font-weight: 700;
        """)
        toolbar_layout.addWidget(self.summary_badge)

        main_layout.addLayout(toolbar_layout)

        # -------------------------
        # SCHEDULE TABLE CONTAINER
        # -------------------------
        table_card = QFrame()
        table_card.setStyleSheet("""
            QFrame#tableCard {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        table_card.setObjectName("tableCard")

        table_card_layout = QVBoxLayout()
        table_card_layout.setContentsMargins(1, 1, 1, 1)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Plant",
            "Location",
            "Last Watered",
            "Next Watering",
            "Status",
            "Action",
        ])

        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(48)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(4, 145)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(5, 115)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: none;
                border-radius: 12px;
                font-size: 13px;
                color: #1e293b;
            }
            QHeaderView::section {
                background-color: #17361e;
                color: #ffffff;
                padding: 12px 14px;
                font-weight: 700;
                font-size: 12px;
                border: none;
                letter-spacing: 0.5px;
            }
            QTableWidget::item {
                padding: 10px 14px;
                border-bottom: 1px solid #f1f5f9;
            }
            QTableWidget::item:selected {
                background-color: #ecfdf5;
                color: #166534;
            }
            QScrollBar:vertical {
                border: none;
                background: #edf2ed;
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                min-height: 25px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        table_card_layout.addWidget(self.table)
        table_card.setLayout(table_card_layout)

        main_layout.addWidget(table_card)
        self.setLayout(main_layout)

    # =========================
    # FILTER CONTROLS
    # =========================

    def set_filter(self, filter_key):
        self.current_filter = filter_key
        self.update_filter_button_styles()
        self.filter_schedule()

    def update_filter_button_styles(self):
        for key, btn in self.filter_buttons.items():
            if key == self.current_filter:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #245e35;
                        color: #ffffff;
                        border: 1px solid #245e35;
                        border-radius: 7px;
                        padding: 6px 14px;
                        font-size: 12px;
                        font-weight: 700;
                    }
                    QPushButton:hover {
                        background-color: #1a4526;
                        border-color: #1a4526;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #ffffff;
                        color: #475569;
                        border: 1px solid #cbd5e1;
                        border-radius: 7px;
                        padding: 6px 14px;
                        font-size: 12px;
                        font-weight: 600;
                    }
                    QPushButton:hover {
                        background-color: #f1f5f9;
                        color: #1e293b;
                        border-color: #94a3b8;
                    }
                """)

#--------------load schedule------------------

    def load_schedule(self):
        try:
            plants = get_schedule_plants()
            today = date.today()

            self.all_schedule_data = []

            for plant in plants:
                plant_id = plant[0]
                plant_name = plant[1]
                location = plant[2]
                watering_interval = plant[3]
                last_watered = plant[4]

                if last_watered and watering_interval:
                    next_watering = last_watered + timedelta(days=watering_interval)
                    days_diff = (next_watering - today).days

                    if days_diff < 0:
                        status = "Overdue"
                        status_type = "overdue"
                        days_over = abs(days_diff)
                        status_text = f"⚠️ Overdue ({days_over}d)"
                    elif days_diff == 0:
                        status = "Due Today"
                        status_type = "today"
                        status_text = "💧 Due Today"
                    elif days_diff == 1:
                        status = "Upcoming"
                        status_type = "upcoming"
                        status_text = "💧 Due Tomorrow"
                    else:
                        status = "Upcoming"
                        status_type = "upcoming"
                        status_text = f"💧 In {days_diff} days"
                else:
                    next_watering = None
                    status = "Not Watered"
                    status_type = "today"
                    status_text = "💧 Needs Initial Water"

                self.all_schedule_data.append({
                    "plant_id": plant_id,
                    "plant_name": plant_name,
                    "location": location,
                    "last_watered": last_watered,
                    "next_watering": next_watering,
                    "status": status,
                    "status_type": status_type,
                    "status_text": status_text,
                })

            #sorting by urgency
            self.all_schedule_data.sort(
                key=lambda p: (
                    p["next_watering"] is None,
                    p["next_watering"] or date.max,
                )
            )

            self.filter_schedule()

        except Exception as error:  # noqa: BLE001
            print("Error loading schedule:", error)

    #--------------filter and render schedule------------------

    def filter_schedule(self):
        query = self.search_input.text().strip().lower()

        filtered = []
        for item in self.all_schedule_data:
            name_lower = (item["plant_name"] or "").lower()
            loc_lower = (item["location"] or "").lower()

            if query and not (query in name_lower or query in loc_lower):
                continue

            if self.current_filter == "today" and item["status_type"] != "today":
                continue
            if self.current_filter == "overdue" and item["status_type"] != "overdue":
                continue
            if self.current_filter == "upcoming" and item["status_type"] != "upcoming":
                continue

            filtered.append(item)

        self.summary_badge.setText(f"{len(filtered)} / {len(self.all_schedule_data)} plants")
        self.render_table(filtered)

    #--------------render table------------------

    def render_table(self, items):
        self.table.setRowCount(len(items))

        if not items:
            return

        today = date.today()

        for row, data in enumerate(items):
            plant_id = data["plant_id"]
            plant_name = data["plant_name"]
            location = data["location"]
            last_watered = data["last_watered"]
            next_watering = data["next_watering"]
            status_type = data["status_type"]
            status_text = data["status_text"]

            #plant name
            nl = (plant_name or "").lower()
            icon = "🌸" if "orchid" in nl else ("🌿" if any(k in nl for k in ["snake", "monstera", "pothos"]) else "🌱")
            name_item = QTableWidgetItem(f"{icon}  {plant_name}")
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            font = name_item.font()
            font.setBold(True)
            name_item.setFont(font)
            self.table.setItem(row, 0, name_item)

            #location
            loc_text = f"📍 {location}" if location else "Home"
            loc_item = QTableWidgetItem(loc_text)
            loc_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(row, 1, loc_item)

            #last watered
            if last_watered:
                if last_watered == today:
                    last_watered_str = "Today"
                else:
                    last_watered_str = last_watered.strftime("%b %d, %Y")
            else:
                last_watered_str = "Never"
            last_item = QTableWidgetItem(last_watered_str)
            last_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 2, last_item)

            #next watering
            if next_watering:
                next_str = next_watering.strftime("%b %d, %Y")
            else:
                next_str = "—"
            next_item = QTableWidgetItem(next_str)
            next_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, next_item)

            #status badge
            status_cell = QWidget()
            status_layout = QHBoxLayout()
            status_layout.setContentsMargins(6, 4, 6, 4)
            status_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            badge = QLabel(status_text)
            if status_type == "overdue":
                badge.setStyleSheet("""
                    background-color: #fee2e2;
                    color: #b91c1c;
                    border: 1px solid #fecaca;
                    border-radius: 10px;
                    padding: 3px 10px;
                    font-size: 11px;
                    font-weight: 700;
                """)
            elif status_type == "today":
                badge.setStyleSheet("""
                    background-color: #e0f2fe;
                    color: #0369a1;
                    border: 1px solid #bae6fd;
                    border-radius: 10px;
                    padding: 3px 10px;
                    font-size: 11px;
                    font-weight: 700;
                """)
            else:
                badge.setStyleSheet("""
                    background-color: #dcfce7;
                    color: #15803d;
                    border: 1px solid #bbf7d0;
                    border-radius: 10px;
                    padding: 3px 10px;
                    font-size: 11px;
                    font-weight: 600;
                """)

            status_layout.addWidget(badge)
            status_cell.setLayout(status_layout)
            self.table.setCellWidget(row, 4, status_cell)

            #action btn
            action_cell = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(6, 4, 6, 4)
            action_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            if last_watered == today:
                water_btn = QPushButton("✓ Watered")
                water_btn.setEnabled(False)
                water_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f1f5f9;
                        color: #64748b;
                        border: 1px solid #e2e8f0;
                        border-radius: 6px;
                        padding: 4px 10px;
                        font-size: 11px;
                        font-weight: 600;
                    }
                """)
            else:
                water_btn = QPushButton("💧 Water")
                water_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                water_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #245e35;
                        color: #ffffff;
                        border: none;
                        border-radius: 6px;
                        padding: 4px 10px;
                        font-size: 11px;
                        font-weight: 700;
                    }
                    QPushButton:hover {
                        background-color: #184224;
                    }
                    QPushButton:pressed {
                        background-color: #102d18;
                    }
                """)
                water_btn.clicked.connect(
                    lambda checked=False, pid=plant_id: self.quick_water(pid)
                )

            action_layout.addWidget(water_btn)
            action_cell.setLayout(action_layout)
            self.table.setCellWidget(row, 5, action_cell)

    #--------------quick water------------------

    def quick_water(self, plant_id):
        try:
            mark_as_watered(plant_id)

            QMessageBox.information(
                self,
                "Plant Watered",
                "Watering registered successfully!",
            )

            self.load_schedule()

        except Exception as error:  # noqa: BLE001
            QMessageBox.critical(
                self,
                "Error",
                f"Could not record watering.\n\n{error}",
            )