from datetime import date, timedelta

from add_plant import AddPlantDialog
from database import delete_plant, mark_as_watered
from edit_plant import EditPlantDialog
from history import HistoryWindow
from my_plants import MyPlantsWindow
from plants import get_all_plants, get_dashboard_stats
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from schedule import ScheduleWindow
from settings import SettingsWindow

#--------------navigation------------------

NAV_ACTIVE_STYLE = """
    QPushButton {
        background-color: #24522d;
        color: #ffffff;
        border: none;
        border-left: 4px solid #4ade80;
        border-radius: 8px;
        padding: 11px 16px;
        text-align: left;
        font-size: 14px;
        font-weight: 700;
    }
    QPushButton:hover {
        background-color: #2d6137;
        color: #ffffff;
    }
"""

NAV_INACTIVE_STYLE = """
    QPushButton {
        background-color: transparent;
        color: #c9decb;
        border: none;
        border-radius: 8px;
        padding: 11px 16px;
        text-align: left;
        font-size: 14px;
        font-weight: 500;
    }
    QPushButton:hover {
        background-color: rgba(255, 255, 255, 0.12);
        color: #ffffff;
    }
"""


class Dashboard(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PlantCare - Manage Your Botanical Collection")
        self.resize(1140, 730)
        self.setMinimumSize(940, 620)

        #search and filter
        self.all_plants_cache = []
        self.current_filter = "all"
        self.current_nav_key = "dashboard"

        self.create_dashboard()
        self.load_dashboard_data()
        self.load_plants()

   #--------------dashboard------------------

    def create_dashboard(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        #--------------sidebar------------------
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setObjectName("sidebar")

        sidebar.setStyleSheet("""
            QFrame#sidebar {
                background-color: #17361e;
                border-right: 1px solid #102615;
            }

            QFrame#sidebar QLabel {
                border: none;
                background: transparent;
            }

            QLabel#logoTitle {
                color: #ffffff;
                font-size: 20px;
                font-weight: 800;
                letter-spacing: 0.5px;
            }

            QLabel#logoSubtitle {
                color: #8bb796;
                font-size: 11px;
                font-weight: 500;
            }
        """)

        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(18, 26, 18, 20)
        sidebar_layout.setSpacing(6)

        #logo header
        logo_box = QHBoxLayout()
        logo_box.setSpacing(12)

        logo_icon_box = QLabel("🌿")
        logo_icon_box.setFixedSize(40, 40)
        logo_icon_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_icon_box.setStyleSheet("""
            background-color: #24542d;
            border-radius: 10px;
            font-size: 20px;
        """)

        logo_text_layout = QVBoxLayout()
        logo_text_layout.setSpacing(1)

        logo_title = QLabel("PlantCare")
        logo_title.setObjectName("logoTitle")

        logo_sub = QLabel("Botanical Assistant")
        logo_sub.setObjectName("logoSubtitle")

        logo_text_layout.addWidget(logo_title)
        logo_text_layout.addWidget(logo_sub)

        logo_box.addWidget(logo_icon_box)
        logo_box.addLayout(logo_text_layout)
        sidebar_layout.addLayout(logo_box)

        sidebar_layout.addSpacing(28)

        #navigator cat label
        nav_label = QLabel("NAVIGATION")
        nav_label.setStyleSheet("""
            color: #659272;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
            padding-left: 6px;
            margin-bottom: 4px;
        """)
        sidebar_layout.addWidget(nav_label)

        #items
        self.dashboard_button = QPushButton("🏠   Dashboard")
        self.plants_button = QPushButton("🌱   My Plants")
        self.schedule_button = QPushButton("📅   Schedule")
        self.history_button = QPushButton("📋   Care History")
        self.settings_button = QPushButton("⚙️   Settings")

        self.nav_buttons = {
            "dashboard": self.dashboard_button,
            "plants": self.plants_button,
            "schedule": self.schedule_button,
            "history": self.history_button,
            "settings": self.settings_button,
        }

        for btn in self.nav_buttons.values():
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        sidebar_layout.addWidget(self.dashboard_button)
        sidebar_layout.addWidget(self.plants_button)
        sidebar_layout.addWidget(self.schedule_button)
        sidebar_layout.addWidget(self.history_button)
        sidebar_layout.addWidget(self.settings_button)

        #nav connections
        self.dashboard_button.clicked.connect(self.open_dashboard)
        self.plants_button.clicked.connect(self.open_my_plants)
        self.schedule_button.clicked.connect(self.open_schedule)
        self.history_button.clicked.connect(self.open_history)
        self.settings_button.clicked.connect(self.open_settings)

        self.update_nav_styles()

        sidebar_layout.addStretch()

        #bottom system card
        system_card = QFrame()
        system_card.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 0.24);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        system_card_layout = QVBoxLayout()
        system_card_layout.setContentsMargins(10, 10, 10, 10)
        system_card_layout.setSpacing(4)

        status_row = QHBoxLayout()
        status_row.setSpacing(6)
        status_dot = QLabel("●")
        status_dot.setStyleSheet("color: #4ade80; font-size: 11px;")
        status_text = QLabel("Connected")
        status_text.setStyleSheet("color: #d1e7dd; font-size: 11px; font-weight: 600;")
        status_row.addWidget(status_dot)
        status_row.addWidget(status_text)
        status_row.addStretch()

        version_label = QLabel("PlantCare Desktop v1.2")
        version_label.setStyleSheet("color: #799f83; font-size: 10px;")

        system_card_layout.addLayout(status_row)
        system_card_layout.addWidget(version_label)
        system_card.setLayout(system_card_layout)

        sidebar_layout.addWidget(system_card)
        sidebar.setLayout(sidebar_layout)

        #--------------main content------------------
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("""
            QStackedWidget {
                background-color: #f6f9f6;
            }
        """)

        #main dashboard
        self.dashboard_view = self.create_dashboard_view()
        self.stack.addWidget(self.dashboard_view)

        #my plants
        self.my_plants_page = MyPlantsWindow()
        self.stack.addWidget(self.my_plants_page)

        #schedule
        self.schedule_page = ScheduleWindow()
        self.stack.addWidget(self.schedule_page)

        #history
        self.history_page = HistoryWindow()
        self.stack.addWidget(self.history_page)

        #settings
        self.settings_page = SettingsWindow()
        self.stack.addWidget(self.settings_page)

        #assemble main
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)

    #--------------dashboard view------------------

    def create_dashboard_view(self):
        content = QWidget()
        content.setObjectName("contentArea")
        content.setStyleSheet("""
            QWidget#contentArea {
                background-color: #f6f9f6;
            }
            QWidget#contentArea QLabel {
                background: transparent;
            }
        """)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(32, 28, 32, 26)
        content_layout.setSpacing(18)

        #--------------header bar------------------
        header_layout = QHBoxLayout()
        header_layout.setSpacing(14)

        welcome_text_layout = QVBoxLayout()
        welcome_text_layout.setSpacing(3)

        welcome_title = QLabel("Dashboard Overview 🌿")
        welcome_title.setStyleSheet("""
            font-size: 26px;
            font-weight: 800;
            color: #15371c;
        """)

        subtitle = QLabel("Keep your botanical collection thriving with daily care insights.")
        subtitle.setStyleSheet("""
            font-size: 13px;
            color: #64748b;
        """)

        welcome_text_layout.addWidget(welcome_title)
        welcome_text_layout.addWidget(subtitle)
        header_layout.addLayout(welcome_text_layout)

        header_layout.addStretch()

        #date
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

        #refresh button
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
        refresh_btn.clicked.connect(self.refresh_all)
        header_layout.addWidget(refresh_btn)

        #add plant button
        add_header_button = QPushButton("+ Add Plant")
        add_header_button.setFixedHeight(36)
        add_header_button.setCursor(Qt.CursorShape.PointingHandCursor)
        add_header_button.setStyleSheet("""
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
        add_header_button.clicked.connect(self.open_add_plant)
        header_layout.addWidget(add_header_button)

        content_layout.addLayout(header_layout)

        #--------------statisticsss------------------
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(14)

        (
            total_card,
            self.total_number,
            self.total_sublabel,
        ) = self.create_card(
            icon="🌱",
            category="TOTAL PLANTS",
            initial_number="0",
            sublabel="Registered collection",
            icon_bg="#e8f5e9",
            accent_color="#1b4332",
        )

        (
            watering_card,
            self.water_number,
            self.water_sublabel,
        ) = self.create_card(
            icon="💧",
            category="WATER TODAY",
            initial_number="0",
            sublabel="Needs hydration",
            icon_bg="#e0f2fe",
            accent_color="#0284c7",
        )

        (
            overdue_card,
            self.overdue_number,
            self.overdue_sublabel,
        ) = self.create_card(
            icon="⚠️",
            category="OVERDUE",
            initial_number="0",
            sublabel="Past schedule",
            icon_bg="#fef2f2",
            accent_color="#dc2626",
        )

        (
            healthy_card,
            self.healthy_number,
            self.healthy_sublabel,
        ) = self.create_card(
            icon="✨",
            category="HEALTHY",
            initial_number="0",
            sublabel="In prime condition",
            icon_bg="#ecfdf5",
            accent_color="#16a34a",
        )

        cards_layout.addWidget(total_card)
        cards_layout.addWidget(watering_card)
        cards_layout.addWidget(overdue_card)
        cards_layout.addWidget(healthy_card)

        content_layout.addLayout(cards_layout)

        #--------------plant section------------------
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(12)

        #section with count
        title_box = QHBoxLayout()
        title_box.setSpacing(8)

        plants_section_title = QLabel("My Plants")
        plants_section_title.setStyleSheet("""
            font-size: 18px;
            font-weight: 800;
            color: #173b1f;
        """)

        self.plant_count_badge = QLabel("0 plants")
        self.plant_count_badge.setStyleSheet("""
            background-color: #e2ece3;
            color: #24582f;
            border-radius: 10px;
            padding: 3px 9px;
            font-size: 11px;
            font-weight: 700;
        """)

        title_box.addWidget(plants_section_title)
        title_box.addWidget(self.plant_count_badge)
        toolbar_layout.addLayout(title_box)

        toolbar_layout.addStretch()

        #--------------search bar------------------
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Search by name, species, location...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setFixedWidth(270)
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

        ##--------------filter pills------------------
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

        content_layout.addLayout(toolbar_layout)

        #--------------scroll plant------------------
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        scroll_area.setStyleSheet("""
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

        plants_container = QWidget()
        plants_container.setStyleSheet("background-color: transparent;")

        self.plants_layout = QVBoxLayout()
        self.plants_layout.setContentsMargins(0, 4, 4, 10)
        self.plants_layout.setSpacing(10)

        plants_container.setLayout(self.plants_layout)
        scroll_area.setWidget(plants_container)

        content_layout.addWidget(scroll_area)
        content.setLayout(content_layout)

        return content

    #--------------metric------------------

    def create_card(
        self,
        icon,
        category,
        initial_number,
        sublabel,
        icon_bg="#e8f5e9",
        accent_color="#1b4332",
    ):
        card = QFrame()
        card.setFixedHeight(116)
        card.setObjectName("metricCard")
        card.setStyleSheet("""
            QFrame#metricCard {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 14px;
            }
            QFrame#metricCard:hover {
                border: 1px solid #86efac;
                background-color: #fcfffc;
            }
            QFrame#metricCard QLabel {
                border: none;
                background: transparent;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(5)

        #icon badge and category title (top row)
        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        icon_label = QLabel(icon)
        icon_label.setFixedSize(36, 36)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"""
            background-color: {icon_bg};
            border-radius: 10px;
            font-size: 18px;
            border: none;
        """)

        category_label = QLabel(category)
        category_label.setStyleSheet("""
            font-size: 11px;
            font-weight: 700;
            color: #64748b;
            letter-spacing: 0.6px;
        """)

        top_row.addWidget(icon_label)
        top_row.addWidget(category_label)
        top_row.addStretch()

        #middle
        number_label = QLabel(initial_number)
        number_label.setStyleSheet(f"""
            font-size: 27px;
            font-weight: 800;
            color: {accent_color};
        """)

        #subtitle
        sub_label = QLabel(sublabel)
        sub_label.setStyleSheet("""
            font-size: 11px;
            color: #64748b;
            font-weight: 500;
        """)

        layout.addLayout(top_row)
        layout.addWidget(number_label)
        layout.addWidget(sub_label)

        card.setLayout(layout)
        return card, number_label, sub_label

   #--------------sidebar navigation------------------

    def navigate_to(self, key):
        nav_indexes = {
            "dashboard": 0,
            "plants": 1,
            "schedule": 2,
            "history": 3,
            "settings": 4,
        }

        if key not in nav_indexes:
            return

        self.current_nav_key = key
        self.update_nav_styles()
        self.stack.setCurrentIndex(nav_indexes[key])

        #refresh data
        if key == "dashboard":
            self.load_dashboard_data()
            self.load_plants()
        elif key == "plants":
            self.my_plants_page.load_plants()
        elif key == "schedule":
            self.schedule_page.load_schedule()
        elif key == "history":
            self.history_page.load_history()

    def update_nav_styles(self):
        for key, btn in self.nav_buttons.items():
            if key == self.current_nav_key:
                btn.setStyleSheet(NAV_ACTIVE_STYLE)
            else:
                btn.setStyleSheet(NAV_INACTIVE_STYLE)

    def open_dashboard(self):
        self.navigate_to("dashboard")

    def open_my_plants(self):
        self.navigate_to("plants")

    def open_schedule(self):
        self.navigate_to("schedule")

    def open_history(self):
        self.navigate_to("history")

    def open_settings(self):
        self.navigate_to("settings")

    #--------------filter control options------------------

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

    def refresh_all(self):
        self.load_dashboard_data()
        self.load_plants()

    #--------------load dashboard stasts------------------

    def load_dashboard_data(self):
        stats = get_dashboard_stats()

        total = stats.get("total", 0)
        water_today = stats.get("water_today", 0)
        overdue = stats.get("overdue", 0)
        healthy = stats.get("healthy", 0)

        self.total_number.setText(str(total))
        self.water_number.setText(str(water_today))
        self.overdue_number.setText(str(overdue))
        self.healthy_number.setText(str(healthy))

        #subtext badges
        if water_today > 0:
            self.water_sublabel.setText(f"{water_today} plant{'s' if water_today > 1 else ''} needs watering")
            self.water_sublabel.setStyleSheet("font-size: 11px; color: #0284c7; font-weight: 600;")
        else:
            self.water_sublabel.setText("All plants hydrated ✓")
            self.water_sublabel.setStyleSheet("font-size: 11px; color: #16a34a; font-weight: 600;")

        if overdue > 0:
            self.overdue_sublabel.setText(f"{overdue} plant{'s' if overdue > 1 else ''} overdue!")
            self.overdue_sublabel.setStyleSheet("font-size: 11px; color: #dc2626; font-weight: 700;")
        else:
            self.overdue_sublabel.setText("No overdue plants ✓")
            self.overdue_sublabel.setStyleSheet("font-size: 11px; color: #16a34a; font-weight: 600;")

        if total > 0:
            pct = int((healthy / total) * 100)
            self.healthy_sublabel.setText(f"{pct}% in good health")
        else:
            self.healthy_sublabel.setText("No plant data")

    #--------------load plants------------------

    def load_plants(self):
        self.all_plants_cache = get_all_plants() or []
        self.plant_count_badge.setText(f"{len(self.all_plants_cache)} plants")
        self.filter_plants()

    #--------------filter and render plants------------------

    def filter_plants(self):
        query = self.search_input.text().strip().lower()
        today = date.today()

        #Clear existing plant widgets in layout
        while self.plants_layout.count():
            item = self.plants_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        filtered = []

        for plant in self.all_plants_cache:
            #plant structure
            plant_name = (plant[1] or "").lower()
            species = (plant[2] or "").lower()
            location = (plant[3] or "").lower()
            watering_interval = plant[4] if len(plant) > 4 else None
            last_watered = plant[5] if len(plant) > 5 else None
            condition = (plant[6] or "").lower() if len(plant) > 6 else ""

            if query and not (query in plant_name or query in species or query in location):
                continue

            #calculate watering status
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

            #filter
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

        #render each plant card
        for plant in filtered:
            self.render_plant_card(plant, today)

        self.plants_layout.addStretch()

    #--------------render empty state------------------

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
            msg = f"No plants currently match the '{self.current_filter.replace('_', ' ').title()}' filter."
        else:
            msg = "Your botanical collection is empty. Start adding plants to track their schedule!"

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

    #--------------individual plant card------------------

    def render_plant_card(self, plant, today):
        plant_id = plant[0]
        plant_name = plant[1]
        species = plant[2]
        location = plant[3]
        watering_interval = plant[4] if len(plant) > 4 else None
        last_watered = plant[5] if len(plant) > 5 else None
        condition = plant[6] if len(plant) > 6 else None

        #container card
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

        #avatar plant container
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

        #plant information details
        details_layout = QVBoxLayout()
        details_layout.setSpacing(4)

        #name and status (top row)
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        name_label = QLabel(plant_name)
        name_label.setStyleSheet("""
            font-size: 16px;
            font-weight: 700;
            color: #17361e;
        """)
        top_row.addWidget(name_label)

        #watering Status
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

        #condition
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

        #species-location-schedule.intervarl
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

        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)

        #mark as watered
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

        #edit button
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

        #delete button
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
            self.load_dashboard_data()
            self.load_plants()
            if hasattr(self, "my_plants_page"):
                self.my_plants_page.load_plants()

    #--------------marks plant as watered------------------

    def mark_as_watered(self, plant_id):
        try:
            mark_as_watered(plant_id)

            QMessageBox.information(
                self,
                "Plant Watered",
                "The plant has been marked as watered today.",
            )

            self.load_dashboard_data()
            self.load_plants()
            if hasattr(self, "my_plants_page"):
                self.my_plants_page.load_plants()

        except Exception as error:  # noqa: BLE001
            QMessageBox.critical(
                self,
                "Error",
                f"Could not update watering information.\n\n{error}",
            )

    #--------------edit plant------------------

    def edit_plant(self, plant):
        dialog = EditPlantDialog(plant, self)

        if dialog.exec():
            self.load_dashboard_data()
            self.load_plants()
            if hasattr(self, "my_plants_page"):
                self.my_plants_page.load_plants()

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

            self.load_dashboard_data()
            self.load_plants()
            if hasattr(self, "my_plants_page"):
                self.my_plants_page.load_plants()

        except Exception as error:  # noqa: BLE001
            QMessageBox.critical(
                self,
                "Error",
                f"Could not delete the plant.\n\n{error}",
            )