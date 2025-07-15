# F1 Race Strategy Simulator

This project is an F1 race strategy simulator written in Python. It models tire degradation, pit stops, and lap times to help find the best tire strategy for a race given user inputs like total laps, track temperature, driver aggression, and track wetness.

---

## Features

- Simulates realistic tire degradation based on track temperature, driver aggression, and wetness.
- Calculates lap times with non-linear degradation.
- Considers pit stop time penalties when changing tire compounds.
- Explores all valid strategy combinations with 1 to 3 stints to find the fastest overall race strategy.
- Interactive dashboard using Streamlit for easy user input and real-time visualization of lap times.
- Supports three tire compounds: soft, medium, and hard.
- Outputs total race time in a human-readable format (hours, minutes, seconds).

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/EnCroissant12/f1-strategy-simulator.git
cd f1-strategy-simulator
