#!/usr/bin/env python3

import os
import sys
import subprocess
from pathlib import Path
from enum import Enum
import curses
import questionary
from rich.console import Console
from rich import print as rprint
import time
from typing import Optional, List, Dict
from threading import Thread, Lock
from collections import deque
from datetime import datetime

# Path resolution based on script location
SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = Path(os.getcwd()).resolve()  # Use current working directory as project root
DEVOPS_DIR = PROJECT_ROOT / "devops"

console = Console()

class Environment(str, Enum):
    DEV = "dev"
    PROD = "prod"
    TEST = "test"

class LogEntry:
    """Represents a single command log entry with a timestamp, command, status, and message."""
    def __init__(self, command: str, status: str, message: str):
        self.timestamp = datetime.now().strftime("%H:%M:%S")
        self.command = command
        self.status = status
        self.message = message

class MenuItem:
    """Represents a single menu item that can be selected in the TUI."""
    def __init__(self, key: str, label: str, description: str, action):
        self.key = key
        self.label = label
        self.description = description
        self.action = action

class ProjectConsole:
    """Console-style TUI for managing Docker Compose environments."""
    def __init__(self, stdscr) -> None:
        self.stdscr = stdscr
        self.current_env = Environment.DEV
        self.running = True
        self.current_row = 0
        
        # Holds command output with expanded size for more visibility
        self.command_output = deque(maxlen=15)
        self.command_log: List[LogEntry] = []
        self.last_draw_time = 0
        
        self.init_menu_items()
        self.init_curses()

    def init_curses(self) -> None:
        """Configure curses settings."""
        curses.start_color()
        curses.use_default_colors()
        
        # Simple color scheme
        curses.init_pair(1, curses.COLOR_WHITE, -1)  # Default
        curses.init_pair(2, curses.COLOR_GREEN, -1)  # Selected
        curses.init_pair(3, curses.COLOR_YELLOW, -1)  # Commands
        curses.init_pair(4, curses.COLOR_CYAN, -1)    # Header
        curses.init_pair(5, curses.COLOR_RED, -1)     # Errors

        curses.curs_set(0)
        self.stdscr.timeout(500)
        self.stdscr.clear()
        self.stdscr.refresh()

    def init_menu_items(self) -> None:
        """Initialize menu items."""
        self.menu_items = [
            MenuItem("u", "Up", f"Start {self.current_env} environment", self.quick_up),
            MenuItem("d", "Down", f"Stop {self.current_env} environment", self.quick_down),
            MenuItem("s", "Status", "Show detailed status", self.quick_status),
            MenuItem("l", "Logs", "View service logs", self.quick_logs),
            MenuItem("p", "Prune", "Clean Docker resources", self.quick_prune),
            MenuItem("t", "Test", "Run tests", self.quick_test),
            MenuItem("e", "Environment", f"Switch environment (current: {self.current_env.value})", self.cycle_environment),
            MenuItem("q", "Quit", "Exit console", self.quit_app),
        ]

    def draw_menu(self) -> None:
        """Draw the console UI."""
        current_time = time.time()
        if current_time - self.last_draw_time < 0.1:
            return

        try:
            self.stdscr.erase()
            height, width = self.stdscr.getmaxyx()

            # Draw header
            header = f" Project Console [{self.current_env.value.upper()}] "
            self.stdscr.addstr(0, 0, "=" * width, curses.color_pair(4))
            self.stdscr.addstr(1, max(0, (width - len(header)) // 2), header, curses.color_pair(4) | curses.A_BOLD)
            self.stdscr.addstr(2, 0, "=" * width, curses.color_pair(4))

            # Draw menu items in a single row
            menu_line = []
            for item in self.menu_items:
                menu_line.append(f"{item.key}:{item.label}")
            menu_str = " | ".join(menu_line)
            self.stdscr.addstr(3, 2, menu_str, curses.color_pair(3))
            
            # Separator
            self.stdscr.addstr(4, 0, "-" * width, curses.color_pair(1))

            # Command output area (expanded)
            output_start = 5
            max_output_lines = height - output_start - 1
            
            for i, line in enumerate(list(self.command_output)[-max_output_lines:]):
                if output_start + i >= height:
                    break
                    
                # Determine line color based on content
                color = curses.color_pair(1)
                if "ERROR:" in line and not any(status in line.lower() for status in ["creating", "starting", "running"]):
                    color = curses.color_pair(5)
                elif any(word in line.lower() for word in ["starting", "stopping", "running", "created", "done"]):
                    color = curses.color_pair(2)
                elif any(word in line for word in ["$", ">", "Executing:"]):
                    color = curses.color_pair(3)
                
                # Handle long lines by wrapping them
                if len(line) > width - 2:
                    wrapped_lines = [line[j:j + width - 3] for j in range(0, len(line), width - 3)]
                    for w_idx, wrapped_line in enumerate(wrapped_lines):
                        if output_start + i + w_idx >= height:
                            break
                        if w_idx == 0:
                            self.stdscr.addstr(output_start + i + w_idx, 1, wrapped_line, color)
                        else:
                            self.stdscr.addstr(output_start + i + w_idx, 3, wrapped_line, color)
                    i += len(wrapped_lines) - 1
                else:
                    self.stdscr.addstr(output_start + i, 1, line, color)

            self.stdscr.refresh()
            self.last_draw_time = current_time
            
        except curses.error:
            pass

    def run(self) -> None:
        """Main run loop."""
        try:
            while self.running:
                self.draw_menu()
                
                try:
                    key = self.stdscr.getch()
                    if key == -1:
                        continue

                    if key == ord('q'):
                        self.running = False
                        break

                    # Handle shortcut keys
                    if 32 <= key <= 126:
                        char = chr(key).lower()
                        for item in self.menu_items:
                            if char == item.key:
                                item.action()
                                break

                except curses.error:
                    continue

                time.sleep(0.05)
        except KeyboardInterrupt:
            self.running = False
        finally:
            curses.endwin()

    def process_docker_output(self, line: str) -> str:
        """Process and format Docker output messages."""
        # Convert Docker message to more user-friendly format
        line = line.strip()
        
        # Handle network creation messages
        if "Network" in line and "Creating" in line:
            return f"INFO: Creating network {line.split()[1]}"
            
        # Handle container messages
        for action in ["Creating", "Starting", "Stopping", "Removing"]:
            if action in line:
                parts = line.split()
                if len(parts) >= 2:
                    service = parts[0]
                    return f"INFO: {action} service {service}"
        
        return line

    def run_compose_command(
        self,
        command: str,
        args: Optional[List[str]] = None,
        env: Optional[Environment] = None
    ) -> subprocess.CompletedProcess:
        """Run a docker-compose command with enhanced error reporting."""
        if env is None:
            env = self.current_env

        compose_file = self.compose_file(env)
        env_file = DEVOPS_DIR / f".env.{env.value}"
        
        if not Path(compose_file).exists():
            error_msg = f"ERROR: Compose file not found: {compose_file}"
            self.command_output.append(error_msg)
            return subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr=error_msg)

        if not Path(env_file).exists():
            self.command_output.append(f"Warning: Environment file not found: {env_file}")

        cmd = ["docker", "compose", "-f", compose_file]
        if Path(env_file).exists():
            cmd.extend(["--env-file", str(env_file)])
        cmd.extend(command.split())
        if args:
            cmd.extend(args)

        # Log the command being executed
        cmd_str = " ".join(cmd)
        self.command_output.append(f"Executing: {cmd_str}")

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=str(DEVOPS_DIR)
            )

            all_output = []
            all_errors = []

            while True:
                output_line = process.stdout.readline()
                error_line = process.stderr.readline()

                if output_line:
                    formatted_line = self.process_docker_output(output_line)
                    all_output.append(output_line)
                    self.command_output.append(formatted_line)

                if error_line:
                    formatted_error = self.process_docker_output(error_line)
                    all_errors.append(error_line)
                    if "WARNING" in error_line.upper():
                        self.command_output.append(f"Warning: {formatted_error}")
                    else:
                        self.command_output.append(f"ERROR: {formatted_error}")

                if process.poll() is not None:
                    # Get any remaining output
                    remaining_out, remaining_err = process.communicate()
                    if remaining_out:
                        all_output.append(remaining_out)
                        for line in remaining_out.splitlines():
                            formatted_line = self.process_docker_output(line)
                            self.command_output.append(formatted_line)
                    if remaining_err:
                        all_errors.append(remaining_err)
                        for line in remaining_err.splitlines():
                            formatted_error = self.process_docker_output(line)
                            if "WARNING" in line.upper():
                                self.command_output.append(f"Warning: {formatted_error}")
                            else:
                                self.command_output.append(f"ERROR: {formatted_error}")
                    break

            returncode = process.wait()
            
            # Add a summary of the command execution
            if returncode == 0:
                self.command_output.append(f"Command completed successfully")
            else:
                self.command_output.append(f"Command failed with exit code {returncode}")
                if not all_errors:
                    self.command_output.append("No error output was captured. Check if Docker is running and accessible.")
            
            return subprocess.CompletedProcess(
                cmd,
                returncode,
                "".join(all_output),
                "".join(all_errors),
            )

        except FileNotFoundError:
            error_msg = "ERROR: Docker command not found. Is Docker installed and in your PATH?"
            self.command_output.append(error_msg)
            return subprocess.CompletedProcess(cmd, 1, "", error_msg)
        except PermissionError:
            error_msg = "ERROR: Permission denied. Do you have the right permissions to run Docker?"
            self.command_output.append(error_msg)
            return subprocess.CompletedProcess(cmd, 1, "", error_msg)
        except Exception as e:
            error_msg = f"ERROR: Command failed: {str(e)}"
            self.command_output.append(error_msg)
            self.command_output.append("Check if Docker daemon is running with: 'docker info'")
            return subprocess.CompletedProcess(cmd, 1, "", error_msg)

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=str(DEVOPS_DIR)  # Ensure we're in the correct directory
            )

            all_output = []
            all_errors = []

            while True:
                output_line = process.stdout.readline()
                error_line = process.stderr.readline()

                if output_line:
                    all_output.append(output_line)
                    self.command_output.append(output_line.strip())

                if error_line:
                    all_errors.append(error_line)
                    self.command_output.append(f"ERROR: {error_line.strip()}")

                if process.poll() is not None:
                    # Get any remaining output
                    remaining_out, remaining_err = process.communicate()
                    if remaining_out:
                        all_output.append(remaining_out)
                        for line in remaining_out.splitlines():
                            self.command_output.append(line.strip())
                    if remaining_err:
                        all_errors.append(remaining_err)
                        for line in remaining_err.splitlines():
                            self.command_output.append(f"ERROR: {line.strip()}")
                    break

            returncode = process.wait()
            
            # Add a summary of the command execution
            if returncode == 0:
                self.command_output.append(f"Command completed successfully: {cmd_str}")
            else:
                self.command_output.append(f"Command failed with exit code {returncode}: {cmd_str}")
                if not all_errors:  # If no specific error message was captured
                    self.command_output.append("No error output was captured. Check if Docker is running and accessible.")
            
            return subprocess.CompletedProcess(
                cmd,
                returncode,
                "".join(all_output),
                "".join(all_errors),
            )

        except FileNotFoundError:
            error_msg = "ERROR: Docker command not found. Is Docker installed and in your PATH?"
            self.command_output.append(error_msg)
            return subprocess.CompletedProcess(cmd, 1, "", error_msg)
        except PermissionError:
            error_msg = "ERROR: Permission denied. Do you have the right permissions to run Docker?"
            self.command_output.append(error_msg)
            return subprocess.CompletedProcess(cmd, 1, "", error_msg)
        except Exception as e:
            error_msg = f"ERROR: Command failed: {str(e)}"
            self.command_output.append(error_msg)
            self.command_output.append("Check if Docker daemon is running with: 'docker info'")
            return subprocess.CompletedProcess(cmd, 1, "", error_msg)

    def quick_up(self) -> None:
        """Start the current environment with detailed error reporting."""
        self.command_output.append(f"Starting {self.current_env.value} environment...")
        self.draw_menu()
        
        # Verify docker-compose file exists
        compose_file = Path(self.compose_file())
        if not compose_file.exists():
            self.command_output.append(f"ERROR: Docker compose file not found: {compose_file}")
            self.command_output.append(f"Expected location: {DEVOPS_DIR}")
            self.command_output.append("Please check if you're in the correct directory and the file exists.")
            return

        # Verify docker is running
        try:
            docker_info = subprocess.run(["docker", "info"], capture_output=True, text=True)
            if docker_info.returncode != 0:
                self.command_output.append("ERROR: Unable to connect to Docker daemon")
                self.command_output.append("Please check if Docker is running with: 'docker info'")
                return
        except FileNotFoundError:
            self.command_output.append("ERROR: Docker command not found")
            self.command_output.append("Please ensure Docker is installed and in your PATH")
            return

        # Run the compose command
        result = self.run_compose_command("up -d")
        if not result or result.returncode != 0:
            self.command_output.append("Failed to start environment. Details:")
            if result and result.stderr:
                for line in result.stderr.splitlines():
                    self.command_output.append(f"  → {line.strip()}")
            self.command_output.append("Troubleshooting steps:")
            self.command_output.append("1. Check if all required images are available")
            self.command_output.append("2. Verify network connectivity")
            self.command_output.append("3. Check port conflicts")
            self.command_output.append("Run 'docker-compose -f docker-compose.dev.yml config' to validate configuration")
        else:
            self.command_output.append(f"Successfully started {self.current_env.value} environment")
        
        self.draw_menu()

    def quick_down(self) -> None:
        """Stop the current environment."""
        self.command_output.append("Stopping environment...")
        self.draw_menu()
        result = self.run_compose_command("down")
        if result and result.returncode == 0:
            self.command_output.append(f"{self.current_env} environment is down!")
        else:
            self.command_output.append("Error stopping environment.")
        self.draw_menu()

    def quick_test(self) -> None:
        """Run tests."""
        curses.endwin()
        test_type = questionary.select(
            "Select test type:",
            choices=["unit", "integration", "e2e", "all"]
        ).ask()

        if test_type:
            os.chdir(PROJECT_ROOT)
            cmd = ["python", "-m", "pytest"]
            if test_type != "all":
                cmd.append(f"tests/{test_type}")

            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    self.command_output.append(f"Completed {test_type} tests")
                else:
                    self.command_output.append(f"Failed {test_type} tests")
                console.print(result.stdout)
            except Exception as e:
                self.command_output.append(f"Test error: {e}")

            input("\nPress Enter to continue...")

    def quick_prune(self) -> None:
        """Clean Docker resources."""
        curses.endwin()
        if questionary.confirm("Do you want to remove all unused Docker resources?").ask():
            try:
                result = subprocess.run(
                    ["docker", "system", "prune", "-f"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    self.command_output.append("Docker cleanup completed")
                else:
                    self.command_output.append(f"Cleanup failed: {result.stderr}")
            except Exception as e:
                self.command_output.append(f"Cleanup error: {e}")

    def quick_status(self) -> None:
        """Show environment status."""
        self.command_output.append(f"Getting status for {self.current_env.value} environment...")
        self.draw_menu()

        # First get services configuration
        config_result = self.run_compose_command("config --services")
        services = []
        if config_result and config_result.returncode == 0:
            services = config_result.stdout.strip().split('\n')
            if services:
                self.command_output.append(f"\nDefined services:")
                for service in services:
                    self.command_output.append(f"  • {service}")

        # Then get running containers
        result = self.run_compose_command("ps")
        if result and result.returncode == 0:
            if "NAME" not in result.stdout:
                self.command_output.append("\nNo containers are currently running")
            else:
                self.command_output.append("\nRunning containers:")
                # Skip header line
                containers = [line for line in result.stdout.split('\n')[1:] if line.strip()]
                for container in containers:
                    parts = container.split()
                    if len(parts) >= 2:
                        name = parts[0]
                        status = "Running" if "Up" in container else "Stopped"
                        self.command_output.append(f"  • {name}: {status}")
        else:
            self.command_output.append("Error getting status.")
        
        self.draw_menu()

    def quick_logs(self) -> None:
        """View service logs."""
        curses.endwin()
        services = self.get_services()
        if not services:
            self.command_output.append("No services found")
            return

        service = questionary.select(
            "Select service to view logs:",
            choices=services
        ).ask()

        if service:
            result = self.run_compose_command(f"logs {service}")
            if result:
                console.print(result.stdout)
            input("\nPress Enter to continue...")

    def get_services(self) -> List[str]:
        """Get list of services from compose file."""
        result = self.run_compose_command("config --services")
        if result and result.returncode == 0:
            return result.stdout.strip().split('\n')
        return []

    def cycle_environment(self) -> None:
        """Switch to next environment."""
        envs = list(Environment)
        current_index = envs.index(self.current_env)
        new_env = envs[(current_index + 1) % len(envs)]
        
        # Verify compose file exists for the new environment
        new_compose_file = Path(self.compose_file(new_env))
        if not new_compose_file.exists():
            self.command_output.append(f"Warning: No compose file found for {new_env.value} environment")
            self.command_output.append(f"Expected: {new_compose_file}")
            return
            
        # Check if current environment has running containers
        result = self.run_compose_command("ps", env=self.current_env)
        has_running = result and result.returncode == 0 and "Up" in result.stdout
        
        if has_running:
            self.command_output.append(f"Warning: Active containers found in {self.current_env.value} environment")
            self.command_output.append("Consider stopping them first with 'd' command")
            
        self.current_env = new_env
        self.command_output.append(f"Switched to {self.current_env.value} environment")
        
        # Show available services in new environment
        config_result = self.run_compose_command("config --services")
        if config_result and config_result.returncode == 0:
            services = config_result.stdout.strip().split('\n')
            if services:
                self.command_output.append("Available services:")
                for service in services:
                    self.command_output.append(f"  • {service}")
                    
        self.init_menu_items()

    def compose_file(self, env: Optional[Environment] = None) -> str:
        """Get compose file path."""
        if env is None:
            env = self.current_env
        # Use .value to get the string value from the Environment enum
        return str(DEVOPS_DIR / f"docker-compose.{env.value}.yml")

    def quit_app(self) -> None:
        """Exit the application."""
        self.running = False

def main() -> None:
    """Main entry point."""
    debug_mode = "--debug" in sys.argv
    
    try:
        if debug_mode:
            print("Starting ProjectConsole in debug mode...")
            print(f"Current working directory: {os.getcwd()}")
            print(f"Python version: {sys.version}")
        else:
            print("Starting ProjectConsole...")

        # Ensure terminal is in a good state
        os.system("clear" if os.name == "posix" else "cls")
        
        # Initialize curses carefully
        try:
            curses.setupterm()
        except Exception as e:
            if debug_mode:
                print(f"Warning: Failed to setup terminal: {e}")

        # Start the curses UI
        try:
            curses.wrapper(lambda stdscr: ProjectConsole(stdscr).run())
        except curses.error as e:
            print(f"Curses error: {e}")
            if debug_mode:
                import traceback
                traceback.print_exc()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nExiting due to keyboard interrupt...")
    except Exception as e:
        print(f"Error during startup: {str(e)}")
        if debug_mode:
            print(f"Exception type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
        sys.exit(1)
    finally:
        try:
            curses.endwin()
        except Exception:
            pass

if __name__ == "__main__":
    main()