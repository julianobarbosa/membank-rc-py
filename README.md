# Roo Code Memory Bank Installer

A cross-platform CLI tool for installing the Roo Code Memory Bank extension into your project. This tool automatically downloads the necessary `.clinerules` files and sets up a `memory-bank` folder with essential documentation. It also provides a convenient self-installation option to add the tool to your Python Scripts folder, making it globally accessible.

## Features

- **Extension Installation:**  
  Detects if extension files exist and, if not, downloads:
  - `.clinerules-architect`
  - `.clinerules-ask`
  - `.clinerules-code`
  
  It also creates a `memory-bank` folder and generates `memory-bank/productContext.md` based on your project's README file.

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
    ```

2. **Make the Script Globally Available (Optional):**

    ```bash
    python membank-rc.py self-install
    ```

    This will install the script to your Python Scripts directory. The installation process is platform-specific:

    - **Windows**:
      - Installs as `membank-rc.py` in the Scripts directory
      - Creates a `membank-rc.bat` launcher for command-line use
    
    - **Unix-like Systems (Linux/macOS)**:
      - Installs as `membank-rc` in the scripts directory
      - Attempts to set executable permissions (chmod 755)
      - If permission setting fails, you may need to manually set execute permissions:
        ```bash
        chmod +x /path/to/scripts/membank-rc
        ```

    When installing in a virtual environment, you'll be prompted to choose between installing to the virtual environment or global Python installation.

## Usage

### Installing the Extension

To install the Roo Code Memory Bank extension in your project directory:

1. Navigate to your project directory:
    ```bash
    cd /path/to/your/project
    ```

2. Run the installation command:
    ```bash
    membank-rc install-extension
    ```
    
    Or if you haven't done the self-install:
    ```bash
    python /path/to/membank-rc.py install-extension
    ```

The installer will:
- Check if any extension files already exist
- Download the necessary .clinerules files
- Create the memory-bank folder
- Generate initial productContext.md from your README
- Optionally update .gitignore

### Using Custom URLs

You can specify custom URLs for the .clinerules files:

```bash
membank-rc install-extension \
  --architect-url https://your-url/.clinerules-architect \
  --ask-url https://your-url/.clinerules-ask \
  --code-url https://your-url/.clinerules-code
```

### Getting Help

Display help information:
```bash
membank-rc --help
```

Show command-specific help:
```bash
membank-rc install-extension --help
membank-rc self-install --help
```

Display version information:
```bash
membank-rc --version
```

## Files Created

The installer creates the following structure in your project:

```
your-project/
├── .clinerules-architect
├── .clinerules-ask
├── .clinerules-code
└── memory-bank/
    └── productContext.md
```

Additional memory-bank files (activeContext.md, decisionLog.md, progress.md, systemPatterns.md) will be created by Roo during usage.

## License

MIT License - See LICENSE file for details.
