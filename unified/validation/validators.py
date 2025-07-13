"""
Input validation framework for commands and parameters
"""
from typing import Any, Dict, List, Optional, Union, Type, Callable
from dataclasses import dataclass, field
from enum import Enum
import re
from pathlib import Path
import ipaddress
from urllib.parse import urlparse


class ValidationType(Enum):
    """Types of validation"""
    REQUIRED = "required"
    TYPE = "type"
    RANGE = "range"
    PATTERN = "pattern"
    LENGTH = "length"
    ENUM = "enum"
    CUSTOM = "custom"


@dataclass
class ValidationRule:
    """A single validation rule"""
    validation_type: ValidationType
    params: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    
    def get_error_message(self, field_name: str, value: Any) -> str:
        """Get error message for validation failure"""
        if self.error_message:
            return self.error_message.format(field=field_name, value=value)
        
        # Default messages
        if self.validation_type == ValidationType.REQUIRED:
            return f"{field_name} is required"
        elif self.validation_type == ValidationType.TYPE:
            expected = self.params.get('type', 'unknown').__name__
            return f"{field_name} must be of type {expected}, got {type(value).__name__}"
        elif self.validation_type == ValidationType.RANGE:
            min_val = self.params.get('min', float('-inf'))
            max_val = self.params.get('max', float('inf'))
            return f"{field_name} must be between {min_val} and {max_val}, got {value}"
        elif self.validation_type == ValidationType.PATTERN:
            return f"{field_name} does not match required pattern"
        elif self.validation_type == ValidationType.LENGTH:
            min_len = self.params.get('min', 0)
            max_len = self.params.get('max', float('inf'))
            return f"{field_name} length must be between {min_len} and {max_len}"
        elif self.validation_type == ValidationType.ENUM:
            allowed = self.params.get('values', [])
            return f"{field_name} must be one of {allowed}, got {value}"
        else:
            return f"{field_name} validation failed"


@dataclass
class ValidationSchema:
    """Schema for validating a set of fields"""
    fields: Dict[str, List[ValidationRule]] = field(default_factory=dict)
    
    def add_field(self, field_name: str, rules: List[ValidationRule]) -> None:
        """Add validation rules for a field"""
        self.fields[field_name] = rules
    
    def validate(self, data: Dict[str, Any]) -> List[str]:
        """Validate data against schema, return list of errors"""
        errors = []
        
        for field_name, rules in self.fields.items():
            value = data.get(field_name)
            
            for rule in rules:
                error = self._validate_rule(field_name, value, rule, data)
                if error:
                    errors.append(error)
                    break  # Stop on first error for this field
        
        return errors
    
    def _validate_rule(self, field_name: str, value: Any, rule: ValidationRule, data: Dict[str, Any]) -> Optional[str]:
        """Validate a single rule"""
        if rule.validation_type == ValidationType.REQUIRED:
            if value is None or (isinstance(value, str) and not value.strip()):
                return rule.get_error_message(field_name, value)
        
        elif rule.validation_type == ValidationType.TYPE:
            if value is not None:
                expected_type = rule.params.get('type')
                if not isinstance(value, expected_type):
                    return rule.get_error_message(field_name, value)
        
        elif rule.validation_type == ValidationType.RANGE:
            if value is not None:
                min_val = rule.params.get('min', float('-inf'))
                max_val = rule.params.get('max', float('inf'))
                if not (min_val <= value <= max_val):
                    return rule.get_error_message(field_name, value)
        
        elif rule.validation_type == ValidationType.PATTERN:
            if value is not None:
                pattern = rule.params.get('pattern')
                if not re.match(pattern, str(value)):
                    return rule.get_error_message(field_name, value)
        
        elif rule.validation_type == ValidationType.LENGTH:
            if value is not None:
                length = len(value) if hasattr(value, '__len__') else 0
                min_len = rule.params.get('min', 0)
                max_len = rule.params.get('max', float('inf'))
                if not (min_len <= length <= max_len):
                    return rule.get_error_message(field_name, value)
        
        elif rule.validation_type == ValidationType.ENUM:
            if value is not None:
                allowed_values = rule.params.get('values', [])
                if value not in allowed_values:
                    return rule.get_error_message(field_name, value)
        
        elif rule.validation_type == ValidationType.CUSTOM:
            if value is not None:
                validator_func = rule.params.get('validator')
                if validator_func and not validator_func(value, data):
                    return rule.get_error_message(field_name, value)
        
        return None


