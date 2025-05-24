
# 🦠 Infection Spread Heatmap Simulation

This project simulates the spread of an infectious disease using a proximity-based SIR model and visualizes it as a heatmap. Instead of tracking individual people or graph connections, the simulation focuses on infection **density** over time from a **top-down aerial view**, similar to how outbreaks are mapped in real-world epidemiology.

## 🌍 Concept

- Uniformly distributed agents across a 2D map.
- Slight Brownian motion to simulate interaction.
- Proximity-based infection: agents infect others within 5 meters.
- Infection probability decreases exponentially with distance.
- Agents recover after a random time.
- Recovered agents can be reinfected, but with lower probability.
- Heatmap shows infection **density**, not people.

## 🔧 Features

- ✅ Brownian motion (minimal movement)
- ✅ SIR model: Susceptible → Infected → Recovered
- ✅ Reinfection support
- ✅ Per-pixel infection heatmap (OpenGL GPU-accelerated)
- ✅ Custom-sized pixel grid (e.g., 200×150) rendered full-screen
- ✅ Real-time rendering using PyOpenGL + GLFW
- ✅ Scalable and optimized with spatial hashing
- ✅ Configurable menu for parameters (planned)

## 🖥️ Screenshot

You can include a screenshot like this (place image in the same directory):

```
![Simulation Screenshot](screenshot.png)
```

> ⚠️ Make sure the image file (e.g., `screenshot.png`) exists in the same folder as this README.

## ⚙️ Planned Menu Options

A configuration menu (or JSON config file) is being planned to allow easy customization of:
- Screen resolution
- Heatmap grid resolution
- Recovery time range
- Infection radius
- Reinfection rate
- Number of agents

## 🛠️ Requirements

- Python 3.11 or later
- [`numpy`](https://pypi.org/project/numpy/)
- [`PyOpenGL`](https://pypi.org/project/PyOpenGL/)
- [`PyGLFW`](https://pypi.org/project/glfw/)

Install dependencies:

```bash
pip install numpy PyOpenGL PyGLFW
```

## 🚀 Running the Simulation

```bash
python main_heatmap.py
```

The window will show a red heatmap, where:
- Light red = low infection density
- Bright red = high infection density

No individual agents are shown — only the infection spread as a visual.

## 🧠 Model Summary

| Parameter              | Value / Range             |
|------------------------|---------------------------|
| Infection Radius       | 5 meters                  |
| Base Infection Prob.   | 0.8                       |
| Distance Decay         | Exponential ($e^{-kd}$)   |
| Recovery Time          | 400–800 ticks             |
| Reinfection Modifier   | 0.2 (i.e., 20% chance)    |
| Agents                 | 500+ (adjustable)         |

## 📚 Report

For full technical details, see the accompanying LaTeX report:
[`infection_simulation_report.tex`](infection_simulation_report.tex)

## 📌 License

MIT License

---

This simulation was built for educational and academic use to model how infections spread in a proximity-based population using GPU-accelerated heatmap rendering.
