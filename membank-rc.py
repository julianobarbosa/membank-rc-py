#!/usr/bin/env python3
import argparse
import os
import sys
import urllib.request
import shutil
import sysconfig
import time
import socket
import os

import datetime
import re

def get_version():
    """Get current version from GitHub releases."""
    try:
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-Agent', 'membank-rc/0.0.0')]
        url = "https://api.github.com/repos/heratiki/membank-rc-py/releases/latest"
        
        with opener.open(url, timeout=CONNECT_TIMEOUT) as response:
            data = response.read().decode('utf-8')
            release_info = eval(data)  # Safe since we trust the GitHub API response
            return release_info.get('tag_name', '0.0.0').lstrip('v')
    except Exception:
        # If we can't reach GitHub API, return default version
        return "0.0.0"

VERSION = get_version()

# --- Network Configuration ---
# Get network settings from environment variables or use defaults
CONNECT_TIMEOUT = int(os.getenv('MEMBANK_CONNECT_TIMEOUT', '10'))
READ_TIMEOUT = int(os.getenv('MEMBANK_READ_TIMEOUT', '30'))
MAX_RETRIES = int(os.getenv('MEMBANK_MAX_RETRIES', '3'))

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

# URLs for downloading files
GITHUB_API_URL = "https://api.github.com/repos/heratiki/membank-rc-py"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/heratiki/membank-rc-py/main"
SCRIPT_URL = f"{GITHUB_RAW_URL}/membank-rc.py"

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

def download_file(url, dest, max_retries=3, connect_timeout=10, read_timeout=30):
    """
    Download a file from a URL and write it to a destination path.
    
    Args:
        url: The URL to download from
        dest: The destination path to save to
        max_retries: Maximum number of retry attempts (default: 3)
        connect_timeout: Connection timeout in seconds (default: 10)
        read_timeout: Read timeout in seconds (default: 30)
    """
    retry_count = 0
    last_error = None
    
    while retry_count <= max_retries:
        try:
            print(f"Downloading {dest}...")
            if retry_count > 0:
                # Calculate backoff time: 2^n seconds
                backoff = 2 ** retry_count
                print(f"Retry attempt {retry_count}/{max_retries} (waiting {backoff}s)...")
                time.sleep(backoff)
            
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-Agent', f'membank-rc/{VERSION}')]
            
            with opener.open(url, timeout=connect_timeout) as response:
                content = response.read().decode("utf-8")
            
            with open(dest, "w", encoding="utf-8") as f:
                f.write(content)
            
            print(f"Successfully downloaded {dest}.")
            return True
            
        except urllib.error.URLError as e:
            last_error = e
            error_msg = str(e.reason) if hasattr(e, 'reason') else str(e)
            
            if isinstance(e.reason, socket.timeout):
                print(f"Timeout error: {error_msg}")
            elif isinstance(e.reason, socket.gaierror):
                print(f"Network error: Could not resolve host - {error_msg}")
            else:
                print(f"Download error: {error_msg}")
                
        except socket.timeout as e:
            last_error = e
            print(f"Timeout error: {e}")
            
        except Exception as e:
            last_error = e
            print(f"Unexpected error: {e}")
        
        retry_count += 1
        
    # If we get here, all retries failed
    print(f"\nFailed to download {dest} after {max_retries} attempts.")
    print(f"Last error: {last_error}")
    if isinstance(last_error, urllib.error.URLError) and isinstance(last_error.reason, socket.timeout):
        print("\nTroubleshooting suggestions:")
        print("1. Check your internet connection")
        print("2. The server might be temporarily unavailable")
        print(f"3. Try increasing the timeouts (current: connect={connect_timeout}s, read={read_timeout}s)")
    sys.exit(1)

