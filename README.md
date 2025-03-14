# Pi Blocks Simulation

A Python simulation that demonstrates pi can be calculated through elastic collisions between blocks of different masses.

## Overview

This project simulates a physics experiment where pi emerges from counting the number of collisions between two blocks. When a small block and a much larger block collide elastically, with the large block initially moving toward a wall, the number of total collisions approaches pi as the mass ratio increases.

The simulation uses precise fraction arithmetic to ensure accurate calculations and avoid floating-point errors.

## Inspiration

This simulation was inspired by videos by:

-   Matt Parker (Stand-up Maths): https://www.youtube.com/watch?v=vlUTlbZT4ig
-   3Blue1Brown: https://www.youtube.com/watch?v=HEfHFsfGXjs and https://www.youtube.com/watch?v=6dTyOl1fmDo

## Features

-   Real-time visualization of block collisions using PyGame
-   Precise fraction arithmetic for accurate calculations
-   Interactive controls to adjust simulation parameters:
    -   Block masses
    -   Simulation speed
    -   Numerical precision
-   Live display of collision count, pi approximation, and error percentage

## Requirements

-   Python 3.13+
-   PyGame 2.6.1+

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/pi-blocks-simulation.git
cd pi-blocks-simulation

# Install dependencies using uv
uv sync
```

## Usage

```bash
# Run the simulation
uv run simulation.py
```

### Controls

-   **SPACE**: Pause/Resume simulation
-   **R**: Reset simulation
-   **1/2**: Decrease/Increase first block mass
-   **3/4**: Decrease/Increase second block mass
-   **+/-**: Adjust simulation speed
-   **[/]**: Adjust fraction precision

## How It Works

The simulation models two blocks on a frictionless surface, with a wall on the left:

1. A small block (m1) starts stationary
2. A larger block (m2) starts moving left toward the small block
3. When blocks collide, they exchange momentum according to elastic collision physics
4. The simulation counts all collisions (block-block and block-wall)

As the mass ratio (m2/m1) increases, the total number of collisions approaches pi \* sqrt(m2/m1).
