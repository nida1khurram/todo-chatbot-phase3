---
name: data_validation
description: Implement Pydantic BaseModel classes with Field validation for min/max length, custom field_validator decorators for business rules, type hints, and clear error messages for invalid inputs.
---

# Data Validation Skill

You are an expert at implementing data validation using Pydantic v2 with proper type hints, field constraints, custom validators, and user-friendly error messages.

## When to Use This Skill

Apply this skill when the user:
- Needs to validate user input or API data
- Wants to create data models with constraints
- Needs custom validation logic for business rules
- Wants type-safe data structures with validation
- Needs to handle and display validation errors clearly

## Installation

```bash
# With UV
uv add pydantic

# For settings/environment variables
uv add pydantic-settings
```

## Pydantic v2 Basics

### Simple Model

```python
"""Basic Pydantic model with type hints."""

from pydantic import BaseModel


class User(BaseModel):
    """User data model."""

    id: int
    name: str
    email: str
    age: int | None = None  # Optional field with default
    active: bool = True     # Required field with default


# Usage
user = User(id=1, name="John", email="john@example.com")
print(user.model_dump())  # {'id': 1, 'name': 'John', 'email': 'john@example.com', 'age': None, 'active': True}
```

## Field Validation with Constraints

### String Constraints

```python
"""String field validation with length and pattern constraints."""

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """User creation model with string validation."""

    username: str = Field(
        ...,  # Required field (no default)
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Username (alphanumeric and underscores only)",
        examples=["john_doe", "user123"],
    )

    email: str = Field(
        ...,
        min_length=5,
        max_length=255,
        description="User's email address",
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (minimum 8 characters)",
    )

    bio: str | None = Field(
        default=None,
        max_length=500,
        description="Optional user biography",
    )
```

### Numeric Constraints

```python
"""Numeric field validation with range constraints."""

from pydantic import BaseModel, Field
from decimal import Decimal


class Product(BaseModel):
    """Product model with numeric validation."""

    id: int = Field(..., gt=0, description="Product ID (positive integer)")

    name: str = Field(..., min_length=1, max_length=200)

    price: Decimal = Field(
        ...,
        gt=0,
        le=1000000,
        decimal_places=2,
        description="Price in dollars (0.01 to 1,000,000.00)",
    )

    quantity: int = Field(
        default=0,
        ge=0,
        le=10000,
        description="Stock quantity (0 to 10,000)",
    )

    discount_percent: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Discount percentage (0-100)",
    )

    rating: float | None = Field(
        default=None,
        ge=0.0,
        le=5.0,
        description="Average rating (0.0 to 5.0)",
    )


class OrderItem(BaseModel):
    """Order item with quantity constraints."""

    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=100, description="Quantity (1-100)")
    unit_price: Decimal = Field(..., gt=0)
```

### Field Constraint Reference

| Constraint | Type | Description |
|------------|------|-------------|
| `gt` | numeric | Greater than |
| `ge` | numeric | Greater than or equal |
| `lt` | numeric | Less than |
| `le` | numeric | Less than or equal |
| `multiple_of` | numeric | Must be multiple of value |
| `min_length` | string/list | Minimum length |
| `max_length` | string/list | Maximum length |
| `pattern` | string | Regex pattern |
| `strict` | any | Disable type coercion |

## Custom Validators

### Field Validators (Single Field)

```python
"""Custom validators for single fields."""

from pydantic import BaseModel, Field, field_validator


class UserRegistration(BaseModel):
    """User registration with custom validation."""

    username: str = Field(..., min_length=3, max_length=50)
    email: str
    password: str = Field(..., min_length=8)
    password_confirm: str
    age: int | None = None

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        """Ensure username contains only allowed characters."""
        if not v.replace("_", "").isalnum():
            raise ValueError("Username must be alphanumeric (underscores allowed)")
        if v[0].isdigit():
            raise ValueError("Username cannot start with a number")
        return v.lower()  # Normalize to lowercase

    @field_validator("email")
    @classmethod
    def email_valid(cls, v: str) -> str:
        """Validate email format."""
        if "@" not in v:
            raise ValueError("Invalid email format")
        local, domain = v.rsplit("@", 1)
        if not local or not domain or "." not in domain:
            raise ValueError("Invalid email format")
        return v.lower()

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Validate password strength."""
        errors = []
        if not any(c.isupper() for c in v):
            errors.append("at least one uppercase letter")
        if not any(c.islower() for c in v):
            errors.append("at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            errors.append("at least one digit")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            errors.append("at least one special character")

        if errors:
            raise ValueError(f"Password must contain {', '.join(errors)}")
        return v

    @field_validator("age")
    @classmethod
    def age_valid(cls, v: int | None) -> int | None:
        """Validate age if provided."""
        if v is not None:
            if v < 13:
                raise ValueError("Must be at least 13 years old")
            if v > 120:
                raise ValueError("Invalid age")
        return v
```

