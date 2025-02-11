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

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
DEVOPS_DIR = PROJECT_ROOT / "devops"

console = Console()

class Environment(str, Enum):
    DEV = "dev"
    PROD = "prod"
    TEST = "test"

class LogEntry:
    def __init__(self, command: str, status: str, message: str):
        self.timestamp = datetime.now().strftime("%H:%M:%S")
        self.command = command
        self.status = status
        self.message = message

class MenuItem:
    def __init__(self, key: str, label: str, description: str, action):
        self.key = key
        self.label = label
        self.description = description
        self.action = action

class EnvironmentStatus:
    def __init__(self):
        self.services = {}
        self.lock = Lock()

    def update(self, services: Dict[str, str]):
        with self.lock:
            self.services = services

    def get_status(self) -> Dict[str, str]:
        with self.lock:
            return self.services.copy()

class ProjectConsole:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.current_env = Environment.DEV
        self.running = True
        self.current_row = 0
        self.env_status = {env: EnvironmentStatus() for env in Environment}
        self.command_log = deque(maxlen=6)
        self.last_draw_time = 0
        
        self.init_menu_items()
        self.init_curses()
        
        self.status_thread = Thread(target=self.update_status_loop, daemon=True)
        self.status_thread.start()

    def init_curses(self):
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_CYAN, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(5, curses.COLOR_GREEN, -1)
        curses.init_pair(6, curses.COLOR_RED, -1)
        curses.init_pair(7, curses.COLOR_WHITE, -1)
        curses.curs_set(0)
        self.stdscr.timeout(500)  # Increased timeout to 500ms
        self.stdscr.clear()
        self.stdscr.refresh()

    def log_command(self, command: str, status: str, message: str):
        self.command_log.append(LogEntry(command, status, message))

    def draw_log_area(self):
        height, width = self.stdscr.getmaxyx()
        log_start_y = height - 8
        
        # Draw log area border
        self.draw_box(log_start_y, 0, 8, width)
        
        # Draw header
        header = " Command Log "
        self.stdscr.addstr(log_start_y, (width - len(header)) // 2,
                          header, curses.color_pair(4) | curses.A_BOLD)

        # Draw log entries
        for i, entry in enumerate(self.command_log):
            if i >= 6:  # Maximum 6 log entries
                break
                
            status_color = curses.color_pair(5) if entry.status == "SUCCESS" else curses.color_pair(6)
            log_line = f" [{entry.timestamp}] {entry.command:<20} | {entry.status:<8} | {entry.message}"
            
            if len(log_line) > width - 2:
                log_line = log_line[:width-5] + "..."
                
            self.stdscr.addstr(log_start_y + i + 1, 1, log_line, status_color)

    def draw_menu(self):
        current_time = time.time()
        # Only redraw if 100ms has passed since last draw
        if current_time - self.last_draw_time < 0.1:
            return
            
        try:
            self.stdscr.erase()  # Use erase instead of clear
            height, width = self.stdscr.getmaxyx()
            
            # Draw header
            header = f" Project Management Console - {self.current_env.value.upper()} "
            self.stdscr.addstr(1, (width - len(header)) // 2, header, curses.color_pair(4) | curses.A_BOLD)
            
            # Draw menu items
            for idx, item in enumerate(self.menu_items):
                y = idx + 3
                if y >= height - 20:
                    break

                if idx == self.current_row:
                    attr = curses.color_pair(2) | curses.A_BOLD
                else:
                    attr = curses.color_pair(1)

                menu_str = f"{item.key}: {item.label:<12} - {item.description}"
                if len(menu_str) > width - 4:
                    menu_str = menu_str[:width - 7] + "..."
                
                self.stdscr.addstr(y, 2, menu_str, attr)

            # Draw status panels and log area
            self.draw_status_panels()
            self.draw_log_area()
            
            self.stdscr.refresh()
            self.last_draw_time = current_time
            
        except curses.error:
            pass  # Ignore curses errors during drawing

    def run_compose_command(self, command: str, args: list = None, env: Environment = None) -> subprocess.CompletedProcess:
        if args is None:
            args = []
        if env is None:
            env = self.current_env
            
        compose_file = self.compose_file(env)
        cmd = ["docker", "compose", "-f", compose_file] + command.split() + args
        
        try:
            full_command = " ".join(cmd)
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_command(
                    command.split()[0],
                    "SUCCESS",
                    "Command completed successfully"
                )
            else:
                self.log_command(
                    command.split()[0],
                    "ERROR",
                    result.stderr.split('\n')[0][:50]  # First line of error, truncated
                )
            return result
        except subprocess.CalledProcessError as e:
            self.log_command(
                command.split()[0],
                "ERROR",
                str(e)
            )
            return None
        except Exception as e:
            self.log_command(
                command.split()[0],
                "ERROR",
                str(e)
            )
            return None

    def quick_up(self):
        curses.endwin()
        result = self.run_compose_command("up -d")
        if result and result.returncode == 0:
            self.show_message(f"{self.current_env} environment is up!")
        else:
            error_msg = result.stderr if result else "Error starting environment"
            self.log_command("up", "ERROR", error_msg[:50])
        time.sleep(1)  # Give time to read the message

    def quick_down(self):
        curses.endwin()
        result = self.run_compose_command("down")
        if result and result.returncode == 0:
            self.show_message(f"{self.current_env} environment is down!")
        else:
            self.show_message("Error stopping environment")

    def quick_test(self):
        curses.endwin()
        test_type = questionary.select(
            "Select test type:",
            choices=["unit", "integration", "e2e", "all"]
        ).ask()
        
        if test_type:
            os.chdir(PROJECT_ROOT)
            cmd = ["python", "-m", "pytest"]
            if test_type != "all":
                cmd.extend([f"tests/{test_type}"])
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    self.log_command("test", "SUCCESS", f"Completed {test_type} tests")
                else:
                    self.log_command("test", "ERROR", f"Failed {test_type} tests")
                console.print(result.stdout)
            except Exception as e:
                self.log_command("test", "ERROR", str(e))
            
            input("\nPress Enter to continue...")

    def quick_prune(self):
        curses.endwin()
        if questionary.confirm("Do you want to remove all unused Docker resources?").ask():
            try:
                result = subprocess.run(["docker", "system", "prune", "-f"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    self.log_command("prune", "SUCCESS", "Docker cleanup completed")
                else:
                    self.log_command("prune", "ERROR", result.stderr.split('\n')[0])
            except Exception as e:
                self.log_command("prune", "ERROR", str(e))

    def init_menu_items(self):
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

    def draw_status_panels(self):
        height, width = self.stdscr.getmaxyx()
        panel_width = (width - 4) // 3  # Width for each environment panel
        
        # Draw environment panels
        for i, env in enumerate(Environment):
            # Calculate panel position
            x_start = i * (panel_width + 1) + 2
            y_start = height - 19  # Start above log area
            
            # Draw panel border
            self.draw_box(y_start, x_start, 10, panel_width)
            
            # Draw panel header
            header = f" {env.value.upper()} "
            self.stdscr.addstr(y_start, x_start + (panel_width - len(header))//2,
                             header, curses.color_pair(4) | curses.A_BOLD)
            
            # Draw services status
            services = self.env_status[env].get_status()
            for idx, (service, status) in enumerate(services.items()):
                if idx >= 7:  # Max 7 services shown
                    break
                status_color = curses.color_pair(5) if status == "Running" else curses.color_pair(6)
                service_str = f"{service[:panel_width-15]:<{panel_width-15}} {status:>7}"
                if len(service_str) < panel_width - 2:
                    self.stdscr.addstr(y_start + idx + 1, x_start + 1,
                                     service_str, status_color)

    def draw_box(self, y, x, height, width):
        """Draw a box with ASCII characters"""
        self.stdscr.addstr(y, x, '┌' + '─' * (width-2) + '┐')
        for i in range(1, height-1):
            self.stdscr.addstr(y+i, x, '│')
            self.stdscr.addstr(y+i, x+width-1, '│')
        self.stdscr.addstr(y+height-1, x, '└' + '─' * (width-2) + '┘')

    def update_status_loop(self):
        while self.running:
            for env in Environment:
                services = self.get_status_for_env(env)
                self.env_status[env].update(services)
            time.sleep(2)  # Update status every 2 seconds

    def get_status_for_env(self, env: Environment) -> Dict[str, str]:
        result = self.run_compose_command("ps", env=env)
        services = {}
        if result and result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            for line in lines:
                if line.strip():
                    parts = line.split()
                    service_name = parts[0]
                    status = "Running" if "Up" in line else "Stopped"
                    services[service_name] = status
        return services

    def compose_file(self, env: Environment = None) -> str:
        if env is None:
            env = self.current_env
        return str(DEVOPS_DIR / f"docker-compose.{env}.yml")

    def quick_status(self):
        curses.endwin()
        result = self.run_compose_command("ps")
        if result and result.returncode == 0:
            console.print("\n[cyan]Container Status:[/cyan]")
            console.print(result.stdout)
            input("\nPress Enter to continue...")
        else:
            self.show_message("Error getting status")

    def quick_logs(self):
        curses.endwin()
        services = self.get_services()
        if not services:
            self.show_message("No services found")
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

    def get_services(self) -> list:
        result = self.run_compose_command("config --services")
        if result and result.returncode == 0:
            return result.stdout.strip().split('\n')
        return []

    def cycle_environment(self):
        envs = list(Environment)
        current_index = envs.index(self.current_env)
        self.current_env = envs[(current_index + 1) % len(envs)]
        self.show_message(f"Switched to {self.current_env.value} environment")
        self.init_menu_items()  # Refresh menu items with new environment

    def show_message(self, message: str):
        self.log_command("INFO", "INFO", message)

    def quit_app(self):
        self.running = False

    def run(self):
        try:
            while self.running:
                self.draw_menu()
                try:
                    key = self.stdscr.getch()
                    if key == -1:  # No input
                        continue
                        
                    if key == ord('q'):
                        self.running = False
                        break
                        
                    if key == curses.KEY_UP and self.current_row > 0:
                        self.current_row -= 1
                    elif key == curses.KEY_DOWN and self.current_row < len(self.menu_items) - 1:
                        self.current_row += 1
                    elif key == ord('\n'):  # Enter key
                        self.menu_items[self.current_row].action()
                    else:
                        # Check for shortcut keys
                        char = chr(key).lower() if 32 <= key <= 126 else ''
                        for item in self.menu_items:
                            if char == item.key:
                                item.action()
                                break
                                
                except curses.error:
                    continue
                
                time.sleep(0.05)  # Add small delay between loops
                
        except KeyboardInterrupt:
            self.running = False
        finally:
            curses.endwin()

def main():
    try:
        os.chdir(DEVOPS_DIR)
        print("Starting ProjectConsole...")  # Debug output
        curses.wrapper(lambda stdscr: ProjectConsole(stdscr).run())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    finally:
        curses.endwin()  # Ensure terminal is restored

if __name__ == "__main__":
    main()