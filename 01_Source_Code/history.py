from datetime import date

from database import get_care_history
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class HistoryWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PlantCare - Care History")
        self.resize(960, 640)
        self.setMinimumSize(780, 520)

        self.all_history_data = []
        self.current_filter = "all"

        self.create_ui()
        self.load_history()

   #--------------create user interface------------------

    def create_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(32, 28, 32, 26)
        main_layout.setSpacing(18)

        #--------------header bar------------------
        header_layout = QHBoxLayout()
        header_layout.setSpacing(14)

        header_text_layout = QVBoxLayout()
        header_text_layout.setSpacing(3)

        title = QLabel("Care History 📋")
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: 800;
            color: #15371c;
        """)

        subtitle = QLabel("Chronological care activity log and historical records.")
        subtitle.setStyleSheet("""
            font-size: 13px;
            color: #64748b;
        """)

        header_text_layout.addWidget(title)
        header_text_layout.addWidget(subtitle)
        header_layout.addLayout(header_text_layout)

        header_layout.addStretch()

        #refresg button
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
        refresh_btn.clicked.connect(self.load_history)
        header_layout.addWidget(refresh_btn)

        main_layout.addLayout(header_layout)

        #--------------stoolbar------------------
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(12)

        #search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Search history by plant or location...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setFixedWidth(290)
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
        self.search_input.textChanged.connect(self.filter_history)
        toolbar_layout.addWidget(self.search_input)

        #filter pills
        self.filter_buttons = {}
        filters_spec = [
            ("all", "All Activities"),
            ("watered", "💧 Watered"),
        ]

        for key, label_text in filters_spec:
            btn = QPushButton(label_text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, f=key: self.set_filter(f))
            self.filter_buttons[key] = btn
            toolbar_layout.addWidget(btn)

        self.update_filter_button_styles()

        toolbar_layout.addStretch()

        self.history_count_badge = QLabel("0 records")
        self.history_count_badge.setStyleSheet("""
            background-color: #e2ece3;
            color: #24582f;
            border-radius: 10px;
            padding: 5px 12px;
            font-size: 11px;
            font-weight: 700;
        """)
        toolbar_layout.addWidget(self.history_count_badge)

        main_layout.addLayout(toolbar_layout)

        #--------------table container------------------
        table_card = QFrame()
        table_card.setStyleSheet("""
            QFrame#historyTableCard {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        table_card.setObjectName("historyTableCard")

        table_card_layout = QVBoxLayout()
        table_card_layout.setContentsMargins(1, 1, 1, 1)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Plant",
            "Action Type",
            "Care Date",
            "Location",
        ])

        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(48)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

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

    #--------------filter ocntrols------------------

    def set_filter(self, filter_key):
        self.current_filter = filter_key
        self.update_filter_button_styles()
        self.filter_history()

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

    #--------------load history------------------

    def load_history(self):
        try:
            history = get_care_history()

            self.all_history_data = []
            for record in history:
                self.all_history_data.append({
                    "plant_name": record[0],
                    "action_type": record[1],
                    "action_date": record[2],
                    "location": record[3],
                })

            self.filter_history()

        except Exception as error:  # noqa: BLE001
            print("Error loading history:", error)

    #--------------filter and render history------------------

    def filter_history(self):
        query = self.search_input.text().strip().lower()

        filtered = []
        for item in self.all_history_data:
            name_lower = (item["plant_name"] or "").lower()
            loc_lower = (item["location"] or "").lower()
            act_lower = (item["action_type"] or "").lower()

            if query and not (query in name_lower or query in loc_lower or query in act_lower):
                continue

            if self.current_filter == "watered" and "water" not in act_lower:
                continue

            filtered.append(item)

        self.history_count_badge.setText(f"{len(filtered)} / {len(self.all_history_data)} entries")
        self.render_table(filtered)

       #--------------render table------------------

    def render_table(self, items):
        self.table.setRowCount(len(items))

        if not items:
            return

        today = date.today()

        for row, record in enumerate(items):
            plant_name = record["plant_name"]
            action_type = record["action_type"]
            action_date = record["action_date"]
            location = record["location"]

            #plant name with icon
            nl = (plant_name or "").lower()
            icon = "🌸" if "orchid" in nl else ("🌿" if any(k in nl for k in ["snake", "monstera", "pothos"]) else "🌱")
            name_item = QTableWidgetItem(f"{icon}  {plant_name}")
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            font = name_item.font()
            font.setBold(True)
            name_item.setFont(font)
            self.table.setItem(row, 0, name_item)

            #action badge
            action_cell = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(6, 4, 6, 4)
            action_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            act_str = action_type or "Care"
            act_label = "💧 Watered" if "water" in act_str.lower() else f"🌱 {act_str}"
            act_badge = QLabel(act_label)
            act_badge.setStyleSheet("""
                background-color: #e0f2fe;
                color: #0369a1;
                border: 1px solid #bae6fd;
                border-radius: 10px;
                padding: 3px 10px;
                font-size: 11px;
                font-weight: 700;
            """)
            action_layout.addWidget(act_badge)
            action_cell.setLayout(action_layout)
            self.table.setCellWidget(row, 1, action_cell)

            #date formatting
            if action_date:
                if action_date == today:
                    date_str = "Today"
                else:
                    date_str = action_date.strftime("%b %d, %Y")
            else:
                date_str = "—"
            date_item = QTableWidgetItem(date_str)
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 2, date_item)

            #location formatting
            loc_text = f"📍 {location}" if location else "Home"
            loc_item = QTableWidgetItem(loc_text)
            loc_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(row, 3, loc_item)