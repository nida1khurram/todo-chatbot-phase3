---
name: command_pattern_implementation
description: Implement Command pattern with abstract base Command class, concrete command classes for each operation with execute() method, clear separation of concerns, and dependency injection for storage.
---

# Command Pattern Implementation Skill

You are an expert at implementing the Command design pattern in Python for CLI applications with proper separation of concerns and dependency injection.

## When to Use This Skill

Apply this skill when the user:
- Needs to structure CLI operations as commands
- Wants separation between UI and business logic
- Needs undo/redo functionality
- Wants to queue or log operations
- Needs testable, decoupled operation handlers

## Command Pattern Overview

The Command pattern encapsulates operations as objects, allowing:
- **Decoupling**: Invoker doesn't know how commands work
- **Extensibility**: Easy to add new commands
- **Undo/Redo**: Commands can store state for reversal
- **Queueing**: Commands can be stored and executed later
- **Logging**: Operations can be logged automatically

## Basic Structure

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Invoker   │────▶│   Command   │────▶│  Receiver   │
│  (CLI App)  │     │ (Abstract)  │     │ (Storage)   │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │CreateCommand│ │ListCommand  │ │DeleteCommand│
    └─────────────┘ └─────────────┘ └─────────────┘
```

## Abstract Command Base

```python
"""Abstract base command class."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class CommandResult:
    """Result of command execution."""

    success: bool
    message: str
    data: Any = None
    error: str | None = None

    @classmethod
    def ok(cls, message: str, data: Any = None) -> "CommandResult":
        """Create successful result."""
        return cls(success=True, message=message, data=data)

    @classmethod
    def fail(cls, error: str) -> "CommandResult":
        """Create failure result."""
        return cls(success=False, message="", error=error)


class Command(ABC):
    """Abstract base class for all commands."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Command name for display/logging."""
        pass

    @property
    def description(self) -> str:
        """Command description for help text."""
        return ""

    @abstractmethod
    def execute(self) -> CommandResult:
        """Execute the command and return result."""
        pass

    def undo(self) -> CommandResult | None:
        """
        Undo the command if supported.

        Returns None if undo is not supported.
        """
        return None

    def can_undo(self) -> bool:
        """Check if command supports undo."""
        return False
```

## Concrete Commands

### Create Command

```python
"""Create command implementation."""

from dataclasses import dataclass
from models import TodoCreate, Todo
from storage import TodoStorage


@dataclass
class CreateTodoCommand(Command):
    """Command to create a new todo."""

    storage: TodoStorage
    title: str
    description: str | None = None
    priority: str = "medium"

    # For undo support
    _created_id: int | None = None

    @property
    def name(self) -> str:
        return "create"

    @property
    def description(self) -> str:
        return "Create a new todo item"

    def execute(self) -> CommandResult:
        """Create the todo."""
        try:
            todo_create = TodoCreate(
                title=self.title,
                description=self.description,
                priority=self.priority,
            )
            todo = self.storage.add(todo_create)
            self._created_id = todo.id
            return CommandResult.ok(
                message=f"Created todo #{todo.id}: {todo.title}",
                data=todo,
            )
        except ValueError as e:
            return CommandResult.fail(str(e))

    def can_undo(self) -> bool:
        return self._created_id is not None

    def undo(self) -> CommandResult | None:
        """Undo by deleting the created todo."""
        if self._created_id is None:
            return None
        if self.storage.delete(self._created_id):
            return CommandResult.ok(f"Undid creation of todo #{self._created_id}")
        return CommandResult.fail("Failed to undo creation")
```

### List Command

```python
"""List command implementation."""

from dataclasses import dataclass, field
from storage import TodoStorage
from models import Todo


