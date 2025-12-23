# Tempus

A high-performance desktop application for visualizing large time-series datasets. Handles files with millions of rows smoothly using native rendering—no browser bottleneck.

## Features

- **Large Dataset Support**: Efficiently handles 500MB+ CSV files with millions of rows
- **Auto-Downsampling**: Maintains high FPS when zoomed out on large datasets
- **Layer Manager**: Toggle visibility, change colors, and adjust line width for each series
- **Smoothing**: Apply rolling average smoothing with adjustable window size
- **X-Axis Zoom**: Zoom on time axis while Y-axis auto-scales to show full data range
- **Dark Theme**: Modern, professional dark-themed interface
- **Crosshair**: Interactive crosshair with coordinate display

## Tech Stack

- **PyQt6** - Desktop GUI framework
- **pyqtgraph** - High-performance plotting (OpenGL-accelerated)
- **Pandas** - Data processing (with PyArrow backend for performance)
- **pyqtdarktheme** - Modern dark theme styling

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd tempus

# Install mise (if not already installed) and development tools (uv, ruff, ty)
# Note: Open a new shell after running if mise was newly installed
make mise

# Install project dependencies
uv sync
```

## Usage

```bash
# Run the desktop application
uv run tempus-desktop

# Or open a file directly
uv run tempus-desktop data/MessTemperatur_20251221.csv
```

### Controls

- **Mouse wheel**: Zoom X-axis (time)
- **Click + drag**: Pan the view
- **Ctrl+O**: Open CSV file
- **Ctrl+R**: Reset view to show all data
- **Ctrl+H**: Toggle crosshair
- **Ctrl+L**: Toggle layer manager panel

## Development Setup

### Development Tools

The following tools are managed by mise (see [mise.toml](mise.toml)):

- **uv** - Package manager
- **ruff** - Linting and formatting
- **ty** - Static type checking

### Running Checks

```bash
# Linting
ruff check .

# Type checking
ty check
```
