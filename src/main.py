from menu import show_menu
from simulation import run_simulation

if __name__ == "__main__":
    last_settings = None  # Start with no last config, so defaults show first time

    while True:
        settings = show_menu(last_settings)  # Pass last_settings for persistence
        if settings is None:
            break  # Allow quitting from the menu

        last_settings = settings  # Save current config to pass back next time
        run_simulation(settings)
