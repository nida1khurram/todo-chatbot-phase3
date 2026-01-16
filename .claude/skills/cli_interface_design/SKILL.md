---
name: cli_interface_design
description: Create command-line interfaces using Rich library with Console for colored output, Table for displaying lists, Prompt.ask() for user input, menu-driven navigation, and user-friendly formatting.
---

# CLI Interface Design Skill

You are an expert at creating beautiful, user-friendly command-line interfaces using the Rich library for Python.

## When to Use This Skill

Apply this skill when the user:
- Needs to create a CLI application with colored output
- Wants menu-driven terminal navigation
- Needs to display data in tables or formatted lists
- Wants interactive prompts and user input
- Needs progress bars, spinners, or status indicators

## Rich Library Overview

Rich provides:
- **Console**: Core class for output with colors and styles
- **Table**: Display tabular data beautifully
- **Panel**: Boxed content with titles
- **Prompt**: Interactive user input
- **Progress**: Progress bars and spinners
- **Tree**: Hierarchical data display
- **Markdown/Syntax**: Formatted text rendering

## Installation

```bash
# With UV
uv add rich

# With pip
pip install rich
```

## Core Components

### 1. Console - Basic Output

```python
"""Console basics for colored and styled output."""

from rich.console import Console

# Create console instance (typically one per application)
console = Console()

# Basic printing
console.print("Hello, World!")

# Colored output using markup
console.print("[bold green]Success![/bold green] Operation completed.")
console.print("[red]Error:[/red] Something went wrong.")
console.print("[yellow]Warning:[/yellow] Check your input.")
console.print("[blue]Info:[/blue] Processing started.")

# Styled output
console.print("[bold]Bold text[/bold]")
console.print("[italic]Italic text[/italic]")
console.print("[underline]Underlined text[/underline]")
console.print("[strike]Strikethrough[/strike]")

# Combined styles
console.print("[bold red on white]Important![/bold red on white]")

# Print with emoji
console.print(":white_check_mark: Task completed")
console.print(":x: Task failed")
console.print(":warning: Warning message")

# Rule (horizontal line with optional title)
console.rule("[bold blue]Section Title")

# Print exception with traceback
try:
    raise ValueError("Example error")
except Exception:
    console.print_exception()
```

### 2. Table - Displaying Lists and Data

```python
"""Table component for displaying structured data."""

from rich.console import Console
from rich.table import Table

console = Console()


def display_items_table(items: list[dict]) -> None:
    """Display items in a formatted table."""
    table = Table(
        title="Items List",
        show_header=True,
        header_style="bold magenta",
        show_lines=True,  # Show row separators
    )

    # Add columns
    table.add_column("ID", style="dim", width=6, justify="right")
    table.add_column("Name", style="cyan", min_width=20)
    table.add_column("Status", justify="center")
    table.add_column("Created", style="green")

    # Add rows
    for item in items:
        status = "[green]Active[/green]" if item["active"] else "[red]Inactive[/red]"
        table.add_row(
            str(item["id"]),
            item["name"],
            status,
            item["created"],
        )

    console.print(table)


def display_simple_table() -> None:
    """Display a simple table without extra styling."""
    table = Table(show_header=True, header_style="bold")

    table.add_column("Option")
    table.add_column("Description")

    table.add_row("1", "Create new item")
    table.add_row("2", "List all items")
    table.add_row("3", "Delete item")
    table.add_row("q", "Quit")

    console.print(table)


def display_todo_list(todos: list[dict]) -> None:
    """Display a todo list with checkboxes."""
    table = Table(
        title="[bold]Todo List[/bold]",
        box=None,  # No border
        padding=(0, 1),
    )

    table.add_column("", width=3)  # Checkbox column
    table.add_column("Task")
    table.add_column("Priority", justify="center")

    for todo in todos:
        checkbox = "[green]✓[/green]" if todo["done"] else "[ ]"
        priority_colors = {"high": "red", "medium": "yellow", "low": "green"}
        priority = f"[{priority_colors[todo['priority']]}]{todo['priority']}[/]"

        style = "dim" if todo["done"] else ""
        table.add_row(checkbox, todo["task"], priority, style=style)

    console.print(table)
```

### 3. Prompt - User Input