### Model Validators (Multiple Fields)

```python
"""Validators that access multiple fields."""

from pydantic import BaseModel, Field, field_validator, model_validator


class DateRange(BaseModel):
    """Date range with cross-field validation."""

    start_date: str
    end_date: str

    @model_validator(mode="after")
    def check_dates(self) -> "DateRange":
        """Ensure end_date is after start_date."""
        if self.start_date >= self.end_date:
            raise ValueError("end_date must be after start_date")
        return self


class PasswordChange(BaseModel):
    """Password change with confirmation validation."""

    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Validate new password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain a digit")
        return v

    @model_validator(mode="after")
    def passwords_match(self) -> "PasswordChange":
        """Ensure new password and confirmation match."""
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self

    @model_validator(mode="after")
    def new_differs_from_current(self) -> "PasswordChange":
        """Ensure new password differs from current."""
        if self.new_password == self.current_password:
            raise ValueError("New password must be different from current password")
        return self


class PaymentMethod(BaseModel):
    """Payment with conditional validation."""

    method: str = Field(..., pattern=r"^(card|bank|paypal)$")
    card_number: str | None = None
    bank_account: str | None = None
    paypal_email: str | None = None

    @model_validator(mode="after")
    def validate_payment_details(self) -> "PaymentMethod":
        """Ensure required payment details are provided."""
        if self.method == "card" and not self.card_number:
            raise ValueError("Card number required for card payment")
        if self.method == "bank" and not self.bank_account:
            raise ValueError("Bank account required for bank payment")
        if self.method == "paypal" and not self.paypal_email:
            raise ValueError("PayPal email required for PayPal payment")
        return self
```

### Before Validators (Pre-processing)

```python
"""Validators that transform data before validation."""

from pydantic import BaseModel, Field, field_validator, BeforeValidator
from typing import Annotated


def strip_whitespace(v: str) -> str:
    """Strip whitespace from string."""
    return v.strip() if isinstance(v, str) else v


def normalize_phone(v: str) -> str:
    """Normalize phone number to digits only."""
    if isinstance(v, str):
        return "".join(c for c in v if c.isdigit())
    return v


# Using Annotated type with BeforeValidator
StrippedStr = Annotated[str, BeforeValidator(strip_whitespace)]
PhoneNumber = Annotated[str, BeforeValidator(normalize_phone)]


class Contact(BaseModel):
    """Contact with pre-processing validators."""

    name: StrippedStr = Field(..., min_length=1, max_length=100)
    phone: PhoneNumber = Field(..., min_length=10, max_length=15)
    email: StrippedStr

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Normalize email to lowercase."""
        if isinstance(v, str):
            return v.strip().lower()
        return v


class TagList(BaseModel):
    """Model with list preprocessing."""

    tags: list[str] = Field(default_factory=list)

    @field_validator("tags", mode="before")
    @classmethod
    def parse_tags(cls, v: str | list[str]) -> list[str]:
        """Accept comma-separated string or list."""
        if isinstance(v, str):
            return [tag.strip() for tag in v.split(",") if tag.strip()]
        return v
```

## Error Handling

### Catching Validation Errors

```python
"""Handling and displaying validation errors."""

from pydantic import BaseModel, Field, ValidationError
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class UserInput(BaseModel):
    """User input model."""

    username: str = Field(..., min_length=3, max_length=20)
    email: str = Field(..., min_length=5)
    age: int = Field(..., ge=13, le=120)


def validate_user_input(data: dict) -> UserInput | None:
    """Validate user input with error handling."""
    try:
        return UserInput(**data)
    except ValidationError as e:
        display_validation_errors(e)
        return None


def display_validation_errors(error: ValidationError) -> None:
    """Display validation errors in a user-friendly format."""
    console.print("\n[bold red]Validation Error[/bold red]\n")

    table = Table(show_header=True, header_style="bold red")
    table.add_column("Field", style="cyan")
    table.add_column("Error", style="white")

    for err in error.errors():
        field = " -> ".join(str(loc) for loc in err["loc"])
        message = err["msg"]
        table.add_row(field, message)

    console.print(table)
    console.print()


def display_errors_simple(error: ValidationError) -> None:
    """Display errors as a simple list."""
    console.print("\n[bold red]Please fix the following errors:[/bold red]\n")

    for err in error.errors():
        field = err["loc"][-1] if err["loc"] else "input"
        message = err["msg"]
        console.print(f"  [red]•[/red] [cyan]{field}[/cyan]: {message}")

    console.print()


# Usage example
def get_validated_user() -> UserInput | None:
    """Interactive user input with validation."""
    from rich.prompt import Prompt, IntPrompt

    data = {
        "username": Prompt.ask("Username"),
        "email": Prompt.ask("Email"),
        "age": IntPrompt.ask("Age"),
    }

    return validate_user_input(data)
```

