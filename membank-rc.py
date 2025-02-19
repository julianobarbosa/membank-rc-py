#!/usr/bin/env python3
import argparse
import os
import sys
import urllib.request
import shutil
import sysconfig

# --- Version Check ---
# Ensure the script is run with Python 3.10 or higher
if sys.version_info < (3, 10):
    print("This script requires Python 3.10 or higher.")
    sys.exit(1)

# --- Constants & URLs ---
# List of expected files and folders for the extension
expected_files = [
    ".clinerules-architect",
    ".clinerules-ask",
    ".clinerules-code",
    os.path.join("memory-bank", "activeContext.md"),
    os.path.join("memory-bank", "decisionLog.md"),
    os.path.join("memory-bank", "productContext.md"),
    os.path.join("memory-bank", "progress.md"),
    os.path.join("memory-bank", "systemPatterns.md"),
]

# URLs for downloading the .clinerules files
clinerules_files = {
    ".clinerules-architect": "https://raw.githubusercontent.com/GreatScottyMac/roo-code-memory-bank/main/.clinerules-architect",
    ".clinerules-ask":       "https://raw.githubusercontent.com/GreatScottyMac/roo-code-memory-bank/main/.clinerules-ask",
    ".clinerules-code":      "https://raw.githubusercontent.com/GreatScottyMac/roo-code-memory-bank/main/.clinerules-code"
}

# --- Utility Functions ---
def any_extension_exists():
    """Check if any expected file/folder exists in the current directory."""
    for path in expected_files:
        if os.path.exists(path):
            return True
    if os.path.isdir("memory-bank"):
        return True
    return False

def prompt_yes_no(prompt):
    """Prompt the user for a yes/no answer."""
    answer = input(prompt + " [Y/n]: ").strip().lower()
    return answer in ("", "y", "yes")

def create_memory_bank_folder():
    """Create the 'memory-bank' folder if it doesn't exist."""
    if not os.path.exists("memory-bank"):
        os.makedirs("memory-bank")
        print("Created 'memory-bank' folder.")

