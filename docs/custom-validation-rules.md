# Writing Custom Validation Rules

This guide explains how to create custom validation rules for the Unified Agent System's validation framework.

## Overview

The validation framework provides a flexible rule-based system that allows you to create custom validation logic for any data type or business requirement.

## Validation Rule Structure

A validation rule consists of:
- **Type**: The validation type (from `ValidationType` enum)
- **Parameters**: Configuration for the validation
- **Error Message**: Custom error message (optional)

```python
from unified.validation import ValidationRule, ValidationType

rule = ValidationRule(
    validation_type=ValidationType.CUSTOM,
    params={'validator': my_validator_function},
    error_message="Custom validation failed: {field} must be {requirement}"
)
```

## Built-in Validation Types

### 1. REQUIRED
Ensures a field is present and not empty.

```python
ValidationRule(ValidationType.REQUIRED)
```

### 2. TYPE
Validates field type.

```python
ValidationRule(ValidationType.TYPE, {'type': str})
ValidationRule(ValidationType.TYPE, {'type': (int, float)})  # Multiple types
```

### 3. RANGE
Validates numeric values are within a range.

```python
ValidationRule(ValidationType.RANGE, {'min': 0, 'max': 100})
ValidationRule(ValidationType.RANGE, {'min': 0})  # Only minimum
```

### 4. PATTERN
Validates string matches a regex pattern.

```python
ValidationRule(ValidationType.PATTERN, {
    'pattern': r'^[A-Z][a-z]+$'
})
```

### 5. LENGTH
Validates string or collection length.

```python
ValidationRule(ValidationType.LENGTH, {'min': 3, 'max': 50})
```

### 6. ENUM
Validates value is in a set of allowed values.

```python
ValidationRule(ValidationType.ENUM, {
    'values': ['active', 'inactive', 'pending']
})
```

### 7. CUSTOM
Uses a custom validation function.

```python
def validate_even(value, data):
    """Value must be even number"""
    return value % 2 == 0

ValidationRule(ValidationType.CUSTOM, {
    'validator': validate_even
}, "Value must be an even number")
```

## Creating Custom Validators

### Simple Custom Validator

```python
def validate_positive(value, data):
    """Ensure value is positive"""
    return value > 0

# Usage
rule = ValidationRule(
    ValidationType.CUSTOM,
    {'validator': validate_positive},
    "{field} must be positive"
)
```

### Complex Custom Validator with Context

```python
def validate_date_range(value, data):
    """Ensure end_date is after start_date"""
    if 'start_date' not in data:
        return True  # Skip if start_date not present
    
    from datetime import datetime
    start = datetime.fromisoformat(data['start_date'])
    end = datetime.fromisoformat(value)
    return end > start

# Usage in schema
schema = ValidationSchema()
schema.add_field('end_date', [
    ValidationRule(ValidationType.REQUIRED),
    ValidationRule(ValidationType.CUSTOM, {
        'validator': validate_date_range
    }, "End date must be after start date")
])
```

### Async Custom Validator

For validators that need to perform async operations:

```python
async def validate_unique_username(value, data):
    """Check username is unique in database"""
    # Async database check
    exists = await db.users.find_one({'username': value})
    return exists is None

# Wrap for sync validation
def validate_username_sync(value, data):
    import asyncio
    return asyncio.run(validate_unique_username(value, data))

rule = ValidationRule(
    ValidationType.CUSTOM,
    {'validator': validate_username_sync},
    "Username already exists"
)
```

## Creating Validation Schemas

### Basic Schema

```python
from unified.validation import ValidationSchema, ValidationRule, ValidationType

# Create schema
user_schema = ValidationSchema()

# Add field validations
user_schema.add_field('username', [
    ValidationRule(ValidationType.REQUIRED),
    ValidationRule(ValidationType.TYPE, {'type': str}),
    ValidationRule(ValidationType.LENGTH, {'min': 3, 'max': 20}),
    ValidationRule(ValidationType.PATTERN, {
        'pattern': r'^[a-zA-Z0-9_]+$'
    }, "Username can only contain letters, numbers, and underscores")
])

user_schema.add_field('email', [
    ValidationRule(ValidationType.REQUIRED),
    ValidationRule(ValidationType.TYPE, {'type': str}),
    ValidationRule(ValidationType.CUSTOM, {
        'validator': lambda v, d: '@' in v and '.' in v.split('@')[1]
    }, "Invalid email format")
])

user_schema.add_field('age', [
    ValidationRule(ValidationType.TYPE, {'type': int}),
    ValidationRule(ValidationType.RANGE, {'min': 13, 'max': 120})
])
```

### Registering Custom Schemas

```python
from unified.validation import get_input_validator

validator = get_input_validator()

# Register custom schema
validator.register_schema('user_registration', user_schema)

# Use the schema
errors = validator.validate('user_registration', {
    'username': 'john_doe',
    'email': 'john@example.com',
    'age': 25
})
```

## Advanced Patterns

### Conditional Validation

```python
def validate_payment_method(value, data):
    """Validate payment details based on payment type"""
    payment_type = data.get('payment_type')
    
    if payment_type == 'credit_card':
        # Check for credit card fields
        return all(key in value for key in ['number', 'cvv', 'expiry'])
    elif payment_type == 'bank_transfer':
        # Check for bank fields
        return all(key in value for key in ['account', 'routing'])
    
    return True

schema.add_field('payment_details', [
    ValidationRule(ValidationType.CUSTOM, {
        'validator': validate_payment_method
    }, "Invalid payment details for selected payment type")
])
```

