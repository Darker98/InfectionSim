import glfw
from OpenGL.GL import *
import numpy as np
import random
import math
import time

# Define agent states
SUSCEPTIBLE, INFECTED, RECOVERED = 0, 1, 2

# Screen dimensions for main and graph windows
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
GRAPH_WIDTH, GRAPH_HEIGHT = 800, 300
RECOVERY_TICKS = (30, 100)  # Range for recovery time in ticks

class Agent:
    def __init__(self, screen_width, screen_height):
        # Initialize agent with random position within screen bounds
        self.pos = np.array([random.uniform(0, screen_width), random.uniform(0, screen_height)], dtype=np.float32)
        # Initialize velocity with small random values
        self.vel = np.random.uniform(-0.2, 0.2, size=2).astype(np.float32)
        # Start as susceptible
        self.state = SUSCEPTIBLE
        self.infection_time = 0
        self.recovery_time = 0

    def update(self):
        # Update position based on velocity
        self.pos += self.vel
        # Bounce off walls if position exceeds screen limits
        for i in range(2):
            limit = SCREEN_WIDTH if i == 0 else SCREEN_HEIGHT
            if self.pos[i] <= 0 or self.pos[i] >= limit:
                self.vel[i] *= -1
                self.pos[i] = max(0, min(self.pos[i], limit))

    def infect(self, tick, reinfected=False):
        # Set state to infected and record infection time
        self.state = INFECTED
        self.infection_time = tick
        # Calculate recovery time based on random range
        base_time = random.randint(*RECOVERY_TICKS)
        self.recovery_time = int(base_time)

    def recover(self):
        # Set state to recovered
        self.state = RECOVERED

