.ONESHELL:

SHELL := /bin/bash
# -e: Exit immediately if a command exits with a non-zero status
# -u: Treat unset variables as an error when substituting
# -o pipefail: The return value of a pipeline is the status of the last command to exit with a non-zero status
SHELLFLAGS := -eu -o pipefail -c

setup: mise qt-dev
	@echo "Setup complete!"

mise:
	@if ! command -v mise &> /dev/null; then \
		echo "Installing mise..."; \
		curl https://mise.run | sh; \
		if ! grep -q 'eval "$$(~/.local/bin/mise activate bash)"' ~/.bashrc; then \
			echo "Adding activation to ~/.bashrc"; \
			echo 'eval "$$(~/.local/bin/mise activate bash)"' >> ~/.bashrc; \
		fi; \
		echo "Installing packages with mise..."; \
		~/.local/bin/mise trust; \
		~/.local/bin/mise install; \
		echo "Open a new shell now to use mise"; \
	elif [ -n "$$(mise ls --missing 2>/dev/null)" ]; then \
		echo "Installing missing packages with mise..."; \
		mise trust; \
		mise install; \
	else \
		echo "mise and all packages are already installed"; \
	fi

qt-dev:
	@if command -v apt &> /dev/null; then \
		echo "Installing qt6-base-dev using apt..."; \
		sudo apt install -y qt6-base-dev; \
	elif command -v apt-get &> /dev/null; then \
		echo "Installing qt6-base-dev using apt-get..."; \
		sudo apt-get install -y qt6-base-dev; \
	elif command -v dnf &> /dev/null; then \
		echo "Installing qt6-qtbase-devel using dnf..."; \
		sudo dnf install -y qt6-qtbase-devel; \
	elif command -v yum &> /dev/null; then \
		echo "Installing qt6-qtbase-devel using yum..."; \
		sudo yum install -y qt6-qtbase-devel; \
	elif command -v zypper &> /dev/null; then \
		echo "Installing qt6-base-devel using zypper..."; \
		sudo zypper install -y qt6-base-devel; \
	elif command -v pacman &> /dev/null; then \
		echo "Installing qt6-base using pacman..."; \
		sudo pacman -S --noconfirm qt6-base; \
	else \
		echo "No supported package manager found (apt, apt-get, dnf, yum, zypper, pacman)"; \
		exit 1; \
	fi

install-uv:
	@if ! command -v uv &> /dev/null; then \
		echo "Installing uv 0.7.8..."; \
		curl -LsSf https://astral.sh/uv/0.7.8/install.sh | sh; \
		echo "uv installed!"; \
	else \
		echo "uv is already installed"; \
	fi

tempus:
	uv run tempus-desktop "$@"