class InputValidator:
    """Main input validation class"""
    
    def __init__(self):
        self.schemas: Dict[str, ValidationSchema] = {}
        self._setup_builtin_schemas()
    
    def _setup_builtin_schemas(self) -> None:
        """Set up built-in validation schemas"""
        # File path schema
        file_schema = ValidationSchema()
        file_schema.add_field('path', [
            ValidationRule(ValidationType.REQUIRED),
            ValidationRule(ValidationType.TYPE, {'type': (str, Path)}),
            ValidationRule(ValidationType.CUSTOM, {
                'validator': lambda v, d: not str(v).startswith('/etc/') and not str(v).startswith('/sys/')
            }, "Path cannot access system directories")
        ])
        self.schemas['file_path'] = file_schema
        
        # Command schema
        command_schema = ValidationSchema()
        command_schema.add_field('command', [
            ValidationRule(ValidationType.REQUIRED),
            ValidationRule(ValidationType.TYPE, {'type': str}),
            ValidationRule(ValidationType.LENGTH, {'min': 1, 'max': 1000}),
            ValidationRule(ValidationType.PATTERN, {
                'pattern': r'^[a-zA-Z0-9\s\-\./_]+$'
            }, "Command contains invalid characters")
        ])
        self.schemas['command'] = command_schema
        
        # Network schema
        network_schema = ValidationSchema()
        network_schema.add_field('url', [
            ValidationRule(ValidationType.REQUIRED),
            ValidationRule(ValidationType.TYPE, {'type': str}),
            ValidationRule(ValidationType.CUSTOM, {
                'validator': self._validate_url
            }, "Invalid URL format")
        ])
        network_schema.add_field('port', [
            ValidationRule(ValidationType.TYPE, {'type': int}),
            ValidationRule(ValidationType.RANGE, {'min': 1, 'max': 65535})
        ])
        self.schemas['network'] = network_schema
    
    def register_schema(self, name: str, schema: ValidationSchema) -> None:
        """Register a custom validation schema"""
        self.schemas[name] = schema
    
    def validate(self, schema_name: str, data: Dict[str, Any]) -> List[str]:
        """Validate data using a named schema"""
        schema = self.schemas.get(schema_name)
        if not schema:
            return [f"Unknown validation schema: {schema_name}"]
        
        return schema.validate(data)
    
    @staticmethod
    def _validate_url(value: str, data: Dict[str, Any]) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(value)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_ip_address(ip: str, version: Optional[int] = None) -> bool:
        """Validate IP address"""
        try:
            addr = ipaddress.ip_address(ip)
            if version:
                return addr.version == version
            return True
        except ValueError:
            return False
    
    @staticmethod
    def sanitize_path(path: Union[str, Path]) -> Path:
        """Sanitize file path to prevent traversal"""
        path = Path(path)
        # Resolve to absolute path and check for traversal
        try:
            resolved = path.resolve()
            # Check if path tries to escape current directory
            cwd = Path.cwd()
            if not (resolved == cwd or resolved.is_relative_to(cwd)):
                # Path tries to escape, return safe version
                return cwd / path.name
            return resolved
        except:
            return Path.cwd() / "invalid_path"
    
    @staticmethod
    def sanitize_command(command: str) -> str:
        """Sanitize command string"""
        # Remove dangerous characters and patterns
        dangerous_patterns = [
            (r'[;&|]', ''),  # Command chaining
            (r'`.*`', ''),   # Command substitution
            (r'\$\(.*\)', ''),  # Command substitution
            (r'>', '_'),     # Redirection
            (r'<', '_'),     # Redirection
            (r'\.\/', ''),   # Current directory
            (r'\.\.', ''),   # Parent directory
        ]
        
        sanitized = command
        for pattern, replacement in dangerous_patterns:
            sanitized = re.sub(pattern, replacement, sanitized)
        
        return sanitized.strip()


class CommandValidator:
    """Validator specifically for command execution"""
    
    def __init__(self):
        self.validator = InputValidator()
        self.allowed_commands = set()
        self.forbidden_patterns = []
        self._setup_defaults()
    
    def _setup_defaults(self) -> None:
        """Set up default allowed commands and patterns"""
        # Safe commands
        self.allowed_commands.update([
            'ls', 'cat', 'echo', 'pwd', 'date', 'whoami',
            'git', 'npm', 'yarn', 'python', 'pip',
            'grep', 'find', 'wc', 'sort', 'uniq'
        ])
        
        # Dangerous patterns
        self.forbidden_patterns = [
            re.compile(r'rm\s+(-rf|-fr)'),
            re.compile(r':(){ :|:& };:'),  # Fork bomb
            re.compile(r'dd\s+if='),
            re.compile(r'mkfs'),
            re.compile(r'sudo'),
            re.compile(r'su\s+'),
            re.compile(r'chmod\s+777'),
            re.compile(r'nc\s+-l'),  # Netcat listener
        ]
    
    def validate_command(self, command: str, context: Optional[Dict[str, Any]] = None) -> List[str]:
        """Validate a command for execution"""
        errors = []
        
        if not command:
            errors.append("Command cannot be empty")
            return errors
        
        # Check command length
        if len(command) > 1000:
            errors.append("Command too long (max 1000 characters)")
        
        # Extract base command
        parts = command.split()
        if not parts:
            errors.append("Invalid command format")
            return errors
        
        base_cmd = parts[0]
        
        # Check if command is allowed
        if base_cmd not in self.allowed_commands:
            errors.append(f"Command '{base_cmd}' is not allowed")
        
        # Check for forbidden patterns
        for pattern in self.forbidden_patterns:
            if pattern.search(command):
                errors.append(f"Forbidden pattern detected in command")
                break
        
        # Check for shell metacharacters
        shell_chars = ['|', '&', ';', '$', '`', '(', ')', '{', '}', '[', ']', '<', '>', '\\']
        for char in shell_chars:
            if char in command:
                errors.append(f"Shell metacharacter '{char}' not allowed")
                break
        
        return errors
    
    def sanitize_for_execution(self, command: str) -> str:
        """Sanitize command for safe execution"""
        # Remove shell metacharacters
        sanitized = re.sub(r'[|&;$`(){}[\]<>\\]', '', command)
        
        # Remove multiple spaces
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        return sanitized.strip()


# Global validator instance
_input_validator = InputValidator()
_command_validator = CommandValidator()


def get_input_validator() -> InputValidator:
    """Get global input validator instance"""
    return _input_validator


def get_command_validator() -> CommandValidator:
    """Get global command validator instance"""
    return _command_validator