def download_file(url, dest):
    """Download a file from a URL and write it to a destination path."""
    try:
        print(f"Downloading {dest}...")
        with urllib.request.urlopen(url) as response:
            content = response.read().decode("utf-8")
        with open(dest, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Downloaded {dest}.")
    except Exception as e:
        print(f"Error downloading {dest}: {e}")
        sys.exit(1)

def generate_product_context():
    """Generate memory-bank/productContext.md by extracting a brief project description from a README file."""
    description = None
    # Define potential README file names
    readme_files = ["README.md", "readme.md", "README.txt", "readme.txt"]
    for readme in readme_files:
        if os.path.exists(readme):
            with open(readme, "r", encoding="utf-8") as f:
                content = f.read()
            # Try "## Project Description" first
            if "## Project Description" in content:
                after_marker = content.split("## Project Description", 1)[1].strip()
            # Otherwise, try "## What it does"
            elif "## What it does" in content:
                after_marker = content.split("## What it does", 1)[1].strip()
            else:
                after_marker = content

            # Split the content by headers if any appear
            lines = after_marker.splitlines()
            collected = []
            for line in lines:
                # Stop if a new header is met.
                if line.strip().startswith("##"):
                    break
                if line.strip():
                    collected.append(line.strip())
                # Gather up to first 2 non-empty lines
                if len(collected) == 2:
                    break
            if collected:
                # Join lines and extract only the first sentence if possible.
                candidate = " ".join(collected)
                # Basic heuristic: take text up to first period.
                if "." in candidate:
                    candidate = candidate.split(".", 1)[0] + "."
                description = candidate
                break

    if not description:
        description = "No project description available."

    prod_context_path = os.path.join("memory-bank", "productContext.md")
    if os.path.exists(prod_context_path):
        if not prompt_yes_no(f"{prod_context_path} already exists. Overwrite?"):
            print("Skipping productContext.md creation.")
            return
    with open(prod_context_path, "w", encoding="utf-8") as f:
        f.write("# Product Context\n\n")
        f.write(description + "\n")
    print("Created memory-bank/productContext.md with project description.")
def update_gitignore():
    """Ask the user to append extension files/folder to .gitignore."""
    ignore_lines = [
        ".clinerules-architect",
        ".clinerules-ask",
        ".clinerules-code",
        "memory-bank/"
    ]
    gitignore_path = ".gitignore"
    existing_lines = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            existing_lines = f.read().splitlines()

    with open(gitignore_path, "a", encoding="utf-8") as f:
        for line in ignore_lines:
            if line not in existing_lines:
                f.write(line + "\n")
                print(f"Added '{line}' to .gitignore.")
    print("Updated .gitignore.")

def verify_installation():
    """Ensure the three .clinerules files and productContext.md exist."""
    required = list(clinerules_files.keys()) + [os.path.join("memory-bank", "productContext.md")]
    all_good = True
    for path in required:
        if not os.path.exists(path):
            print(f"Error: {path} is missing.")
            all_good = False
    return all_good

# --- Command Functions ---
def do_install_extension(architect_url, ask_url, code_url):
    """Run the installation process for the Roo Code Memory Bank extension."""
    print("=== Roo Code Memory Bank Extension Installer ===\n")
    if any_extension_exists():
        print("Extension files already exist in this directory. Aborting installation.")
        sys.exit(0)
    if not prompt_yes_no("No Roo Code Memory Bank files found. Would you like to install the extension?"):
        print("Installation aborted.")
        sys.exit(0)

    create_memory_bank_folder()
    download_file(architect_url, ".clinerules-architect")
    download_file(ask_url, ".clinerules-ask")
    download_file(code_url, ".clinerules-code")
    generate_product_context()


    if verify_installation():
        print("\nRoo Code Memory Bank extension has been successfully created in the current folder.")
    else:
        print("\nInstallation encountered errors. Please check the output and try again.")
        sys.exit(1)

    if prompt_yes_no("Would you like to add the extension files to your .gitignore file?"):
        update_gitignore()
    else:
        print("Skipping .gitignore update.")
def do_self_install():
    """
    Install this CLI tool into the Python Scripts folder so that it can be run globally.
    If a virtual environment is detected, prompt the user to choose the installation location.
    Safety checks ensure no accidental damage to the file system.
    """
    # Determine target base path based on virtual environment detection
    if sys.prefix != sys.base_prefix:
        # Virtual environment detected
        choice = input("Virtual environment detected. Install to (v)env or (g)lobal Python? [v/g]: ").strip().lower()
        if choice == "g":
            # Use global Python installation base
            base_path = sys.base_prefix
        else:
            # Default to current virtual environment
            base_path = sys.prefix
    else:
        base_path = sys.prefix

    # Get the scripts directory for the selected base
    target_folder = sysconfig.get_path("scripts", vars={'base': base_path})
    if not target_folder:
        print("Could not determine the Python Scripts directory for the selected installation.")
        sys.exit(1)

    # Safety check: ensure the target folder is writable
    if not os.access(target_folder, os.W_OK):
        print(f"Write access denied for directory: {target_folder}. Aborting installation.")
        sys.exit(1)

    # Define the target file path using 'membank-rc' with platform-specific extension
    if os.name == 'nt':
        target_file = os.path.join(target_folder, "membank-rc.py")
    else:
        target_file = os.path.join(target_folder, "membank-rc")
    current_script = os.path.abspath(__file__)

    # Safety check: if the target file exists, prompt before overwriting
    if os.path.exists(target_file):
        overwrite = input(f"{target_file} already exists. Overwrite? [y/N]: ").strip().lower()
        if overwrite not in ("y", "yes"):
            print("Installation aborted by user.")
            sys.exit(0)

    try:
        shutil.copy(current_script, target_file)
        if os.name != 'nt':
            try:
                os.chmod(target_file, 0o755)
            except Exception as e:
                print(f"Warning: Could not set executable permissions: {e}")
                print("You may need to manually set executable permissions.")
        else:
            # On Windows, create a batch file launcher
            bat_path = os.path.join(target_folder, "membank-rc.bat")
            with open(bat_path, "w", encoding="utf-8") as bat:
                bat.write(f'@echo off\r\n"{sys.executable}" "{target_file}" %*\r\n')
            print(f"Created Windows batch launcher at {bat_path}.")
        print(f"Successfully installed the tool to {target_file}.")
    except Exception as e:
        print(f"Error installing tool: {e}")
        sys.exit(1)

# --- Main CLI ---
def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Roo Code Memory Bank Extension Installer and Self-Installer."
    )
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # Subcommand to install the extension into the current folder
    install_parser = subparsers.add_parser(
        "install-extension",
        help="Install the Roo Code Memory Bank extension in the current directory."
    )
    install_parser.add_argument(
        "--architect-url",
        default="https://raw.githubusercontent.com/GreatScottyMac/roo-code-memory-bank/main/.clinerules-architect",
        help="URL for the .clinerules-architect file"
    )
    install_parser.add_argument(
        "--ask-url",
        default="https://raw.githubusercontent.com/GreatScottyMac/roo-code-memory-bank/main/.clinerules-ask",
        help="URL for the .clinerules-ask file"
    )
    install_parser.add_argument(
        "--code-url",
        default="https://raw.githubusercontent.com/GreatScottyMac/roo-code-memory-bank/main/.clinerules-code",
        help="URL for the .clinerules-code file"
    )
    # Subcommand to install this CLI tool into the Python Scripts folder
    subparsers.add_parser(
        "self-install",
        help="Install this CLI tool into your Python Scripts directory for global access."
    )

    # Global version flag
    parser.add_argument("--version", action="store_true", help="Show version info and exit.")

    args = parser.parse_args()

    if args.version:
        print("Roo Code Memory Bank Installer version 1.0")
        sys.exit(0)

    if args.command == "install-extension":
        do_install_extension(args.architect_url, args.ask_url, args.code_url)
    elif args.command == "self-install":
        do_self_install()
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