```python
"""Prompt component for interactive user input."""

from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt

console = Console()


def get_user_input() -> dict:
    """Collect user input with various prompt types."""

    # Basic text prompt
    name = Prompt.ask("Enter your name")

    # Prompt with default value
    email = Prompt.ask("Enter your email", default="user@example.com")

    # Prompt with choices
    color = Prompt.ask(
        "Choose a color",
        choices=["red", "green", "blue"],
        default="blue"
    )

    # Integer prompt with validation
    age = IntPrompt.ask("Enter your age", default=25)

    # Confirmation prompt
    confirmed = Confirm.ask("Do you want to proceed?")

    # Password prompt (hidden input)
    password = Prompt.ask("Enter password", password=True)

    return {
        "name": name,
        "email": email,
        "color": color,
        "age": age,
        "confirmed": confirmed,
    }


def prompt_with_validation() -> str:
    """Prompt with custom validation."""
    while True:
        value = Prompt.ask("Enter a value (3-10 characters)")
        if 3 <= len(value) <= 10:
            return value
        console.print("[red]Value must be 3-10 characters[/red]")


def select_from_list(items: list[str], prompt_text: str = "Select an option") -> str:
    """Display numbered list and get selection."""
    console.print()
    for i, item in enumerate(items, 1):
        console.print(f"  [cyan]{i}[/cyan]. {item}")
    console.print()

    choices = [str(i) for i in range(1, len(items) + 1)]
    selection = Prompt.ask(prompt_text, choices=choices)

    return items[int(selection) - 1]
```

### 4. Panel - Boxed Content

```python
"""Panel component for boxed content display."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def display_info_panel(title: str, content: str) -> None:
    """Display information in a panel."""
    panel = Panel(
        content,
        title=title,
        title_align="left",
        border_style="blue",
        padding=(1, 2),
    )
    console.print(panel)


def display_error_panel(message: str) -> None:
    """Display error message in a red panel."""
    panel = Panel(
        f"[white]{message}[/white]",
        title="[bold]Error[/bold]",
        title_align="left",
        border_style="red",
        padding=(0, 1),
    )
    console.print(panel)


def display_success_panel(message: str) -> None:
    """Display success message in a green panel."""
    panel = Panel(
        f"[white]{message}[/white]",
        title="[bold]Success[/bold]",
        title_align="left",
        border_style="green",
        padding=(0, 1),
    )
    console.print(panel)


def display_welcome_banner(app_name: str, version: str) -> None:
    """Display application welcome banner."""
    text = Text()
    text.append(f"{app_name}\n", style="bold cyan")
    text.append(f"Version {version}\n\n", style="dim")
    text.append("Type 'help' for available commands", style="italic")

    panel = Panel(
        text,
        border_style="bright_blue",
        padding=(1, 4),
    )
    console.print(panel)
```

### 5. Menu-Driven Navigation

```python
"""Menu system for CLI navigation."""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

console = Console()


class MenuOption:
    """Represents a menu option."""

    def __init__(self, key: str, label: str, handler: callable, description: str = ""):
        self.key = key
        self.label = label
        self.handler = handler
        self.description = description


class Menu:
    """Interactive menu system."""

    def __init__(self, title: str, options: list[MenuOption]):
        self.title = title
        self.options = options
        self._build_choices()

    def _build_choices(self) -> None:
        """Build choice list for prompt."""
        self.choices = [opt.key.lower() for opt in self.options]

    def display(self) -> None:
        """Display the menu."""
        console.print()
        console.rule(f"[bold blue]{self.title}[/bold blue]")
        console.print()

        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Key", style="cyan bold", width=4)
        table.add_column("Option")
        table.add_column("Description", style="dim")

        for option in self.options:
            table.add_row(
                f"[{option.key}]",
                option.label,
                option.description,
            )

        console.print(table)
        console.print()

    def get_choice(self) -> MenuOption | None:
        """Get user's menu choice."""
        choice = Prompt.ask(
            "Select option",
            choices=self.choices,
            show_choices=False,
        ).lower()

        for option in self.options:
            if option.key.lower() == choice:
                return option
        return None

    def run(self) -> None:
        """Display menu and handle selection."""
        self.display()
        option = self.get_choice()
        if option:
            option.handler()


class Application:
    """Main application with menu navigation."""

    def __init__(self):
        self.console = Console()
        self.running = True

    def create_main_menu(self) -> Menu:
        """Create the main menu."""
        return Menu(
            title="Main Menu",
            options=[
                MenuOption("1", "Create Item", self.create_item, "Add a new item"),
                MenuOption("2", "List Items", self.list_items, "View all items"),
                MenuOption("3", "Search", self.search_items, "Search for items"),
                MenuOption("4", "Settings", self.show_settings, "Configure app"),
                MenuOption("h", "Help", self.show_help, "Show help"),
                MenuOption("q", "Quit", self.quit, "Exit application"),
            ]
        )

    def run(self) -> None:
        """Run the application main loop."""
        self.show_welcome()

        while self.running:
            menu = self.create_main_menu()
            menu.run()

    def show_welcome(self) -> None:
        """Display welcome message."""
        self.console.clear()
        panel = Panel(
            "[bold cyan]My CLI App[/bold cyan]\n\n"
            "Welcome to the application!",
            border_style="blue",
            padding=(1, 4),
        )
        self.console.print(panel)

    def create_item(self) -> None:
        """Handle create item action."""
        self.console.print("\n[bold]Create New Item[/bold]\n")
        name = Prompt.ask("Item name")
        self.console.print(f"[green]Created item: {name}[/green]\n")

    def list_items(self) -> None:
        """Handle list items action."""
        self.console.print("\n[bold]All Items[/bold]\n")
        # Implementation here

    def search_items(self) -> None:
        """Handle search action."""
        query = Prompt.ask("Search query")
        self.console.print(f"Searching for: {query}\n")

    def show_settings(self) -> None:
        """Show settings submenu."""
        settings_menu = Menu(
            title="Settings",
            options=[
                MenuOption("1", "Theme", lambda: None, "Change color theme"),
                MenuOption("2", "Profile", lambda: None, "Edit profile"),
                MenuOption("b", "Back", lambda: None, "Return to main menu"),
            ]
        )
        settings_menu.run()

    def show_help(self) -> None:
        """Display help information."""
        help_text = """
[bold]Available Commands:[/bold]

  [cyan]1[/cyan] - Create a new item
  [cyan]2[/cyan] - List all items
  [cyan]3[/cyan] - Search items
  [cyan]4[/cyan] - Open settings
  [cyan]h[/cyan] - Show this help
  [cyan]q[/cyan] - Quit application
        """
        self.console.print(Panel(help_text.strip(), title="Help", border_style="green"))

    def quit(self) -> None:
        """Exit the application."""
        if Confirm.ask("Are you sure you want to quit?"):
            self.running = False
            self.console.print("[yellow]Goodbye![/yellow]")
```