@dataclass
class ListTodosCommand(Command):
    """Command to list todos with optional filtering."""

    storage: TodoStorage
    show_completed: bool = True
    priority: str | None = None
    search: str | None = None

    @property
    def name(self) -> str:
        return "list"

    @property
    def description(self) -> str:
        return "List todo items"

    def execute(self) -> CommandResult:
        """List todos with filtering."""
        todos = self.storage.get_all()

        # Apply filters
        if not self.show_completed:
            todos = [t for t in todos if not t.completed]

        if self.priority:
            todos = [t for t in todos if t.priority == self.priority]

        if self.search:
            search_lower = self.search.lower()
            todos = [
                t for t in todos
                if search_lower in t.title.lower()
                or (t.description and search_lower in t.description.lower())
            ]

        if not todos:
            return CommandResult.ok("No todos found", data=[])

        return CommandResult.ok(
            f"Found {len(todos)} todo(s)",
            data=todos,
        )
```

### Update Command

```python
"""Update command implementation."""

from dataclasses import dataclass
from storage import TodoStorage
from models import Todo, TodoUpdate


@dataclass
class UpdateTodoCommand(Command):
    """Command to update a todo."""

    storage: TodoStorage
    todo_id: int
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    completed: bool | None = None

    # For undo support
    _previous_state: Todo | None = None

    @property
    def name(self) -> str:
        return "update"

    @property
    def description(self) -> str:
        return "Update an existing todo"

    def execute(self) -> CommandResult:
        """Update the todo."""
        # Store previous state for undo
        self._previous_state = self.storage.get(self.todo_id)
        if self._previous_state is None:
            return CommandResult.fail(f"Todo #{self.todo_id} not found")

        update = TodoUpdate(
            title=self.title,
            description=self.description,
            priority=self.priority,
            completed=self.completed,
        )

        updated = self.storage.update(self.todo_id, update)
        if updated is None:
            return CommandResult.fail("Update failed")

        return CommandResult.ok(
            f"Updated todo #{self.todo_id}",
            data=updated,
        )

    def can_undo(self) -> bool:
        return self._previous_state is not None

    def undo(self) -> CommandResult | None:
        """Restore previous state."""
        if self._previous_state is None:
            return None

        update = TodoUpdate(
            title=self._previous_state.title,
            description=self._previous_state.description,
            priority=self._previous_state.priority,
            completed=self._previous_state.completed,
        )
        restored = self.storage.update(self.todo_id, update)

        if restored:
            return CommandResult.ok(f"Restored todo #{self.todo_id}")
        return CommandResult.fail("Failed to restore")
```

### Delete Command

```python
"""Delete command implementation."""

from dataclasses import dataclass
from storage import TodoStorage
from models import Todo, TodoCreate


@dataclass
class DeleteTodoCommand(Command):
    """Command to delete a todo."""

    storage: TodoStorage
    todo_id: int

    # For undo support
    _deleted_todo: Todo | None = None

    @property
    def name(self) -> str:
        return "delete"

    @property
    def description(self) -> str:
        return "Delete a todo item"

    def execute(self) -> CommandResult:
        """Delete the todo."""
        # Store for undo
        self._deleted_todo = self.storage.get(self.todo_id)
        if self._deleted_todo is None:
            return CommandResult.fail(f"Todo #{self.todo_id} not found")

        if self.storage.delete(self.todo_id):
            return CommandResult.ok(
                f"Deleted todo #{self.todo_id}: {self._deleted_todo.title}"
            )
        return CommandResult.fail("Delete failed")

    def can_undo(self) -> bool:
        return self._deleted_todo is not None

    def undo(self) -> CommandResult | None:
        """Restore deleted todo."""
        if self._deleted_todo is None:
            return None

        # Note: This will get a new ID
        create = TodoCreate(
            title=self._deleted_todo.title,
            description=self._deleted_todo.description,
            priority=self._deleted_todo.priority,
        )
        restored = self.storage.add(create)

        return CommandResult.ok(
            f"Restored todo as #{restored.id}",
            data=restored,
        )
```

### Complete/Toggle Command

```python
"""Toggle completion command."""

from dataclasses import dataclass
from storage import TodoStorage