class SpatialGrid:
    def __init__(self, cell_size=5):
        # Initialize grid with given cell size for spatial partitioning
        self.cell_size = cell_size
        self.grid = {}

    def clear(self):
        # Clear the grid dictionary for the next update
        self.grid.clear()

    def hash(self, pos):
        # Compute grid cell coordinates for a given position
        return int(pos[0] // self.cell_size), int(pos[1] // self.cell_size)

    def insert(self, agent):
        # Insert agent into the appropriate grid cell based on position
        key = self.hash(agent.pos)
        self.grid.setdefault(key, []).append(agent)

    def query(self, pos):
        # Retrieve all agents in the neighboring cells around a position
        cx, cy = self.hash(pos)
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                neighbors += self.grid.get((cx + dx, cy + dy), [])
        return neighbors

def draw_line(data, color, max_y, total_points):
    # Set color for the line in the graph
    glColor3f(*color)
    glBegin(GL_LINE_STRIP)
    for i, y in enumerate(data[-total_points:]):
        # Normalize x and y coordinates for OpenGL rendering
        x_norm = i / total_points
        y_norm = y / max_y if max_y > 0 else 0
        glVertex2f(x_norm * 2 - 1, y_norm * 2 - 1)
    glEnd()

def run_simulation(config):
    # Extract simulation parameters from config dictionary
    NUM_AGENTS = config["agents"]
    INITIAL_INFECTED = config["initial_infected"]
    TICK_INTERVAL = 1.0 / config["tick_speed"]
    INFECTION_RADIUS = config["infection_radius"]
    BASE_INFECTION_PROB = config["infection_probability"]
    REINFECT_MODIFIER = config["reinfection_probability"]
    DECAY_RATE = 0.5  # Rate at which infection probability decays with distance
    PIXEL_SIZE = config["pixel_size"]
    GRID_WIDTH = SCREEN_WIDTH // PIXEL_SIZE
    GRID_HEIGHT = SCREEN_HEIGHT // PIXEL_SIZE

    # Initialize global counters for agent states
    global INFECTED_COUNT, RECOVERED_COUNT, SUSCEPTIBLE_COUNT
    INFECTED_COUNT = INITIAL_INFECTED
    RECOVERED_COUNT = 0
    SUSCEPTIBLE_COUNT = NUM_AGENTS - INITIAL_INFECTED

    # Create list of agents with initial conditions
    agents = [Agent(SCREEN_WIDTH, SCREEN_HEIGHT) for _ in range(NUM_AGENTS)]
    # Randomly infect the initial set of agents
    for i in random.sample(range(NUM_AGENTS), INITIAL_INFECTED):
        agents[i].infect(0)

    # Initialize spatial grid for efficient neighbor queries and heatmap array
    grid = SpatialGrid(INFECTION_RADIUS)
    heatmap = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=np.float32)
    history_sus, history_inf, history_rec = [], [], []  # History for graphing

    # Initialize GLFW library
    if not glfw.init():
        raise Exception("GLFW initialization failed")

    # Create windows
    main_window = glfw.create_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Infection Heatmap", None, None)
    graph_window = glfw.create_window(GRAPH_WIDTH, GRAPH_HEIGHT, "Infection Graph", None, main_window)

    if not main_window or not graph_window:
        glfw.terminate()
        raise Exception("Window creation failed")

    # Set up OpenGL context for the main window
    glfw.make_context_current(main_window)
    glClearColor(0, 0, 0, 1)  # Black background

    tick = 0  # Simulation tick counter
    last_time = time.time()  # Time of last tick

    frame_count = 0  # Frame counter for FPS calculation
    frame_timer = time.time()  # Timer for FPS reset

    # Main simulation loop
    while not glfw.window_should_close(main_window) and not glfw.window_should_close(graph_window):
        now = time.time()

        # Count frames every loop iteration
        frame_count += 1

        # Print FPS every second and reset counter
        if now - frame_timer >= 1.0:
            # print(f"FPS: {frame_count}")
            frame_count = 0
            frame_timer = now

        # Wait for the next tick based on interval
        if now - last_time < TICK_INTERVAL:
            glfw.poll_events()
            continue
        last_time = now
        tick += 1

        # Update agents and rebuild spatial grid
        grid.clear()
        for a in agents:
            a.update()
            grid.insert(a)

        # Process infections and recoveries
        for a in agents:
            if a.state == INFECTED:
                if tick - a.infection_time >= a.recovery_time:
                    # Agent recovers if recovery time is reached
                    RECOVERED_COUNT += 1
                    INFECTED_COUNT -= 1
                    a.recover()
                else:
                    # Check nearby agents for potential infection
                    for b in grid.query(a.pos):
                        if a is b or b.state == INFECTED:
                            continue
                        dist = np.linalg.norm(a.pos - b.pos)
                        if dist <= INFECTION_RADIUS:
                            # Calculate infection probability based on distance
                            p = BASE_INFECTION_PROB * math.exp(-DECAY_RATE * dist) if b.state == SUSCEPTIBLE else REINFECT_MODIFIER * math.exp(-DECAY_RATE * dist)
                            if random.random() < p:
                                if b.state == RECOVERED:
                                    RECOVERED_COUNT -= 1
                                if b.state == SUSCEPTIBLE:
                                    SUSCEPTIBLE_COUNT -= 1
                                INFECTED_COUNT += 1
                                b.infect(tick, reinfected=(b.state == RECOVERED))

        # Record state counts for graphing
        history_sus.append(SUSCEPTIBLE_COUNT)
        history_inf.append(INFECTED_COUNT)
        history_rec.append(RECOVERED_COUNT)

        # Update heatmap with decay and agent contributions
        heatmap[:] *= 0.975  # Decay heatmap intensity
        for a in agents:
            x = int(a.pos[0] / SCREEN_WIDTH * GRID_WIDTH)
            y = int(a.pos[1] / SCREEN_HEIGHT * GRID_HEIGHT)
            if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                if a.state == INFECTED:
                    heatmap[y][x] += 1.0 / math.sqrt(NUM_AGENTS)
                elif a.state == RECOVERED:
                    heatmap[y][x] -= 1.0 / math.sqrt(NUM_AGENTS)

        # Render heatmap in the main window
        glfw.make_context_current(main_window)
        glClear(GL_COLOR_BUFFER_BIT)
        glRasterPos2f(-1, -1)
        np.clip(heatmap, 0, None, out=heatmap)  # Ensure non-negative values
        normalized = np.log1p(heatmap) / np.log1p(np.max(heatmap) + 1e-5)  # Normalize for display
        rgb = np.zeros((GRID_HEIGHT, GRID_WIDTH, 3), dtype=np.uint8)
        rgb[..., 0] = (normalized * 255).astype(np.uint8)  # Red channel for intensity
        texture = rgb.repeat(PIXEL_SIZE, axis=0).repeat(PIXEL_SIZE, axis=1)
        glDrawPixels(SCREEN_WIDTH, SCREEN_HEIGHT, GL_RGB, GL_UNSIGNED_BYTE, texture)
        glfw.swap_buffers(main_window)

        # Render graph in the second window
        glfw.make_context_current(graph_window)
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        max_y = NUM_AGENTS  # Max value for y-axis
        max_points = GRAPH_WIDTH  # Number of points to display

        # Draw lines for susceptible, infected, and recovered counts
        draw_line(history_sus, (0.2, 0.6, 1.0), max_y, max_points)  # Blue
        draw_line(history_inf, (1.0, 0.2, 0.2), max_y, max_points)  # Red
        draw_line(history_rec, (0.2, 1.0, 0.2), max_y, max_points)  # Green
        glfw.swap_buffers(graph_window)

        # Handle window events and update title with stats
        glfw.poll_events()
        glfw.set_window_title(main_window, f"Infected: {INFECTED_COUNT}, Recovered: {RECOVERED_COUNT}")

    # Clean up GLFW resources
    glfw.terminate()