### Custom Error Messages

```python
"""Models with custom error messages."""

from pydantic import BaseModel, Field, field_validator


class CreateAccount(BaseModel):
    """Account creation with custom error messages."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
        json_schema_extra={
            "error_messages": {
                "min_length": "Username must be at least 3 characters",
                "max_length": "Username cannot exceed 20 characters",
            }
        },
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username with custom messages."""
        if not v[0].isalpha():
            raise ValueError("Username must start with a letter")
        if not v.replace("_", "").isalnum():
            raise ValueError(
                "Username can only contain letters, numbers, and underscores"
            )
        if "__" in v:
            raise ValueError("Username cannot contain consecutive underscores")
        return v


class Amount(BaseModel):
    """Amount with context-specific error messages."""

    value: float = Field(..., gt=0)
    currency: str = Field(..., pattern=r"^[A-Z]{3}$")

    @field_validator("value")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        """Validate amount with helpful message."""
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        if v > 1_000_000:
            raise ValueError("Amount cannot exceed 1,000,000")
        # Round to 2 decimal places
        return round(v, 2)

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Validate currency code."""
        valid_currencies = {"USD", "EUR", "GBP", "JPY", "CAD"}
        if v not in valid_currencies:
            raise ValueError(
                f"Unsupported currency. Valid options: {', '.join(sorted(valid_currencies))}"
            )
        return v
```

## Common Patterns

### Immutable Models

```python
"""Immutable (frozen) models."""

from pydantic import BaseModel, ConfigDict


class ImmutableUser(BaseModel):
    """User that cannot be modified after creation."""

    model_config = ConfigDict(frozen=True)

    id: int
    username: str
    email: str


# Usage
user = ImmutableUser(id=1, username="john", email="john@example.com")
# user.username = "jane"  # This would raise an error
```

### Models with Aliases

```python
"""Models with field aliases for API compatibility."""

from pydantic import BaseModel, Field


class APIResponse(BaseModel):
    """Model with aliases for JSON keys."""

    user_id: int = Field(..., alias="userId")
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    email_address: str = Field(..., alias="emailAddress")

    model_config = ConfigDict(populate_by_name=True)


# Can use either name
response = APIResponse(userId=1, firstName="John", lastName="Doe", emailAddress="john@example.com")
# Or
response = APIResponse(user_id=1, first_name="John", last_name="Doe", email_address="john@example.com")
```

### Nested Models

```python
"""Nested model validation."""

from pydantic import BaseModel, Field
from datetime import datetime


class Address(BaseModel):
    """Address model."""

    street: str = Field(..., min_length=1, max_length=200)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=2, max_length=50)
    postal_code: str = Field(..., pattern=r"^\d{5}(-\d{4})?$")
    country: str = Field(default="US", pattern=r"^[A-Z]{2}$")


class Person(BaseModel):
    """Person with nested address."""

    name: str = Field(..., min_length=1, max_length=100)
    email: str
    address: Address
    shipping_address: Address | None = None


class Order(BaseModel):
    """Order with nested models."""

    id: int = Field(..., gt=0)
    customer: Person
    items: list[dict] = Field(..., min_length=1)
    created_at: datetime = Field(default_factory=datetime.now)
    total: float = Field(..., gt=0)
```

### Enum Validation

```python
"""Validation with enums."""

from enum import Enum
from pydantic import BaseModel, Field


class Status(str, Enum):
    """Task status enum."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Priority(str, Enum):
    """Task priority enum."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Task(BaseModel):
    """Task with enum fields."""

    id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=200)
    status: Status = Field(default=Status.PENDING)
    priority: Priority = Field(default=Priority.MEDIUM)


# Usage
task = Task(id=1, title="Complete report", priority="high")  # String coerced to enum
task = Task(id=2, title="Review code", priority=Priority.LOW)  # Direct enum
```