@dataclass
class ToggleTodoCommand(Command):
    """Command to toggle todo completion status."""

    storage: TodoStorage
    todo_id: int

    _previous_status: bool | None = None

    @property
    def name(self) -> str:
        return "toggle"

    @property
    def description(self) -> str:
        return "Toggle todo completion status"

    def execute(self) -> CommandResult:
        """Toggle the completion status."""
        todo = self.storage.get(self.todo_id)
        if todo is None:
            return CommandResult.fail(f"Todo #{self.todo_id} not found")

        self._previous_status = todo.completed
        new_status = not todo.completed

        updated = self.storage.update(
            self.todo_id,
            TodoUpdate(completed=new_status)
        )

        if updated:
            status_text = "completed" if new_status else "incomplete"
            return CommandResult.ok(
                f"Marked todo #{self.todo_id} as {status_text}",
                data=updated,
            )
        return CommandResult.fail("Toggle failed")

    def can_undo(self) -> bool:
        return self._previous_status is not None

    def undo(self) -> CommandResult | None:
        """Restore previous completion status."""
        if self._previous_status is None:
            return None

        self.storage.update(
            self.todo_id,
            TodoUpdate(completed=self._previous_status)
        )
        return CommandResult.ok(f"Restored todo #{self.todo_id} status")
```

## Command Invoker

```python
"""Command invoker with history and undo support."""

from collections import deque
from rich.console import Console

console = Console()


class CommandInvoker:
    """Executes commands and maintains history for undo."""

    def __init__(self, max_history: int = 50) -> None:
        self._history: deque[Command] = deque(maxlen=max_history)
        self._redo_stack: list[Command] = []

    def execute(self, command: Command) -> CommandResult:
        """Execute a command and store in history if undoable."""
        result = command.execute()

        if result.success and command.can_undo():
            self._history.append(command)
            self._redo_stack.clear()  # Clear redo on new command

        return result

    def undo(self) -> CommandResult | None:
        """Undo the last command."""
        if not self._history:
            return CommandResult.fail("Nothing to undo")

        command = self._history.pop()
        result = command.undo()

        if result and result.success:
            self._redo_stack.append(command)

        return result

    def redo(self) -> CommandResult | None:
        """Redo the last undone command."""
        if not self._redo_stack:
            return CommandResult.fail("Nothing to redo")

        command = self._redo_stack.pop()
        result = command.execute()

        if result.success and command.can_undo():
            self._history.append(command)

        return result

    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self._history) > 0

    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self._redo_stack) > 0

    @property
    def history_count(self) -> int:
        """Get number of commands in history."""
        return len(self._history)
```

## Command Factory

```python
"""Factory for creating commands with dependency injection."""

from storage import TodoStorage


class CommandFactory:
    """Factory for creating command instances."""

    def __init__(self, storage: TodoStorage) -> None:
        self._storage = storage

    def create_todo(
        self,
        title: str,
        description: str | None = None,
        priority: str = "medium",
    ) -> CreateTodoCommand:
        """Create a CreateTodoCommand."""
        return CreateTodoCommand(
            storage=self._storage,
            title=title,
            description=description,
            priority=priority,
        )

    def list_todos(
        self,
        show_completed: bool = True,
        priority: str | None = None,
        search: str | None = None,
    ) -> ListTodosCommand:
        """Create a ListTodosCommand."""
        return ListTodosCommand(
            storage=self._storage,
            show_completed=show_completed,
            priority=priority,
            search=search,
        )

    def update_todo(
        self,
        todo_id: int,
        title: str | None = None,
        description: str | None = None,
        priority: str | None = None,
        completed: bool | None = None,
    ) -> UpdateTodoCommand:
        """Create an UpdateTodoCommand."""
        return UpdateTodoCommand(
            storage=self._storage,
            todo_id=todo_id,
            title=title,
            description=description,
            priority=priority,
            completed=completed,
        )

    def delete_todo(self, todo_id: int) -> DeleteTodoCommand:
        """Create a DeleteTodoCommand."""
        return DeleteTodoCommand(
            storage=self._storage,
            todo_id=todo_id,
        )

    def toggle_todo(self, todo_id: int) -> ToggleTodoCommand:
        """Create a ToggleTodoCommand."""
        return ToggleTodoCommand(
            storage=self._storage,
            todo_id=todo_id,
        )
