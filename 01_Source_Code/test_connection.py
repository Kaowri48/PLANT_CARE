
from database import (
    DATA_FILE,
    get_all_plants,
    get_care_history,
    get_dashboard_stats,
    load_data,
)

print("Checking JSON storage connection...")

try:
    data = load_data()
    plants = get_all_plants()
    history = get_care_history()
    stats = get_dashboard_stats()

    print("\n[SUCCESS] Connected to JSON storage!")
    print(f"Data file location: {DATA_FILE}")
    print(f"Total plants:       {len(plants)}")
    print(f"History entries:    {len(history)}")
    print(f"Dashboard stats:    {stats}")
    print("\nEverything is working properly with JSON!")

except Exception as error:  # noqa: BLE001
    print("\n[FAILURE] JSON storage check encountered an error:")
    print("Error:", error)