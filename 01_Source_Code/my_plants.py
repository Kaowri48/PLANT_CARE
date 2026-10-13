from datetime import date, timedelta

from add_plant import AddPlantDialog
from database import delete_plant, mark_as_watered
from edit_plant import EditPlantDialog
from plants import get_all_plants
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class MyPlantsWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PlantCare - My Plants")
        self.resize(960, 640)
        self.setMinimumSize(780, 520)

        self.all_plants_cache = []
        self.current_filter = "all"

        self.create_ui()
        self.load_plants()

    #--------------create uyser interface------------------

    def create_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(32, 28, 32, 26)
        main_layout.setSpacing(18)

        #--------------header bar------------------
        header_layout = QHBoxLayout()
        header_layout.setSpacing(14)

        header_text_layout = QVBoxLayout()
        header_text_layout.setSpacing(3)

        title = QLabel("My Plants 🌱")
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: 800;
            color: #15371c;
        """)

        subtitle = QLabel("Manage, monitor, and care for all registered botanical specimens.")
        subtitle.setStyleSheet("""
            font-size: 13px;
            color: #64748b;
        """)

        header_text_layout.addWidget(title)
        header_text_layout.addWidget(subtitle)
        header_layout.addLayout(header_text_layout)

        header_layout.addStretch()

        #plant count
        self.plant_count_badge = QLabel("0 plants")
        self.plant_count_badge.setFixedHeight(36)
        self.plant_count_badge.setStyleSheet("""
            background-color: #e2ece3;
            color: #24582f;
            border-radius: 18px;
            padding: 0px 16px;
            font-size: 12px;
            font-weight: 700;
        """)
        header_layout.addWidget(self.plant_count_badge)

        #add plant button
        add_button = QPushButton("+ Add Plant")
        add_button.setFixedHeight(36)
        add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #245e35;
                color: #ffffff;
                border: none;
                padding: 0px 18px;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #1a4526;
            }
            QPushButton:pressed {
                background-color: #14351d;
            }
        """)
        add_button.clicked.connect(self.open_add_plant)
        header_layout.addWidget(add_button)

        main_layout.addLayout(header_layout)

        #--------------tool bar------------------
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(12)

        #search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Search by name, species, location...")
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
        self.search_input.textChanged.connect(self.filter_plants)
        toolbar_layout.addWidget(self.search_input)

        #filter pills 
        self.filter_buttons = {}

        filters_spec = [
            ("all", "All"),
            ("water_today", "💧 Water Today"),
            ("overdue", "⚠️ Overdue"),
            ("healthy", "✨ Healthy"),
        ]

        for key, label_text in filters_spec:
            btn = QPushButton(label_text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, f=key: self.set_filter(f))
            self.filter_buttons[key] = btn
            toolbar_layout.addWidget(btn)

        self.update_filter_button_styles()

        toolbar_layout.addStretch()
        main_layout.addLayout(toolbar_layout)

        #--------------scroll------------------
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
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

        self.plants_container = QWidget()
        self.plants_container.setStyleSheet("background-color: transparent;")

        self.plants_layout = QVBoxLayout()
        self.plants_layout.setContentsMargins(0, 4, 4, 10)
        self.plants_layout.setSpacing(10)

        self.plants_container.setLayout(self.plants_layout)
        self.scroll_area.setWidget(self.plants_container)

        main_layout.addWidget(self.scroll_area)
        self.setLayout(main_layout)

    #--------------filter controls------------------

    def set_filter(self, filter_key):
        self.current_filter = filter_key
        self.update_filter_button_styles()
        self.filter_plants()

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

    #--------------load plants------------------

    def load_plants(self):
        self.all_plants_cache = get_all_plants() or []
        self.plant_count_badge.setText(f"{len(self.all_plants_cache)} plants")
        self.filter_plants()

    #--------------filter and render------------------

    def filter_plants(self):
        query = self.search_input.text().strip().lower()
        today = date.today()

        while self.plants_layout.count():
            item = self.plants_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        filtered = []

        for plant in self.all_plants_cache:
            plant_name = (plant[1] or "").lower()
            species = (plant[2] or "").lower()
            location = (plant[3] or "").lower()
            watering_interval = plant[4] if len(plant) > 4 else None
            last_watered = plant[5] if len(plant) > 5 else None
            condition = (plant[6] or "").lower() if len(plant) > 6 else ""

            if query and not (query in plant_name or query in species or query in location):
                continue

            is_water_today = False
            is_overdue = False

            if last_watered and watering_interval:
                next_watering = last_watered + timedelta(days=watering_interval)
                if next_watering == today:
                    is_water_today = True
                elif next_watering < today:
                    is_overdue = True
            elif not last_watered:
                is_water_today = True

            is_healthy = condition in ["healthy", "good"]

            if self.current_filter == "water_today" and not is_water_today:
                continue
            if self.current_filter == "overdue" and not is_overdue:
                continue
            if self.current_filter == "healthy" and not is_healthy:
                continue

            filtered.append(plant)

        if not filtered:
            self.render_empty_state()
            return

        for plant in filtered:
            self.render_plant_card(plant, today)

        self.plants_layout.addStretch()

    #--------------empty state------------------

    def render_empty_state(self):
        empty_frame = QFrame()
        empty_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 2px dashed #d1d5db;
                border-radius: 14px;
                padding: 35px 20px;
            }
            QLabel {
                border: none;
                background: transparent;
            }
        """)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)

        icon = QLabel("🌱")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 38px;")

        title = QLabel("No plants found")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #334155;")

        if self.search_input.text().strip():
            msg = f"No plants match '{self.search_input.text().strip()}'."
        elif self.current_filter != "all":
            msg = f"No plants match the '{self.current_filter.replace('_', ' ').title()}' filter."
        else:
            msg = "No plants in your collection yet. Start adding plants to keep track of their care!"

        subtitle = QLabel(msg)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 13px; color: #64748b;")

        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(subtitle)

        if not self.all_plants_cache:
            add_now_btn = QPushButton("+ Add First Plant")
            add_now_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            add_now_btn.setStyleSheet("""
                QPushButton {
                    background-color: #245e35;
                    color: white;
                    border: none;
                    padding: 8px 18px;
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: 700;
                    margin-top: 10px;
                }
                QPushButton:hover {
                    background-color: #1a4526;
                }
            """)
            add_now_btn.clicked.connect(self.open_add_plant)
            layout.addWidget(add_now_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        empty_frame.setLayout(layout)
        self.plants_layout.addWidget(empty_frame)

    #--------------render plant card------------------

    def render_plant_card(self, plant, today):
        plant_id = plant[0]
        plant_name = plant[1]
        species = plant[2]
        location = plant[3]
        watering_interval = plant[4] if len(plant) > 4 else None
        last_watered = plant[5] if len(plant) > 5 else None
        condition = plant[6] if len(plant) > 6 else None

        plant_card = QFrame()
        plant_card.setObjectName("plantCard")
        plant_card.setStyleSheet("""
            QFrame#plantCard {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
            QFrame#plantCard:hover {
                border: 1px solid #86efac;
                background-color: #fcfffd;
            }
            QFrame#plantCard QLabel {
                border: none;
                background: transparent;
            }
        """)

        card_layout = QHBoxLayout()
        card_layout.setContentsMargins(18, 14, 18, 14)
        card_layout.setSpacing(16)

        #avatar
        name_lower = (plant_name or "").lower()
        species_lower = (species or "").lower()

        if any(w in name_lower or w in species_lower for w in ["orchid", "flower", "rose"]):
            avatar_emoji = "🌸"
            avatar_bg = "#fdf2f8"
        elif any(w in name_lower or w in species_lower for w in ["cactus", "succulent", "aloe"]):
            avatar_emoji = "🌵"
            avatar_bg = "#fefce8"
        elif any(w in name_lower or w in species_lower for w in ["snake", "fern", "ivy", "monstera", "pothos", "philodendron", "ficus", "palm"]):
            avatar_emoji = "🌿"
            avatar_bg = "#ecfdf5"
        else:
            avatar_emoji = "🌱"
            avatar_bg = "#eef7ee"

        avatar_label = QLabel(avatar_emoji)
        avatar_label.setFixedSize(48, 48)
        avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_label.setStyleSheet(f"""
            background-color: {avatar_bg};
            border: 1px solid rgba(0, 0, 0, 0.05);
            border-radius: 10px;
            font-size: 24px;
        """)
        card_layout.addWidget(avatar_label)

        #details
        details_layout = QVBoxLayout()
        details_layout.setSpacing(4)

        #name and status
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        name_label = QLabel(plant_name)
        name_label.setStyleSheet("""
            font-size: 16px;
            font-weight: 700;
            color: #17361e;
        """)
        top_row.addWidget(name_label)

        #watering status badge
        water_badge = QLabel()
        if last_watered and watering_interval:
            next_water_date = last_watered + timedelta(days=watering_interval)
            days_diff = (next_water_date - today).days

            if days_diff < 0:
                days_over = abs(days_diff)
                water_badge.setText(f"⚠️ Overdue ({days_over}d)")
                water_badge.setStyleSheet("""
                    background-color: #fee2e2;
                    color: #b91c1c;
                    border: 1px solid #fecaca;
                    border-radius: 11px;
                    padding: 2px 9px;
                    font-size: 11px;
                    font-weight: 700;
                """)
            elif days_diff == 0:
                water_badge.setText("💧 Water Today")
                water_badge.setStyleSheet("""
                    background-color: #e0f2fe;
                    color: #0369a1;
                    border: 1px solid #bae6fd;
                    border-radius: 11px;
                    padding: 2px 9px;
                    font-size: 11px;
                    font-weight: 700;
                """)
            elif days_diff == 1:
                water_badge.setText("💧 Due Tomorrow")
                water_badge.setStyleSheet("""
                    background-color: #f1f5f9;
                    color: #475569;
                    border-radius: 11px;
                    padding: 2px 9px;
                    font-size: 11px;
                    font-weight: 600;
                """)
            else:
                water_badge.setText(f"💧 Due in {days_diff}d ({next_water_date.strftime('%b %d')})")
                water_badge.setStyleSheet("""
                    background-color: #f1f5f9;
                    color: #475569;
                    border-radius: 11px;
                    padding: 2px 9px;
                    font-size: 11px;
                    font-weight: 600;
                """)
        elif not last_watered:
            water_badge.setText("💧 Needs Initial Water")
            water_badge.setStyleSheet("""
                background-color: #fef3c7;
                color: #b45309;
                border: 1px solid #fde68a;
                border-radius: 11px;
                padding: 2px 9px;
                font-size: 11px;
                font-weight: 700;
            """)
        else:
            water_badge.setText("💧 Schedule Unset")
            water_badge.setStyleSheet("""
                background-color: #f1f5f9;
                color: #64748b;
                border-radius: 11px;
                padding: 2px 9px;
                font-size: 11px;
            """)
        top_row.addWidget(water_badge)

        #condtion
        if condition:
            cond_badge = QLabel()
            cond_lower = condition.lower()
            if cond_lower in ["healthy", "good"]:
                cond_badge.setText(f"✓ {condition.title()}")
                cond_badge.setStyleSheet("""
                    background-color: #dcfce7;
                    color: #15803d;
                    border-radius: 11px;
                    padding: 2px 9px;
                    font-size: 11px;
                    font-weight: 700;
                """)
            else:
                cond_badge.setText(f"⚠️ {condition.title()}")
                cond_badge.setStyleSheet("""
                    background-color: #fef3c7;
                    color: #b45309;
                    border-radius: 11px;
                    padding: 2px 9px;
                    font-size: 11px;
                    font-weight: 600;
                """)
            top_row.addWidget(cond_badge)

        top_row.addStretch()
        details_layout.addLayout(top_row)

        #species location schedule
        meta_row = QHBoxLayout()
        meta_row.setSpacing(8)

        species_text = species if species else "Unspecified species"
        species_label = QLabel(f"<i>{species_text}</i>")
        species_label.setStyleSheet("color: #64748b; font-size: 13px;")

        dot1 = QLabel("•")
        dot1.setStyleSheet("color: #cbd5e1;")

        loc_text = location if location else "Home"
        loc_label = QLabel(f"📍 {loc_text}")
        loc_label.setStyleSheet("color: #475569; font-size: 13px;")

        dot2 = QLabel("•")
        dot2.setStyleSheet("color: #cbd5e1;")

        freq_days = watering_interval if watering_interval else "—"
        freq_label = QLabel(f"🔄 Every {freq_days} days")
        freq_label.setStyleSheet("color: #64748b; font-size: 13px;")

        meta_row.addWidget(species_label)
        meta_row.addWidget(dot1)
        meta_row.addWidget(loc_label)
        meta_row.addWidget(dot2)
        meta_row.addWidget(freq_label)
        meta_row.addStretch()
        details_layout.addLayout(meta_row)

        #last watered date
        if last_watered:
            last_watered_str = last_watered.strftime("%b %d, %Y")
            if last_watered == today:
                last_water_text = "💧 Watered today!"
            else:
                last_water_text = f"Last watered: {last_watered_str}"
        else:
            last_water_text = "Never watered yet"

        last_water_label = QLabel(last_water_text)
        last_water_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
        details_layout.addWidget(last_water_label)

        card_layout.addLayout(details_layout)
        card_layout.addStretch()

        #action btn
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)

        if last_watered == today:
            watered_button = QPushButton("✓ Watered Today")
            watered_button.setCursor(Qt.CursorShape.PointingHandCursor)
            watered_button.setStyleSheet("""
                QPushButton {
                    background-color: #e2f0d9;
                    color: #276738;
                    border: 1px solid #b8dfbe;
                    padding: 8px 14px;
                    border-radius: 8px;
                    font-weight: 700;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #245e35;
                    color: #ffffff;
                    border-color: #245e35;
                }
                QPushButton:pressed {
                    background-color: #1a4526;
                }
            """)
        else:
            watered_button = QPushButton("💧 Mark Watered")
            watered_button.setCursor(Qt.CursorShape.PointingHandCursor)
            watered_button.setStyleSheet("""
                QPushButton {
                    background-color: #245e35;
                    color: #ffffff;
                    border: none;
                    padding: 8px 14px;
                    border-radius: 8px;
                    font-weight: 700;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #184224;
                }
                QPushButton:pressed {
                    background-color: #102d18;
                }
            """)

        watered_button.clicked.connect(
            lambda checked=False, pid=plant_id: self.mark_as_watered(pid)
        )

        edit_button = QPushButton("✏️ Edit")
        edit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #334155;
                border: 1px solid #cbd5e1;
                padding: 8px 13px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 12px;
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
        edit_button.clicked.connect(
            lambda checked=False, p=plant: self.edit_plant(p)
        )

        delete_button = QPushButton("🗑️")
        delete_button.setToolTip("Delete Plant")
        delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #fff1f2;
                color: #e11d48;
                border: 1px solid #fecdd3;
                padding: 8px 12px;
                border-radius: 8px;
                font-weight: 700;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e11d48;
                color: #ffffff;
                border-color: #e11d48;
            }
            QPushButton:pressed {
                background-color: #be123c;
            }
        """)
        delete_button.clicked.connect(
            lambda checked=False, pid=plant_id: self.delete_plant(pid)
        )

        actions_layout.addWidget(watered_button)
        actions_layout.addWidget(edit_button)
        actions_layout.addWidget(delete_button)

        card_layout.addLayout(actions_layout)
        plant_card.setLayout(card_layout)
        self.plants_layout.addWidget(plant_card)

    #--------------add plant------------------

    def open_add_plant(self):
        dialog = AddPlantDialog(self)
        if dialog.exec():
            self.load_plants()

    #--------------mark as watered------------------

    def mark_as_watered(self, plant_id):
        try:
            mark_as_watered(plant_id)

            QMessageBox.information(
                self,
                "Plant Watered",
                "The plant has been marked as watered today.",
            )

            self.load_plants()

        except Exception as error:  # noqa: BLE001
            QMessageBox.critical(
                self,
                "Error",
                f"Could not update the plant.\n\n{error}",
            )

    #--------------edit------------------

    def edit_plant(self, plant):
        dialog = EditPlantDialog(plant, self)
        if dialog.exec():
            self.load_plants()

    #--------------delete plant------------------

    def delete_plant(self, plant_id):
        reply = QMessageBox.question(
            self,
            "Delete Plant",
            "Are you sure you want to delete this plant?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            delete_plant(plant_id)

            QMessageBox.information(
                self,
                "Plant Deleted",
                "The plant has been deleted.",
            )

            self.load_plants()

        except Exception as error:  # noqa: BLE001
            QMessageBox.critical(
                self,
                "Error",
                f"Could not delete the plant.\n\n{error}",
            )