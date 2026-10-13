import json
import os
from datetime import date, datetime, timedelta

# Auto-detect data file location: supports both flat structure and 01_Source_Code/02_Data structure
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PARENT_DIR = os.path.dirname(_CURRENT_DIR)
_DATA_FOLDER_CANDIDATE = os.path.join(_PARENT_DIR, "02_Data", "plantcare_data.json")
_LOCAL_CANDIDATE = os.path.join(_CURRENT_DIR, "plantcare_data.json")

if os.path.exists(_DATA_FOLDER_CANDIDATE):
    DATA_FILE = _DATA_FOLDER_CANDIDATE
elif os.path.exists(_LOCAL_CANDIDATE):
    DATA_FILE = _LOCAL_CANDIDATE
elif os.path.isdir(os.path.join(_PARENT_DIR, "02_Data")):
    DATA_FILE = _DATA_FOLDER_CANDIDATE
else:
    DATA_FILE = _LOCAL_CANDIDATE


def _parse_date(val):
    """Convert an ISO date string or date object to a datetime.date object."""
    if not val:
        return None
    if isinstance(val, date):
        return val
    try:
        return date.fromisoformat(str(val)[:10])
    except Exception:  # noqa: BLE001
        return None


def _format_date(val):
    """Convert a date or datetime object to an ISO format string (YYYY-MM-DD)."""
    if not val:
        return None
    if isinstance(val, (date, datetime)):
        return val.isoformat()[:10]
    return str(val)


def _get_default_data():
    """Default starter data if no JSON file exists."""
    today = date.today()
    return {
        "plants": [
            {
                "plant_id": 1,
                "plant_name": "Monstera",
                "species": "Monstera deliciosa",
                "location": "Living Room",
                "watering_interval": 7,
                "last_watered": (today - timedelta(days=3)).isoformat(),
                "condition_status": "Healthy"
            },
            {
                "plant_id": 2,
                "plant_name": "Snake Plant",
                "species": "Sansevieria trifasciata",
                "location": "Bedroom",
                "watering_interval": 14,
                "last_watered": (today - timedelta(days=14)).isoformat(),
                "condition_status": "Healthy"
            },
            {
                "plant_id": 3,
                "plant_name": "Peace Lily",
                "species": "Spathiphyllum",
                "location": "Office",
                "watering_interval": 5,
                "last_watered": (today - timedelta(days=7)).isoformat(),
                "condition_status": "Good"
            },
            {
                "plant_id": 4,
                "plant_name": "Fiddle Leaf Fig",
                "species": "Ficus lyrata",
                "location": "Balcony",
                "watering_interval": 10,
                "last_watered": (today - timedelta(days=1)).isoformat(),
                "condition_status": "Healthy"
            }
        ],
        "history": [
            {
                "history_id": 1,
                "plant_id": 3,
                "action_type": "Watered",
                "action_date": (today - timedelta(days=7)).isoformat()
            },
            {
                "history_id": 2,
                "plant_id": 1,
                "action_type": "Watered",
                "action_date": (today - timedelta(days=3)).isoformat()
            },
            {
                "history_id": 3,
                "plant_id": 4,
                "action_type": "Watered",
                "action_date": (today - timedelta(days=1)).isoformat()
            }
        ]
    }


def load_data():
    """Load plants and history from the JSON file."""
    if not os.path.exists(DATA_FILE):
        data = _get_default_data()
        save_data(data)
        return data

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                data = {"plants": [], "history": []}
            data.setdefault("plants", [])
            data.setdefault("history", [])
            return data
    except Exception as error:  # noqa: BLE001
        print(f"Error loading JSON data from {DATA_FILE}: {error}")
        return {"plants": [], "history": []}