### Generic Validators

```python
"""Reusable validation functions."""

from typing import Annotated
from pydantic import BaseModel, Field, BeforeValidator, AfterValidator


def to_lowercase(v: str) -> str:
    """Convert string to lowercase."""
    return v.lower() if isinstance(v, str) else v


def strip_whitespace(v: str) -> str:
    """Strip whitespace from string."""
    return v.strip() if isinstance(v, str) else v


def must_not_be_empty(v: str) -> str:
    """Ensure string is not empty after stripping."""
    if not v:
        raise ValueError("Value cannot be empty")
    return v


# Reusable annotated types
CleanString = Annotated[
    str,
    BeforeValidator(strip_whitespace),
    AfterValidator(must_not_be_empty),
]

NormalizedEmail = Annotated[
    str,
    BeforeValidator(strip_whitespace),
    BeforeValidator(to_lowercase),
]

Username = Annotated[
    str,
    BeforeValidator(strip_whitespace),
    BeforeValidator(to_lowercase),
    Field(min_length=3, max_length=50, pattern=r"^[a-z0-9_]+$"),
]


class UserProfile(BaseModel):
    """Profile using reusable types."""

    username: Username
    email: NormalizedEmail
    display_name: CleanString = Field(..., max_length=100)
```

## Complete Example: Todo Item

```python
"""Complete example: Todo item with full validation."""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict


class Priority(str, Enum):
    """Todo priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TodoCreate(BaseModel):
    """Model for creating a new todo."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Todo title (1-200 characters)",
    )
    description: str | None = Field(
        default=None,
        max_length=2000,
        description="Optional detailed description",
    )
    priority: Priority = Field(
        default=Priority.MEDIUM,
        description="Task priority level",
    )
    due_date: datetime | None = Field(
        default=None,
        description="Optional due date",
    )
    tags: list[str] = Field(
        default_factory=list,
        max_length=10,
        description="Optional tags (max 10)",
    )

    @field_validator("title")
    @classmethod
    def title_not_whitespace(cls, v: str) -> str:
        """Ensure title is not just whitespace."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("Title cannot be empty or whitespace only")
        return stripped

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Validate and normalize tags."""
        normalized = []
        for tag in v:
            tag = tag.strip().lower()
            if tag:
                if len(tag) > 50:
                    raise ValueError(f"Tag '{tag[:20]}...' exceeds 50 characters")
                if not tag.replace("-", "").replace("_", "").isalnum():
                    raise ValueError(f"Tag '{tag}' contains invalid characters")
                normalized.append(tag)
        return list(set(normalized))  # Remove duplicates

    @field_validator("due_date")
    @classmethod
    def due_date_not_past(cls, v: datetime | None) -> datetime | None:
        """Ensure due date is not in the past."""
        if v is not None and v < datetime.now():
            raise ValueError("Due date cannot be in the past")
        return v


class TodoUpdate(BaseModel):
    """Model for updating a todo (all fields optional)."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    priority: Priority | None = None
    due_date: datetime | None = None
    completed: bool | None = None
    tags: list[str] | None = Field(default=None, max_length=10)

    @model_validator(mode="after")
    def at_least_one_field(self) -> "TodoUpdate":
        """Ensure at least one field is being updated."""
        if all(
            getattr(self, field) is None
            for field in self.model_fields
        ):
            raise ValueError("At least one field must be provided for update")
        return self


class Todo(BaseModel):
    """Complete todo model with all fields."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None = None
    priority: Priority = Priority.MEDIUM
    due_date: datetime | None = None
    completed: bool = False
    tags: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
```

## Validation Checklist

```markdown
## Data Validation Checklist

### Model Definition
- [ ] All fields have appropriate types
- [ ] Required vs optional fields clearly defined
- [ ] Default values set where appropriate
- [ ] Field descriptions added for documentation

### Constraints
- [ ] String length limits (min_length, max_length)
- [ ] Numeric ranges (gt, ge, lt, le)
- [ ] Pattern validation for formatted strings
- [ ] List length limits where needed

### Custom Validators
- [ ] Business rules implemented with field_validator
- [ ] Cross-field validation with model_validator
- [ ] Pre-processing with mode="before" where needed
- [ ] Clear, actionable error messages

### Error Handling
- [ ] ValidationError caught appropriately
- [ ] Errors displayed in user-friendly format
- [ ] Field names mapped to display names
- [ ] All error paths tested
```