### 6. Progress Indicators

```python
"""Progress bars and spinners for long operations."""

import time
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
)

console = Console()


def progress_bar_example(items: list) -> None:
    """Show progress bar for processing items."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
    ) as progress:
        task = progress.add_task("Processing...", total=len(items))

        for item in items:
            # Process item here
            time.sleep(0.1)  # Simulate work
            progress.advance(task)


def spinner_example() -> None:
    """Show spinner for indeterminate operations."""
    with console.status("[bold green]Loading data...") as status:
        # Simulate loading
        time.sleep(2)
        status.update("[bold blue]Processing...")
        time.sleep(1)

    console.print("[green]Done![/green]")


def multiple_progress_bars() -> None:
    """Show multiple concurrent progress bars."""
    with Progress() as progress:
        task1 = progress.add_task("[red]Downloading...", total=100)
        task2 = progress.add_task("[green]Processing...", total=100)
        task3 = progress.add_task("[cyan]Installing...", total=100)

        while not progress.finished:
            progress.update(task1, advance=0.9)
            progress.update(task2, advance=0.6)
            progress.update(task3, advance=0.3)
            time.sleep(0.02)
```

### 7. Tree - Hierarchical Display

```python
"""Tree component for hierarchical data."""

from rich.console import Console
from rich.tree import Tree

console = Console()


def display_directory_tree() -> None:
    """Display a directory-like tree structure."""
    tree = Tree("[bold blue]project/[/bold blue]")

    src = tree.add("[bold]src/[/bold]")
    src.add("main.py")
    src.add("config.py")

    models = src.add("[bold]models/[/bold]")
    models.add("__init__.py")
    models.add("user.py")

    tests = tree.add("[bold]tests/[/bold]")
    tests.add("test_main.py")

    tree.add("pyproject.toml")
    tree.add("README.md")

    console.print(tree)


def display_category_tree(categories: dict) -> None:
    """Display categories as a tree."""
    tree = Tree("[bold]Categories[/bold]")

    def add_items(parent: Tree, items: dict) -> None:
        for key, value in items.items():
            if isinstance(value, dict):
                branch = parent.add(f"[cyan]{key}[/cyan]")
                add_items(branch, value)
            else:
                parent.add(f"{key}: [green]{value}[/green]")

    add_items(tree, categories)
    console.print(tree)
```

### 8. Complete CLI Application Pattern

