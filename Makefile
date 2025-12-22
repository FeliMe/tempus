.ONESHELL:

SHELL := /bin/bash
# -e: Exit immediately if a command exits with a non-zero status
# -u: Treat unset variables as an error when substituting
# -o pipefail: The return value of a pipeline is the status of the last command to exit with a non-zero status
SHELLFLAGS := -eu -o pipefail -c

mise:
	@if ! command -v mise &> /dev/null; then \
		curl https://mise.run | sh; \
		echo Adding activation to ~/.bashrc and ~/.zshrc; \
		echo 'eval "$$(~/.local/bin/mise activate bash)"' >> ~/.bashrc; \
		echo 'eval "$$(~/.local/bin/mise activate zsh)"' >> ~/.zshrc; \
		echo Open a new shell now to use mise; \
	else \
		echo mise is already installed; \
	fi
	mise install $(mise_install_args)