```

## Complete Application Structure

```python
"""Complete CLI application using Command pattern."""

from rich.console import Console
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.table import Table
from rich.panel import Panel

from storage import TodoStorage
from commands import (
    Command,
    CommandResult,
    CommandInvoker,
    CommandFactory,
)


class TodoApp:
    """Todo CLI application."""

    def __init__(self) -> None:
        self.console = Console()
        self.storage = TodoStorage()
        self.invoker = CommandInvoker()
        self.factory = CommandFactory(self.storage)
        self.running = True

    def run(self) -> None:
        """Main application loop."""
        self.show_welcome()

        while self.running:
            self.show_menu()
            choice = self.get_choice()
            self.handle_choice(choice)

    def show_welcome(self) -> None:
        """Display welcome message."""
        self.console.print(
            Panel("[bold cyan]Todo Manager[/bold cyan]", border_style="blue")
        )

    def show_menu(self) -> None:
        """Display main menu."""
        self.console.print("\n[bold]Commands:[/bold]")
        self.console.print("  [cyan]1[/cyan] - Add todo")
        self.console.print("  [cyan]2[/cyan] - List todos")
        self.console.print("  [cyan]3[/cyan] - Complete todo")
        self.console.print("  [cyan]4[/cyan] - Delete todo")
        if self.invoker.can_undo():
            self.console.print("  [cyan]u[/cyan] - Undo")
        if self.invoker.can_redo():
            self.console.print("  [cyan]r[/cyan] - Redo")
        self.console.print("  [cyan]q[/cyan] - Quit")

    def get_choice(self) -> str:
        """Get user menu choice."""
        choices = ["1", "2", "3", "4", "q"]
        if self.invoker.can_undo():
            choices.append("u")
        if self.invoker.can_redo():
            choices.append("r")

        return Prompt.ask("\nChoice", choices=choices, show_choices=False)

    def handle_choice(self, choice: str) -> None:
        """Route choice to appropriate handler."""
        handlers = {
            "1": self.handle_add,
            "2": self.handle_list,
            "3": self.handle_complete,
            "4": self.handle_delete,
            "u": self.handle_undo,
            "r": self.handle_redo,
            "q": self.handle_quit,
        }
        handler = handlers.get(choice)
        if handler:
            handler()

    def handle_add(self) -> None:
        """Handle add todo command."""
        title = Prompt.ask("Title")
        priority = Prompt.ask(
            "Priority",
            choices=["low", "medium", "high"],
            default="medium",
        )

        command = self.factory.create_todo(title=title, priority=priority)
        result = self.invoker.execute(command)
        self.show_result(result)

    def handle_list(self) -> None:
        """Handle list todos command."""
        command = self.factory.list_todos()
        result = self.invoker.execute(command)

        if result.success and result.data:
            self.display_todos(result.data)
        else:
            self.console.print("[dim]No todos found[/dim]")

    def handle_complete(self) -> None:
        """Handle complete todo command."""
        todo_id = IntPrompt.ask("Todo ID")
        command = self.factory.toggle_todo(todo_id)
        result = self.invoker.execute(command)
        self.show_result(result)

    def handle_delete(self) -> None:
        """Handle delete todo command."""
        todo_id = IntPrompt.ask("Todo ID")

        if Confirm.ask(f"Delete todo #{todo_id}?"):
            command = self.factory.delete_todo(todo_id)
            result = self.invoker.execute(command)
            self.show_result(result)

    def handle_undo(self) -> None:
        """Handle undo command."""
        result = self.invoker.undo()
        if result:
            self.show_result(result)

    def handle_redo(self) -> None:
        """Handle redo command."""
        result = self.invoker.redo()
        if result:
            self.show_result(result)

    def handle_quit(self) -> None:
        """Handle quit command."""
        if Confirm.ask("Quit?"):
            self.running = False
            self.console.print("[yellow]Goodbye![/yellow]")

    def show_result(self, result: CommandResult) -> None:
        """Display command result."""
        if result.success:
            self.console.print(f"[green]{result.message}[/green]")
        else:
            self.console.print(f"[red]Error: {result.error}[/red]")

    def display_todos(self, todos: list) -> None:
        """Display todos in a table."""
        table = Table(title="Todos")
        table.add_column("ID", style="dim")
        table.add_column("Title")
        table.add_column("Priority")
        table.add_column("Status")

        for todo in todos:
            status = "[green]✓[/green]" if todo.completed else "[ ]"
            priority_colors = {"high": "red", "medium": "yellow", "low": "green"}
            priority = f"[{priority_colors[todo.priority]}]{todo.priority}[/]"

            table.add_row(str(todo.id), todo.title, priority, status)

        self.console.print(table)