def save_data(data):
    """Save plants and history to the JSON file."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as error:
        print(f"Error saving JSON data to {DATA_FILE}: {error}")
        raise


def get_all_plants():
    """
    Returns list of tuples matching existing plant structure:
    (plant_id, plant_name, species, location, watering_interval, last_watered, condition_status)
    """
    data = load_data()
    plants = []
    for p in sorted(data.get("plants", []), key=lambda x: x.get("plant_id", 0)):
        plants.append((
            p.get("plant_id"),
            p.get("plant_name", ""),
            p.get("species", ""),
            p.get("location", ""),
            p.get("watering_interval", 7),
            _parse_date(p.get("last_watered")),
            p.get("condition_status", "Healthy")
        ))
    return plants


def get_dashboard_stats():
    """Calculate summary statistics for dashboard cards."""
    data = load_data()
    plants = data.get("plants", [])
    total_plants = len(plants)
    water_today = 0
    overdue = 0
    healthy = 0
    today = date.today()

    for p in plants:
        watering_interval = p.get("watering_interval")
        last_watered = _parse_date(p.get("last_watered"))
        condition = p.get("condition_status", "")

        if last_watered and watering_interval:
            next_watering = last_watered + timedelta(days=watering_interval)
            if next_watering == today:
                water_today += 1
            elif next_watering < today:
                overdue += 1
        elif not last_watered:
            water_today += 1

        if condition and condition.lower() in ["healthy", "good"]:
            healthy += 1

    return {
        "total": total_plants,
        "water_today": water_today,
        "overdue": overdue,
        "healthy": healthy
    }


def add_plant(plant_name, species, location, watering_interval, condition_status="Healthy"):
    """Add a new plant to JSON storage."""
    data = load_data()
    plants = data.get("plants", [])
    existing_ids = [p.get("plant_id", 0) for p in plants]
    next_id = max(existing_ids, default=0) + 1

    new_plant = {
        "plant_id": next_id,
        "plant_name": plant_name,
        "species": species,
        "location": location,
        "watering_interval": int(watering_interval),
        "last_watered": None,
        "condition_status": condition_status or "Healthy"
    }
    plants.append(new_plant)
    data["plants"] = plants
    save_data(data)
    return next_id


def update_plant(plant_id, plant_name, species, location, watering_interval):
    """Update an existing plant's details in JSON storage."""
    data = load_data()
    found = False
    for p in data.get("plants", []):
        if p.get("plant_id") == plant_id:
            p["plant_name"] = plant_name
            p["species"] = species
            p["location"] = location
            p["watering_interval"] = int(watering_interval)
            found = True
            break

    if not found:
        raise ValueError(f"Plant with ID {plant_id} not found.")

    save_data(data)


def delete_plant(plant_id):
    """Delete a plant and its associated care history from JSON storage."""
    data = load_data()
    data["plants"] = [p for p in data.get("plants", []) if p.get("plant_id") != plant_id]
    data["history"] = [h for h in data.get("history", []) if h.get("plant_id") != plant_id]
    save_data(data)


def mark_as_watered(plant_id):
    """Mark a plant as watered today and record a history entry."""
    data = load_data()
    today = date.today()
    today_str = today.isoformat()

    plant_found = False
    for p in data.get("plants", []):
        if p.get("plant_id") == plant_id:
            p["last_watered"] = today_str
            plant_found = True
            break

    if not plant_found:
        raise ValueError(f"Plant with ID {plant_id} not found.")

    history = data.get("history", [])
    existing_hids = [h.get("history_id", 0) for h in history]
    next_hid = max(existing_hids, default=0) + 1

    history.append({
        "history_id": next_hid,
        "plant_id": plant_id,
        "action_type": "Watered",
        "action_date": today_str
    })
    data["history"] = history
    save_data(data)


def get_care_history():
    """
    Returns list of tuples: (plant_name, action_type, action_date, location)
    sorted by action_date descending, history_id descending.
    """
    data = load_data()
    plant_map = {p.get("plant_id"): p for p in data.get("plants", [])}
    history_records = []

    for h in data.get("history", []):
        pid = h.get("plant_id")
        p = plant_map.get(pid, {})
        plant_name = p.get("plant_name", f"Plant #{pid}")
        location = p.get("location", "")
        action_type = h.get("action_type", "Watered")
        action_date = _parse_date(h.get("action_date"))
        history_id = h.get("history_id", 0)

        history_records.append({
            "plant_name": plant_name,
            "action_type": action_type,
            "action_date": action_date,
            "location": location,
            "history_id": history_id
        })

    # Sort descending by date, then history ID
    history_records.sort(
        key=lambda x: (
            x["action_date"] or date.min,
            x["history_id"]
        ),
        reverse=True
    )

    return [(r["plant_name"], r["action_type"], r["action_date"], r["location"]) for r in history_records]


def get_schedule_plants():
    """
    Returns list of tuples: (plant_id, plant_name, location, watering_interval, last_watered)
    for scheduling calculations.
    """
    data = load_data()
    schedule_list = []
    for p in sorted(data.get("plants", []), key=lambda x: x.get("plant_id", 0)):
        schedule_list.append((
            p.get("plant_id"),
            p.get("plant_name", ""),
            p.get("location", ""),
            p.get("watering_interval", 7),
            _parse_date(p.get("last_watered"))
        ))
    return schedule_list