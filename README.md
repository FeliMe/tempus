# Tempus

A high-performance desktop application for visualizing large time-series datasets. Handles files with millions of rows smoothly using native rendering—no browser bottleneck.

## Installation

### Quick Setup (Recommended)

After cloning the repository, you can either double-click the `install.sh` script in your file manager, or run the following commands:

```bash
# Clone the repository
git clone <repository-url>
cd tempus

# Option 1: Double-click install.sh in your file manager

# Option 2: Run from terminal
make setup
```

### What Gets Installed

The `make setup` command installs:

1. **mise** - A polyglot runtime manager that handles development tools
2. **uv** - Fast Python package manager (installed via mise)
3. **ruff** - Python linter and formatter (installed via mise)
4. **ty** - Static type checker (installed via mise)
5. **Qt6 development libraries** - Required for PyQt6 GUI framework

### Alternative Installation (Without mise)

If you prefer not to use mise, or if the mise installation fails, you can install the minimum required dependencies manually:

#### 1. Install uv (Required)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or use the Makefile target:

```bash
make install-uv
```

#### 2. Install Qt6 Development Libraries (Required)

Qt6 development libraries are needed for PyQt6. Install them using your system's package manager:

**Debian/Ubuntu:**

```bash
sudo apt install -y qt6-base-dev
```

**Fedora:**

```bash
sudo dnf install -y qt6-qtbase-devel
```

**Arch Linux:**

```bash
sudo pacman -S --noconfirm qt6-base
```

**openSUSE:**

```bash
sudo zypper install -y qt6-base-devel
```

Or use the Makefile target which auto-detects your package manager:

```bash
make qt-dev
```

#### 3. Install Python Dependencies

```bash
uv sync
```

### Troubleshooting

- **mise installation fails**: Use the alternative installation path above with `make install-uv` and `make qt-dev`
- **Qt6 not found during `uv sync`**: Ensure Qt6 development libraries are installed (`make qt-dev`)
- **Command not found after installation**: Open a new terminal shell to reload PATH

## Usage

```bash
# Option 1: Double-click run.sh in your file manager

# Option 2: Run from terminal
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

## Tech Stack

- **PyQt6** - Desktop GUI framework
- **pyqtgraph** - High-performance plotting (OpenGL-accelerated)
- **Pandas** - Data processing (with PyArrow backend for performance)
- **pyqtdarktheme** - Modern dark theme styling

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
