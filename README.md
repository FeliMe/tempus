# Tempus

TBD: Project description goes here.

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

The following tools are managed by mise (see [.mise.toml](.mise.toml)):

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
