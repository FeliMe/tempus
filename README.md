# Tempus

A lightweight web application for visualizing time series data from CSV files.

## Features

- **CSV Upload**: Drag-and-drop or browse to upload CSV files
- **Interactive Charts**: Toggle individual time series on/off, zoom, and pan

## Tech Stack

- **Streamlit** - Web framework
- **Pandas** - Data processing (with PyArrow backend for performance)
- **Plotly** - Interactive charting

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
