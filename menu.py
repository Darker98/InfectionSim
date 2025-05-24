import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants for screen dimensions and colors
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 580  # Screen dimensions in pixels
BG_COLOR = (40, 40, 40)  # Background color (dark gray)
TEXT_COLOR = (230, 230, 230)  # Text color (light gray)
HIGHLIGHT_COLOR = (255, 215, 0)  # Highlight color (gold), unused here but defined
INPUT_BG_COLOR = (70, 70, 70)  # Input field background color (darker gray)
INPUT_ACTIVE_COLOR = (100, 100, 150)  # Active input field color (bluish gray)
ERROR_COLOR = (200, 50, 50)  # Error message color (red)
FONT = pygame.font.SysFont(None, 28)  # Default font for input text, size 28
LABEL_FONT = pygame.font.SysFont(None, 24)  # Default font for labels, size 24
ERROR_FONT = pygame.font.SysFont(None, 22)  # Default font for error messages, size 22
MAX_INPUT_LENGTH = 12  # Maximum characters allowed in input fields

def show_menu(last_settings=None):
    # Set up the display window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Simulation Menu")  # Window title

    # Default simulation parameter values
    defaults = {
        "Agents": "25000",  # Number of agents
        "Initial Infected": "1",  # Initial infected agents
        "Tick Speed (FPS)": "64",  # Simulation speed in frames per second
        "Infection Probability": "0.8",  # Chance of infection (0 to 1)
        "Infection Radius": "5.0",  # Radius for infection spread
        "Reinfection Probability": "0.02",  # Chance of reinfection (0 to 1)
        "Pixel Size": "4",  # Size of each heatmap pixel
    }

    # Initialize input fields with defaults or last settings
    input_fields = {}
    for key, default_val in defaults.items():
        setting_key = key.lower().replace(" ", "_")  # Convert to lowercase and replace spaces with underscores
        if last_settings and setting_key in last_settings:  # Use previous settings if provided
            val = last_settings[setting_key]
            input_fields[key] = {"value": str(val)}
        else:
            input_fields[key] = {"value": default_val}  # Use default value

    keys = list(input_fields.keys())  # List of input field names
    selected_index = 0  # Index of the currently selected field

    # Set up clock and cursor for blinking effect
    clock = pygame.time.Clock()  # Controls frame rate
    cursor_visible = True  # Toggles cursor visibility
    cursor_counter = 0  # Counter for cursor blinking timing

    # Define input field rectangles for display
    input_rects = []
    start_x_label = 50  # X position for labels
    start_x_input = 300  # X position for input boxes
    box_width, box_height = 200, 32  # Input box dimensions
    start_y = 50  # Starting Y position for fields
    spacing_y = 50  # Vertical spacing between fields

    for i in range(len(keys)):
        # Create a rectangle for each input field
        rect = pygame.Rect(start_x_input, start_y + i * spacing_y - 6, box_width, box_height)
        input_rects.append(rect)

    error_message = ""  # Holds error messages to display

    def draw():
        nonlocal cursor_visible  # Allow modification of outer scope variable
        screen.fill(BG_COLOR)  # Fill screen with background color

        # Draw each label and input field
        for i, key in enumerate(keys):
            y = start_y + i * spacing_y  # Calculate Y position
            # Render and display the label
            label_surface = LABEL_FONT.render(key, True, TEXT_COLOR)
            screen.blit(label_surface, (start_x_label, y))

            rect = input_rects[i]  # Get the input field's rectangle
            # Draw input box with different color if selected
            if i == selected_index:
                pygame.draw.rect(screen, INPUT_ACTIVE_COLOR, rect, border_radius=4)
            else:
                pygame.draw.rect(screen, INPUT_BG_COLOR, rect, border_radius=4)

            val = input_fields[key]["value"]  # Get current input value
            display_text = val[-MAX_INPUT_LENGTH:]  # Truncate to max length
            text_surface = FONT.render(display_text, True, TEXT_COLOR)
            screen.blit(text_surface, (rect.x + 8, rect.y + 4))  # Draw text inside box

            # Draw blinking cursor if field is selected
            if i == selected_index and cursor_visible:
                cursor_x = rect.x + 8 + text_surface.get_width() + 2  # Position after text
                cursor_y = rect.y + 6  # Vertical position
                cursor_height = FONT.get_height()  # Cursor height matches font
                pygame.draw.line(screen, TEXT_COLOR, (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_height), 2)

        # Display error message if present
        if error_message:
            error_surface = ERROR_FONT.render(error_message, True, ERROR_COLOR)
            screen.blit(error_surface, (start_x_label, SCREEN_HEIGHT - 180))

        # Display user instructions
        instructions = [
            "ENTER = Start simulation",
            "UP/DOWN = Select field",
            "Type to edit",
            "Backspace = Delete character",
            "ESC = Quit",
        ]
        for i, line in enumerate(instructions):
            instr_surface = LABEL_FONT.render(line, True, (180, 180, 180))  # Lighter gray for instructions
            screen.blit(instr_surface, (20, SCREEN_HEIGHT - 140 + i * 25))

        pygame.display.flip()  # Update the screen

    running = True
    while running:
        cursor_counter += 1
        # Toggle cursor visibility every 30 frames
        if cursor_counter >= 30:
            cursor_visible = not cursor_visible
            cursor_counter = 0

        draw()  # Redraw the menu

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Window close button
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:  # Keyboard input
                if event.key == pygame.K_ESCAPE:  # Exit on ESC
                    pygame.quit()
                    sys.exit()

                elif event.key == pygame.K_RETURN:  # Start simulation on Enter
                    try:
                        # Convert input values to appropriate types
                        agents = int(input_fields["Agents"]["value"])
                        initial_infected = int(input_fields["Initial Infected"]["value"])
                        tick_speed = float(input_fields["Tick Speed (FPS)"]["value"])
                        infection_probability = float(input_fields["Infection Probability"]["value"])
                        infection_radius = float(input_fields["Infection Radius"]["value"])
                        reinfection_probability = float(input_fields["Reinfection Probability"]["value"])
                        pixel_size = int(input_fields["Pixel Size"]["value"])

                        # Validate inputs and set error messages
                        if agents <= 0:
                            error_message = "Number of agents must be greater than 0."
                            continue
                        if initial_infected <= 0 or initial_infected >= agents:
                            error_message = "Initial infected must be > 0 and < number of agents."
                            continue
                        if tick_speed <= 0 or tick_speed >= 144:
                            error_message = "Tick speed must be > 0 and < 144."
                            continue
                        if not (0 < infection_probability <= 1):
                            error_message = "Infection probability must be between 0 and 1."
                            continue
                        if infection_radius <= 0 or infection_radius >= 100:
                            error_message = "Infection radius must be > 0 and < 100."
                            continue
                        if not (0 <= reinfection_probability <= 1):
                            error_message = "Reinfection probability must be >= 0 and < 1."
                            continue
                        if pixel_size <= 0 or pixel_size > 10:
                            error_message = "Pixel size must be > 0 and < 10."
                            continue

                        # Return validated settings if all checks pass
                        return {
                            "agents": agents,
                            "initial_infected": initial_infected,
                            "tick_speed": tick_speed,
                            "infection_probability": infection_probability,
                            "infection_radius": infection_radius,
                            "reinfection_probability": reinfection_probability,
                            "pixel_size": pixel_size,
                        }

                    except ValueError:  # Handle non-numeric input
                        error_message = "All inputs must be numeric."
                        continue

                elif event.key == pygame.K_BACKSPACE:  # Delete last character
                    val = input_fields[keys[selected_index]]["value"]
                    input_fields[keys[selected_index]]["value"] = val[:-1]

                elif event.key == pygame.K_UP:  # Move selection up
                    selected_index = (selected_index - 1) % len(keys)

                elif event.key == pygame.K_DOWN:  # Move selection down
                    selected_index = (selected_index + 1) % len(keys)

                else:  # Handle typing
                    if event.unicode.isprintable():  # Only printable characters
                        val = input_fields[keys[selected_index]]["value"]
                        if len(val) < MAX_INPUT_LENGTH:  # Respect max length
                            input_fields[keys[selected_index]]["value"] += event.unicode

        clock.tick(30)  # Cap frame rate at 30 FPS