def generate_product_context():
    """Generate memory-bank/productContext.md by extracting project description from README and adding efficiency guidelines."""
    description = None
    readme_files = ["README.md", "readme.md", "README.txt", "readme.txt"]
    
    # Efficiency-focused template
    efficiency_template = """
# Product Context

## Project Overview

{project_description}

## Development Guidelines

### Efficiency & Cost Optimization

- Do NOT generate code unless explicitly requested
- Do NOT provide excessive details or descriptions unless necessary
- Keep all responses structured, concise, and actionable
- Always seek approval before expanding on details or switching modes

### Best Practices

1. Gather Full Context Before Planning
   - Ask only critical clarifying questions
   - Identify key objectives and constraints
   - Use existing context when sufficient

2. Design & Development Efficiency
   - Follow modern development principles
   - Optimize for performance and maintainability
   - Prioritize modular, reusable solutions
   - Consider scalability and long-term costs

3. Token-Efficient Development
   - Break features into logical phases
   - Focus on essential architecture
   - Use efficient tools and frameworks
   - Provide concise, actionable roadmaps
   - Seek approval before detailed implementation
"""

    # Extract project description from README
    for readme in readme_files:
        if os.path.exists(readme):
            with open(readme, "r", encoding="utf-8") as f:
                content = f.read()

            # Try to find project description section
            sections = [
                ("## Project Description", "## "),
                ("## What it does", "## "),
                ("# Project Description", "# "),
                ("# What it does", "# ")
            ]

            for section_start, section_end in sections:
                if section_start in content:
                    parts = content.split(section_start, 1)[1].split(section_end, 1)
                    description = parts[0] if len(parts) > 1 else parts[0]
                    description = description.strip()
                    break

            if not description:
                # If no section found, use first paragraph after first heading
                lines = content.splitlines()
                collecting = False
                collected = []

                for line in lines:
                    if line.startswith('#') and not collecting:
                        collecting = True
                        continue
                    if collecting:
                        if not line.strip():
                            if collected:
                                break
                            continue
                        if line.startswith('#'):
                            break
                        collected.append(line.strip())

                if collected:
                    description = ' '.join(collected)

            if description:
                break

    if not description:
        description = "No project description available."

    # Format the content with the extracted description
    content = efficiency_template.format(project_description=description)

    # Write to productContext.md
    prod_context_path = os.path.join("memory-bank", "productContext.md")
    if os.path.exists(prod_context_path):
        if not prompt_yes_no(f"{prod_context_path} already exists. Overwrite?"):
            print("Skipping productContext.md creation.")
            return

    with open(prod_context_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("Created memory-bank/productContext.md with project description and efficiency guidelines.")
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

def get_remote_file_info(url, max_retries=MAX_RETRIES, connect_timeout=CONNECT_TIMEOUT, read_timeout=READ_TIMEOUT):
    """
    Get information about a remote file including last modified time and content.
    
    Args:
        url: The URL to check
        max_retries: Maximum number of retry attempts
        connect_timeout: Connection timeout in seconds
        read_timeout: Read timeout in seconds
    
    Returns:
        Dict with 'last_modified' and 'content' if successful, None if failed
    """
    retry_count = 0
    last_error = None
    
    while retry_count <= max_retries:
        try:
            if retry_count > 0:
                backoff = 2 ** retry_count
                print(f"Retry attempt {retry_count}/{max_retries} (waiting {backoff}s)...")
                time.sleep(backoff)
            
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-Agent', f'membank-rc/{VERSION}')]
            
            with opener.open(url, timeout=connect_timeout) as response:
                return {
                    'last_modified': response.headers.get('last-modified'),
                    'content': response.read().decode('utf-8')
                }
                
        except urllib.error.URLError as e:
            last_error = e
            error_msg = str(e.reason) if hasattr(e, 'reason') else str(e)
            
            if isinstance(e.reason, socket.timeout):
                print(f"Timeout error checking {url}: {error_msg}")
            elif isinstance(e.reason, socket.gaierror):
                print(f"Network error checking {url}: Could not resolve host - {error_msg}")
            else:
                print(f"Error checking {url}: {error_msg}")
                
        except socket.timeout as e:
            last_error = e
            print(f"Timeout error checking {url}: {e}")
            
        except Exception as e:
            last_error = e
            print(f"Unexpected error checking {url}: {e}")
        
        retry_count += 1
    
    # If we get here, all retries failed
    print(f"\nFailed to check {url} after {max_retries} attempts.")
    print(f"Last error: {last_error}")
    if isinstance(last_error, urllib.error.URLError) and isinstance(last_error.reason, socket.timeout):
        print("\nTroubleshooting suggestions:")
        print("1. Check your internet connection")
        print("2. The server might be temporarily unavailable")
        print(f"3. Try increasing the timeouts (current: connect={connect_timeout}s, read={read_timeout}s)")
    return None

def verify_installation():
    """Ensure the three .clinerules files and productContext.md exist."""
    required = list(clinerules_files.keys()) + [os.path.join("memory-bank", "productContext.md")]
    all_good = True
    for path in required:
        if not os.path.exists(path):
            print(f"Error: {path} is missing.")
            all_good = False
    return all_good

def backup_script(script_path):
    """Create a backup of the script with timestamp."""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{script_path}.{timestamp}.backup"
    try:
        shutil.copy2(script_path, backup_path)
        print(f"Created backup at: {backup_path}")
        return True
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False

def parse_version(version_str):
    """Parse a version string into a tuple of integers."""
    try:
        version_str = version_str.strip()
        if not version_str or not all(part.isdigit() for part in version_str.split('.')):
            return (0, 0, 0)
        return tuple(map(int, version_str.split('.')))
    except (AttributeError, ValueError):
        return (0, 0, 0)

def increment_version(version_str, level='patch'):
    """
    Increment version at specified level (major, minor, or patch).
    Returns the new version string.
    """
    major, minor, patch = parse_version(version_str)
    if level == 'major':
        return f"{major + 1}.0.0"
    elif level == 'minor':
        return f"{major}.{minor + 1}.0"
    else:  # patch
        return f"{major}.{minor}.{patch + 1}"

def update_memory_bank_version(new_version):
    """Update version in Memory Bank's productContext.md."""
    try:
        prod_context_path = os.path.join("memory-bank", "productContext.md")
        with open(prod_context_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Update current version
        content = re.sub(
            r"Current Version: [\d\.]+",
            f"Current Version: {new_version}",
            content
        )

        # Add to version history if not present
        history_marker = "Version History:"
        if history_marker in content:
            history_section = content.split(history_marker)[1].split("\n\n")[0]
            if new_version not in history_section:
                today = datetime.datetime.now().strftime("%Y-%m-%d")
                history_entry = f"  * {new_version} - {today} - Memory Bank update"
                content = content.replace(
                    history_marker,
                    f"{history_marker}\n{history_entry}"
                )

        # Update last updated date
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        content = re.sub(
            r"Last Updated: [\d\-]+",
            f"Last Updated: {today}",
            content
        )

        with open(prod_context_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error updating Memory Bank version: {e}")
        return False

def check_script_version(max_retries=MAX_RETRIES, connect_timeout=CONNECT_TIMEOUT, read_timeout=READ_TIMEOUT):
    """Check if a newer version is available from GitHub releases."""
    print("Checking for script updates...")
    
    retry_count = 0
    last_error = None
    
    while retry_count <= max_retries:
        try:
            if retry_count > 0:
                backoff = 2 ** retry_count
                print(f"Retry attempt {retry_count}/{max_retries} (waiting {backoff}s)...")
                time.sleep(backoff)
            
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-Agent', f'membank-rc/{VERSION}')]
            
            with opener.open(f"{GITHUB_API_URL}/releases/latest", timeout=connect_timeout) as response:
                if response.headers.get('X-RateLimit-Remaining', '').isdigit():
                    remaining = int(response.headers['X-RateLimit-Remaining'])
                    if remaining < 10:
                        print(f"Warning: GitHub API rate limit low ({remaining} requests remaining)")
                
                data = response.read().decode('utf-8')
                release_info = eval(data)  # Safe since we trust the GitHub API response
                latest_version = release_info.get('tag_name', '0.0.0').lstrip('v')
                
                current = parse_version(VERSION)
                latest = parse_version(latest_version)
                
                if latest == (0, 0, 0):
                    print("Warning: Unable to parse latest version number")
                    return None
                    
                if latest > current:
                    return latest_version
                print("Script is up to date.")
                return None
                
        except urllib.error.URLError as e:
            last_error = e
            if hasattr(e, 'code'):
                # HTTP error with status code
                error_msg = f"HTTP {e.code}"
                if e.code == 404:
                    error_msg += " (No releases found on GitHub)"
                elif e.code == 403:
                    error_msg += " (GitHub API rate limit exceeded)"
                    # Check when rate limit resets
                    try:
                        reset_time = int(e.headers.get('X-RateLimit-Reset', 0))
                        if reset_time:
                            reset_datetime = datetime.datetime.fromtimestamp(reset_time)
                            error_msg += f"\nRate limit will reset at {reset_datetime}"
                    except:
                        pass
                else:
                    error_msg += f" ({str(e.reason) if hasattr(e, 'reason') else 'unknown error'})"
                print(f"Error checking version: {error_msg}")
            else:
                # Network-level error
                error_msg = str(e.reason) if hasattr(e, 'reason') else str(e)
                if isinstance(e.reason, socket.timeout):
                    print(f"Timeout error checking version: {error_msg}")
                elif isinstance(e.reason, socket.gaierror):
                    print(f"Network error: Could not resolve host - {error_msg}")
                else:
                    print(f"Network error checking version: {error_msg}")
                
        except socket.timeout as e:
            last_error = e
            print(f"Timeout error checking version: {e}")
            
        except Exception as e:
            last_error = e
            print(f"Unexpected error checking version: {e}")
        
        retry_count += 1
    
    # If we get here, all retries failed
    print(f"\nFailed to check version after {max_retries} attempts.")
    print(f"Last error: {last_error}")
    if isinstance(last_error, urllib.error.URLError) and isinstance(last_error.reason, socket.timeout):
        print("\nTroubleshooting suggestions:")
        print("1. Check your internet connection")
        print("2. The server might be temporarily unavailable")
        print(f"3. Try increasing the timeouts (current: connect={connect_timeout}s, read={read_timeout}s)")
    return None

def update_script(script_path, new_version=None, max_retries=MAX_RETRIES, connect_timeout=CONNECT_TIMEOUT, read_timeout=READ_TIMEOUT):
    """
    Update the script and Memory Bank to the latest version.
    
    Args:
        script_path: Path to the script file to update
        new_version: Optional version string to update to
        max_retries: Maximum number of retry attempts
        connect_timeout: Connection timeout in seconds
        read_timeout: Read timeout in seconds
    
    Returns:
        True if update successful, False otherwise
    """
    retry_count = 0
    last_error = None
    
    while retry_count <= max_retries:
        try:
            print("Downloading latest version...")
            if retry_count > 0:
                backoff = 2 ** retry_count
                print(f"Retry attempt {retry_count}/{max_retries} (waiting {backoff}s)...")
                time.sleep(backoff)
            
            # Create backup first
            if not backup_script(script_path):
                return False
                
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-Agent', f'membank-rc/{VERSION}')]
            
            with opener.open(SCRIPT_URL, timeout=connect_timeout) as response:
                new_content = response.read().decode('utf-8')
            
            # Write new content
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # On Unix-like systems, ensure the file is executable
            if os.name != 'nt':
                os.chmod(script_path, 0o755)

            # Update Memory Bank version if provided
            if new_version and os.path.exists(os.path.join("memory-bank", "productContext.md")):
                if update_memory_bank_version(new_version):
                    print(f"Memory Bank version updated to {new_version}")
                else:
                    print("Warning: Failed to update Memory Bank version")
                
            print("Script successfully updated!")
            return True
            
        except urllib.error.URLError as e:
            last_error = e
            error_msg = str(e.reason) if hasattr(e, 'reason') else str(e)
            
            if isinstance(e.reason, socket.timeout):
                print(f"Timeout error downloading update: {error_msg}")
            elif isinstance(e.reason, socket.gaierror):
                print(f"Network error: Could not resolve host - {error_msg}")
            else:
                print(f"Error downloading update: {error_msg}")
                
        except socket.timeout as e:
            last_error = e
            print(f"Timeout error downloading update: {e}")
            
        except Exception as e:
            last_error = e
            print(f"Unexpected error updating script: {e}")
        
        retry_count += 1
    
    # If we get here, all retries failed
    print(f"\nFailed to update script after {max_retries} attempts.")
    print(f"Last error: {last_error}")
    if isinstance(last_error, urllib.error.URLError) and isinstance(last_error.reason, socket.timeout):
        print("\nTroubleshooting suggestions:")
        print("1. Check your internet connection")
        print("2. The server might be temporarily unavailable")
        print(f"3. Try increasing the timeouts (current: connect={connect_timeout}s, read={read_timeout}s)")
    return False

def do_check_updates(script_path=None):
    """Check for and apply updates to both the script and .clinerules files."""
    print("=== Checking for Updates ===\n")
    
    # Check script updates first
    if script_path:
        latest_version = check_script_version()
        if latest_version:
            print(f"\nNew version available: {latest_version} (current: {VERSION})")
            if prompt_yes_no("Would you like to update the script?"):
                if update_script(script_path, new_version=latest_version):
                    print("\nPlease restart the script to use the new version.")
                    return  # Exit after script update
            else:
                print("Script update skipped.")
        else:
            print("\nScript is up to date.")
    
    # Then check .clinerules updates
    do_update_extension()

def do_update_extension():
    """Check for and apply updates to .clinerules files and Memory Bank version."""
    print("=== Checking for Roo Code Memory Bank Extension Updates ===\n")
    
    updates_available = False
    version_updated = False
    current_version = VERSION
    
    for local_file, remote_url in clinerules_files.items():
        if not os.path.exists(local_file):
            print(f"Warning: {local_file} not found. Skipping update check.")
            continue
            
        print(f"Checking {local_file} for updates...")
        remote_info = get_remote_file_info(remote_url)
        
        if remote_info:
            with open(local_file, 'r', encoding='utf-8') as f:
                local_content = f.read()
            
            if local_content != remote_info['content']:
                updates_available = True
                if prompt_yes_no(f"Update available for {local_file}. Would you like to update?"):
                    with open(local_file, 'w', encoding='utf-8') as f:
                        f.write(remote_info['content'])
                    print(f"Updated {local_file}.")
                else:
                    print(f"Skipped update for {local_file}.")
    
    if not updates_available:
        print("\nAll .clinerules files are up to date!")
    else:
        # Increment version if updates were applied
        new_version = increment_version(current_version, 'patch')
        if update_memory_bank_version(new_version):
            print(f"\nMemory Bank version updated to {new_version}")
        else:
            print("\nWarning: Failed to update Memory Bank version")
        print("\nUpdate process completed.")

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
    
    # Subcommand to update script and .clinerules files
    update_parser = subparsers.add_parser(
        "update",
        help="Check for and apply updates to both the script and .clinerules files."
    )
    update_parser.add_argument(
        "--skip-script",
        action="store_true",
        help="Skip checking for script updates, only check .clinerules files."
    )

    # Global version flag
    parser.add_argument("--version", action="store_true", help="Show version info and exit.")

    args = parser.parse_args()

    if args.version:
        print(f"Roo Code Memory Bank Installer version {VERSION}")
        sys.exit(0)

    if args.command == "install-extension":
        do_install_extension(args.architect_url, args.ask_url, args.code_url)
    elif args.command == "self-install":
        do_self_install()
    elif args.command == "update":
        if args.skip_script:
            do_update_extension()
        else:
            do_check_updates(os.path.abspath(__file__))
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