```python
"""Complete CLI application structure."""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

console = Console()


class CLIApp:
    """Template for a complete CLI application."""

    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self.running = True

    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        console.clear()

    def show_header(self) -> None:
        """Display application header."""
        console.print(
            Panel(
                f"[bold cyan]{self.name}[/bold cyan] v{self.version}",
                border_style="blue",
            )
        )

    def show_menu(self) -> str:
        """Display main menu and get choice."""
        console.print("\n[bold]Main Menu[/bold]\n")

        table = Table(show_header=False, box=None)
        table.add_column("Key", style="cyan", width=4)
        table.add_column("Action")

        table.add_row("1", "Create")
        table.add_row("2", "List")
        table.add_row("3", "Update")
        table.add_row("4", "Delete")
        table.add_row("q", "Quit")

        console.print(table)
        console.print()

        return Prompt.ask(
            "Choose option",
            choices=["1", "2", "3", "4", "q"],
            show_choices=False,
        )

    def handle_choice(self, choice: str) -> None:
        """Route menu choice to handler."""
        handlers = {
            "1": self.create,
            "2": self.list_all,
            "3": self.update,
            "4": self.delete,
            "q": self.quit,
        }
        handler = handlers.get(choice)
        if handler:
            handler()

    def create(self) -> None:
        """Handle create action."""
        console.rule("[bold green]Create New Item")
        name = Prompt.ask("Name")
        console.print(f"\n[green]Created: {name}[/green]\n")
        self.pause()

    def list_all(self) -> None:
        """Handle list action."""
        console.rule("[bold blue]All Items")
        # Display items here
        console.print("[dim]No items yet[/dim]\n")
        self.pause()

    def update(self) -> None:
        """Handle update action."""
        console.rule("[bold yellow]Update Item")
        item_id = Prompt.ask("Item ID")
        console.print(f"[yellow]Updated item {item_id}[/yellow]\n")
        self.pause()

    def delete(self) -> None:
        """Handle delete action."""
        console.rule("[bold red]Delete Item")
        item_id = Prompt.ask("Item ID")
        if Confirm.ask(f"Delete item {item_id}?"):
            console.print(f"[red]Deleted item {item_id}[/red]\n")
        self.pause()

    def quit(self) -> None:
        """Exit application."""
        if Confirm.ask("\nExit application?"):
            self.running = False
            console.print("\n[yellow]Goodbye![/yellow]\n")

    def pause(self) -> None:
        """Pause until user presses Enter."""
        Prompt.ask("\nPress Enter to continue", default="")

    def run(self) -> None:
        """Main application loop."""
        self.clear_screen()
        self.show_header()

        while self.running:
            choice = self.show_menu()
            self.handle_choice(choice)
            if self.running:
                self.clear_screen()
                self.show_header()


def main() -> None:
    """Entry point."""
    app = CLIApp("My App", "1.0.0")
    app.run()


if __name__ == "__main__":
    main()
```

## Style Reference

### Color Names

```
black, red, green, yellow, blue, magenta, cyan, white
bright_black, bright_red, bright_green, bright_yellow
bright_blue, bright_magenta, bright_cyan, bright_white
```

### Style Modifiers

```
bold, dim, italic, underline, strike, reverse
```

### Markup Syntax

```python
"[bold]Bold[/bold]"
"[red]Red text[/red]"
"[bold red on white]Combined[/bold red on white]"
"[link=https://example.com]Click here[/link]"
":emoji_name:"  # e.g., :white_check_mark:
```

## Best Practices

1. **Single Console Instance**: Create one `Console()` per application
2. **Consistent Colors**: Use color scheme consistently (green=success, red=error, yellow=warning)
3. **Clear Hierarchy**: Use panels for sections, tables for data, rules for separation
4. **Graceful Input**: Always provide defaults and validate input
5. **Progress Feedback**: Show progress for operations > 1 second
6. **Clean Exit**: Handle Ctrl+C gracefully with try/except KeyboardInterrupt

## Validation Checklist

```markdown
## CLI Interface Checklist

### Visual Design
- [ ] Consistent color scheme throughout
- [ ] Clear visual hierarchy (headers, sections, content)
- [ ] Tables used for structured data
- [ ] Panels used for important messages
- [ ] Progress indicators for long operations

### User Input
- [ ] Clear prompts with expected format
- [ ] Default values where appropriate
- [ ] Input validation with helpful errors
- [ ] Confirmation for destructive actions

### Navigation
- [ ] Clear menu structure
- [ ] Easy way to go back/cancel
- [ ] Help command available
- [ ] Quit confirmation

### Error Handling
- [ ] Errors displayed clearly (red)
- [ ] Helpful error messages
- [ ] Graceful handling of Ctrl+C
- [ ] No crashes on invalid input
```
