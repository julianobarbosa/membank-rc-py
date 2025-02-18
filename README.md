# Roo Code Memory Bank Installer

A cross-platform CLI tool for installing the Roo Code Memory Bank extension into your project. This tool automatically downloads the necessary `.clinerules` files and sets up a `memory-bank` folder with essential documentation. It also provides a convenient self-installation option to add the tool to your Python Scripts folder, making it globally accessible.

## Features

- **Extension Installation:**  
  Detects if extension files exist and, if not, downloads:
  - `.clinerules-architect`
  - `.clinerules-ask`
  - `.clinerules-code`
  
  It also creates a `memory-bank` folder and generates `memory-bank/productContext.md` based on your project’s README file.

- **Git Integration:**  
  Optionally appends the extension files and folder to your project's `.gitignore`.

- **Self-Installation:**  
  Installs the CLI tool into your Python Scripts folder so you can run it from anywhere (provided Python is in your PATH).

- **Cross-Platform:**  
  Runs on any platform with Python 3.10+ installed (macOS, Linux, Windows).

- **Command-Line Interface:**  
  Provides subcommands (`install-extension`, `self-install`), along with `--help` and `--version` options.

## Requirements

- Python 3.10 or higher
- Internet connection (to download the extension files)

## Installation

1. **Clone or Download the Script:**

   ```bash
   git clone https://github.com/heratiki/roo-code-memory-bank-installer.git
   cd roo-code-memory-bank-installer