### Cross-Field Validation

```python
def validate_password_confirmation(value, data):
    """Ensure password matches confirmation"""
    return value == data.get('password')

schema.add_field('password_confirmation', [
    ValidationRule(ValidationType.CUSTOM, {
        'validator': validate_password_confirmation
    }, "Password confirmation does not match")
])
```

### Nested Object Validation

```python
def validate_address(value, data):
    """Validate address object"""
    if not isinstance(value, dict):
        return False
    
    required_fields = ['street', 'city', 'postal_code']
    return all(field in value and value[field] for field in required_fields)

schema.add_field('address', [
    ValidationRule(ValidationType.CUSTOM, {
        'validator': validate_address
    }, "Address must include street, city, and postal code")
])
```

## Error Message Formatting

Error messages support placeholders:
- `{field}`: The field name being validated
- `{value}`: The actual value that failed validation
- Any parameter from the rule's params dict

```python
rule = ValidationRule(
    ValidationType.RANGE,
    {'min': 1, 'max': 10},
    "{field} must be between {min} and {max}, got {value}"
)
```

## Integration Examples

### With Tool Framework

```python
from unified.tools import Tool, ToolContext
from unified.validation import ValidationSchema, ValidationRule, ValidationType

class DataProcessingTool(Tool):
    def __init__(self):
        super().__init__("data_processor", ...)
        self.schema = self._create_schema()
    
    def _create_schema(self):
        schema = ValidationSchema()
        schema.add_field('input_file', [
            ValidationRule(ValidationType.REQUIRED),
            ValidationRule(ValidationType.CUSTOM, {
                'validator': lambda v, d: Path(v).exists()
            }, "Input file does not exist")
        ])
        return schema
    
    def validate_input(self, **kwargs):
        return self.schema.validate(kwargs)
```

### With Command Validation

```python
from unified.validation import get_command_validator

validator = get_command_validator()

# Add custom allowed command
validator.allowed_commands.add('my_tool')

# Add custom forbidden pattern
import re
validator.forbidden_patterns.append(
    re.compile(r'my_dangerous_pattern')
)
```

## Best Practices

1. **Order Matters**: Place REQUIRED validation first to avoid unnecessary checks on missing fields.

2. **Fail Fast**: Order validations from least to most expensive (type checks before database lookups).

3. **Clear Messages**: Provide specific error messages that guide users to fix the issue.

4. **Reusable Validators**: Create utility functions for common validations:

```python
# utils/validators.py
def create_length_validator(min_len, max_len):
    def validator(value, data):
        return min_len <= len(value) <= max_len
    return validator

def create_regex_validator(pattern):
    import re
    compiled = re.compile(pattern)
    def validator(value, data):
        return bool(compiled.match(str(value)))
    return validator
```

5. **Type Safety**: Always validate type before other validations:

```python
schema.add_field('count', [
    ValidationRule(ValidationType.TYPE, {'type': int}),  # First
    ValidationRule(ValidationType.RANGE, {'min': 0})     # Then range
])
```

6. **Documentation**: Document complex validators:

```python
def validate_business_hours(value, data):
    """
    Validates business hours format.
    Expected format: "HH:MM-HH:MM" (e.g., "09:00-17:00")
    
    Args:
        value: The hours string to validate
        data: Full data object (unused)
    
    Returns:
        bool: True if valid format and end > start
    """
    # Implementation...
```

## Testing Custom Validators

```python
import pytest
from unified.validation import ValidationSchema, ValidationRule, ValidationType

def test_custom_validator():
    # Create test validator
    def validate_multiple_of_five(value, data):
        return value % 5 == 0
    
    # Create schema
    schema = ValidationSchema()
    schema.add_field('number', [
        ValidationRule(ValidationType.CUSTOM, {
            'validator': validate_multiple_of_five
        }, "Must be multiple of 5")
    ])
    
    # Test valid
    assert schema.validate({'number': 10}) == []
    
    # Test invalid
    errors = schema.validate({'number': 7})
    assert len(errors) == 1
    assert "Must be multiple of 5" in errors[0]
```

## Common Patterns Library

```python
# Common validation patterns
PATTERNS = {
    'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    'url': r'^https?://[^\s]+$',
    'phone': r'^\+?1?\d{9,15}$',
    'uuid': r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
    'slug': r'^[a-z0-9]+(?:-[a-z0-9]+)*$',
    'hex_color': r'^#[0-9A-Fa-f]{6}$',
    'ipv4': r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$',
    'semantic_version': r'^\d+\.\d+\.\d+$'
}

# Usage
schema.add_field('email', [
    ValidationRule(ValidationType.PATTERN, {
        'pattern': PATTERNS['email']
    })
])
```

## Debugging Validation Errors

Enable debug logging to see validation details:

```python
import logging
logging.getLogger('unified.validation').setLevel(logging.DEBUG)

# Validation will now log detailed information
errors = schema.validate(data)
```

## Performance Considerations

1. **Cache Compiled Regex**: Compile patterns once and reuse.
2. **Batch Validations**: Validate multiple fields together when possible.
3. **Async Validators**: Use async validators for I/O operations.
4. **Early Exit**: Return on first error if appropriate.

```python
# Efficient validation with early exit
def validate_all_fields(data):
    for field, value in data.items():
        errors = validate_field(field, value)
        if errors:
            return errors  # Exit on first error
    return []
```