def main() -> None:
    """Entry point."""
    app = TodoApp()
    app.run()


if __name__ == "__main__":
    main()
```

## Testing Commands

```python
"""Tests for command pattern implementation."""

import pytest
from storage import TodoStorage
from commands import (
    CreateTodoCommand,
    ListTodosCommand,
    UpdateTodoCommand,
    DeleteTodoCommand,
    CommandInvoker,
    CommandFactory,
)


class TestCreateTodoCommand:
    """Tests for CreateTodoCommand."""

    @pytest.fixture
    def storage(self) -> TodoStorage:
        return TodoStorage()

    def test_execute_creates_todo(self, storage: TodoStorage) -> None:
        """Test command creates todo successfully."""
        command = CreateTodoCommand(
            storage=storage,
            title="Test Todo",
            priority="high",
        )

        result = command.execute()

        assert result.success
        assert result.data.title == "Test Todo"
        assert storage.count() == 1

    def test_undo_deletes_created_todo(self, storage: TodoStorage) -> None:
        """Test undo removes the created todo."""
        command = CreateTodoCommand(storage=storage, title="Test")
        command.execute()

        result = command.undo()

        assert result.success
        assert storage.count() == 0


class TestCommandInvoker:
    """Tests for CommandInvoker."""

    @pytest.fixture
    def storage(self) -> TodoStorage:
        return TodoStorage()

    @pytest.fixture
    def invoker(self) -> CommandInvoker:
        return CommandInvoker()

    def test_undo_restores_previous_state(
        self,
        storage: TodoStorage,
        invoker: CommandInvoker,
    ) -> None:
        """Test undo restores state."""
        command = CreateTodoCommand(storage=storage, title="Test")
        invoker.execute(command)

        invoker.undo()

        assert storage.count() == 0

    def test_redo_reapplies_command(
        self,
        storage: TodoStorage,
        invoker: CommandInvoker,
    ) -> None:
        """Test redo reapplies undone command."""
        command = CreateTodoCommand(storage=storage, title="Test")
        invoker.execute(command)
        invoker.undo()

        invoker.redo()

        assert storage.count() == 1
```

## Validation Checklist

```markdown
## Command Pattern Checklist

### Command Structure
- [ ] Abstract Command base class defined
- [ ] CommandResult class for standardized returns
- [ ] name and description properties on commands
- [ ] execute() method returns CommandResult

### Concrete Commands
- [ ] One command class per operation
- [ ] Commands receive dependencies via constructor
- [ ] Commands validate input before executing
- [ ] Commands return meaningful error messages

### Undo Support
- [ ] can_undo() method on commands
- [ ] undo() method stores/restores state
- [ ] Previous state captured in execute()

### Invoker
- [ ] Command history maintained
- [ ] Undo/redo functionality works
- [ ] History size limited

### Factory
- [ ] Central factory for command creation
- [ ] Dependencies injected into commands
- [ ] Clean API for command creation

### Testing
- [ ] Each command tested independently
- [ ] Undo functionality tested
- [ ] Error cases tested
```
