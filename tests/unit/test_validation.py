"""
Unit tests for validation framework
"""
import pytest
from pathlib import Path
from unified.validation import (
    ValidationRule, ValidationSchema, ValidationType,
    InputValidator, CommandValidator,
    get_input_validator, get_command_validator
)


class TestValidationRule:
    """Test ValidationRule functionality"""
    
    def test_required_rule(self):
        """Test required validation rule"""
        rule = ValidationRule(ValidationType.REQUIRED)
        
        # Should fail for None
        assert rule.get_error_message("field", None) == "field is required"
        
        # Should fail for empty string
        assert rule.get_error_message("field", "") == "field is required"
    
    def test_type_rule(self):
        """Test type validation rule"""
        rule = ValidationRule(ValidationType.TYPE, {'type': str})
        
        error = rule.get_error_message("field", 123)
        assert "must be of type str" in error
        assert "got int" in error
    
    def test_range_rule(self):
        """Test range validation rule"""
        rule = ValidationRule(ValidationType.RANGE, {'min': 1, 'max': 10})
        
        error = rule.get_error_message("field", 15)
        assert "must be between 1 and 10" in error
        assert "got 15" in error
    
    def test_pattern_rule(self):
        """Test pattern validation rule"""
        rule = ValidationRule(ValidationType.PATTERN, {'pattern': r'^[a-z]+$'})
        
        error = rule.get_error_message("field", "ABC123")
        assert "does not match required pattern" in error
    
    def test_enum_rule(self):
        """Test enum validation rule"""
        rule = ValidationRule(ValidationType.ENUM, {'values': ['a', 'b', 'c']})
        
        error = rule.get_error_message("field", "d")
        assert "must be one of ['a', 'b', 'c']" in error
        assert "got d" in error
    
    def test_custom_error_message(self):
        """Test custom error messages"""
        rule = ValidationRule(
            ValidationType.REQUIRED,
            error_message="Please provide {field}"
        )
        
        error = rule.get_error_message("username", None)
        assert error == "Please provide username"


class TestValidationSchema:
    """Test ValidationSchema functionality"""
    
    def test_schema_validation(self):
        """Test complete schema validation"""
        schema = ValidationSchema()
        
        # Add field rules
        schema.add_field('name', [
            ValidationRule(ValidationType.REQUIRED),
            ValidationRule(ValidationType.TYPE, {'type': str}),
            ValidationRule(ValidationType.LENGTH, {'min': 3, 'max': 20})
        ])
        
        schema.add_field('age', [
            ValidationRule(ValidationType.TYPE, {'type': int}),
            ValidationRule(ValidationType.RANGE, {'min': 0, 'max': 120})
        ])
        
        # Valid data
        errors = schema.validate({'name': 'John', 'age': 25})
        assert errors == []
        
        # Missing required field
        errors = schema.validate({'age': 25})
        assert len(errors) == 1
        assert "name is required" in errors[0]
        
        # Invalid type
        errors = schema.validate({'name': 123, 'age': 25})
        assert len(errors) == 1
        assert "must be of type str" in errors[0]
        
        # Out of range
        errors = schema.validate({'name': 'John', 'age': 150})
        assert len(errors) == 1
        assert "must be between 0 and 120" in errors[0]
    
    def test_custom_validator(self):
        """Test custom validation function"""
        def validate_even(value, data):
            return value % 2 == 0
        
        schema = ValidationSchema()
        schema.add_field('number', [
            ValidationRule(ValidationType.TYPE, {'type': int}),
            ValidationRule(
                ValidationType.CUSTOM,
                {'validator': validate_even},
                "Number must be even"
            )
        ])
        
        # Valid even number
        errors = schema.validate({'number': 4})
        assert errors == []
        
        # Invalid odd number
        errors = schema.validate({'number': 5})
        assert len(errors) == 1
        assert "Number must be even" in errors[0]


class TestInputValidator:
    """Test InputValidator functionality"""
    
    @pytest.fixture
    def validator(self):
        return InputValidator()
    
    def test_builtin_file_schema(self, validator):
        """Test built-in file path validation"""
        # Valid file path
        errors = validator.validate('file_path', {'path': '/home/user/file.txt'})
        assert errors == []
        
        # System directory
        errors = validator.validate('file_path', {'path': '/etc/passwd'})
        assert len(errors) == 1
        assert "cannot access system directories" in errors[0]
        
        # Missing path
        errors = validator.validate('file_path', {'path': None})
        assert len(errors) == 1
        assert "required" in errors[0]
    
    def test_builtin_command_schema(self, validator):
        """Test built-in command validation"""
        # Valid command
        errors = validator.validate('command', {'command': 'ls -la /home'})
        assert errors == []
        
        # Invalid characters
        errors = validator.validate('command', {'command': 'rm -rf / && echo pwned'})
        assert len(errors) == 1
        assert "invalid characters" in errors[0]
    
    def test_builtin_network_schema(self, validator):
        """Test built-in network validation"""
        # Valid URL
        errors = validator.validate('network', {
            'url': 'https://example.com',
            'port': 443
        })
        assert errors == []
        
        # Invalid URL
        errors = validator.validate('network', {
            'url': 'not-a-url',
            'port': 443
        })
        assert len(errors) == 1
        assert "Invalid URL" in errors[0]
        
        # Invalid port
        errors = validator.validate('network', {
            'url': 'https://example.com',
            'port': 70000
        })
        assert len(errors) == 1
        assert "must be between 1 and 65535" in errors[0]
    
    def test_email_validation(self, validator):
        """Test email validation"""
        assert validator.validate_email("user@example.com") is True
        assert validator.validate_email("user+tag@sub.example.com") is True
        assert validator.validate_email("invalid.email") is False
        assert validator.validate_email("@example.com") is False
        assert validator.validate_email("user@") is False
    
    def test_ip_validation(self, validator):
        """Test IP address validation"""
        # Valid IPv4
        assert validator.validate_ip_address("192.168.1.1") is True
        assert validator.validate_ip_address("192.168.1.1", version=4) is True
        
        # Valid IPv6
        assert validator.validate_ip_address("2001:db8::1") is True
        assert validator.validate_ip_address("2001:db8::1", version=6) is True
        
        # Invalid
        assert validator.validate_ip_address("999.999.999.999") is False
        assert validator.validate_ip_address("not-an-ip") is False
        
        # Wrong version
        assert validator.validate_ip_address("192.168.1.1", version=6) is False
    
    def test_path_sanitization(self, validator):
        """Test path sanitization"""
        # Normal path
        sanitized = validator.sanitize_path("file.txt")
        assert sanitized.name == "file.txt"
        
        # Path traversal attempt
        sanitized = validator.sanitize_path("../../etc/passwd")
        assert "etc" not in str(sanitized)
        assert "passwd" in str(sanitized)
    
    def test_command_sanitization(self, validator):
        """Test command sanitization"""
        # Remove dangerous characters
        sanitized = validator.sanitize_command("echo hello && rm -rf /")
        assert "&" not in sanitized
        assert "echo hello rm -rf /" in sanitized
        
        # Remove command substitution
        sanitized = validator.sanitize_command("echo $(whoami)")
        assert "$(" not in sanitized
        assert ")" not in sanitized
        
        # Remove backticks
        sanitized = validator.sanitize_command("echo `date`")
        assert "`" not in sanitized


class TestCommandValidator:
    """Test CommandValidator functionality"""
    
    @pytest.fixture
    def validator(self):
        return CommandValidator()
    
    def test_allowed_commands(self, validator):
        """Test allowed command validation"""
        # Allowed commands
        errors = validator.validate_command("ls -la")
        assert errors == []
        
        errors = validator.validate_command("git status")
        assert errors == []
        
        # Disallowed command
        errors = validator.validate_command("nc -l 1234")
        assert len(errors) > 0
        assert any("not allowed" in e for e in errors)
    
    def test_forbidden_patterns(self, validator):
        """Test forbidden pattern detection"""
        # Dangerous rm
        errors = validator.validate_command("rm -rf /")
        assert len(errors) > 0
        assert any("Forbidden pattern" in e for e in errors)
        
        # Fork bomb
        errors = validator.validate_command(":(){ :|:& };:")
        assert len(errors) > 0
        
        # Sudo
        errors = validator.validate_command("sudo apt-get update")
        assert len(errors) > 0
    
    def test_shell_metacharacters(self, validator):
        """Test shell metacharacter detection"""
        # Pipe
        errors = validator.validate_command("ls | grep test")
        assert len(errors) > 0
        assert any("Shell metacharacter '|'" in e for e in errors)
        
        # Background
        errors = validator.validate_command("sleep 10 &")
        assert len(errors) > 0
        assert any("Shell metacharacter '&'" in e for e in errors)
        
        # Command substitution
        errors = validator.validate_command("echo $(date)")
        assert len(errors) > 0
    
    def test_command_sanitization(self, validator):
        """Test command sanitization for execution"""
        # Remove metacharacters
        sanitized = validator.sanitize_for_execution("ls | grep test")
        assert sanitized == "ls grep test"
        
        # Remove multiple spaces
        sanitized = validator.sanitize_for_execution("ls    -la")
        assert sanitized == "ls -la"
        
        # Remove all dangerous characters
        sanitized = validator.sanitize_for_execution("rm -rf / && echo done; exit")
        assert sanitized == "rm -rf / echo done exit"


def test_global_validators():
    """Test global validator instances"""
    input_validator = get_input_validator()
    assert isinstance(input_validator, InputValidator)
    
    command_validator = get_command_validator()
    assert isinstance(command_validator, CommandValidator)
    
    # Should return same instances
    assert input_validator is get_input_validator()
    assert command_validator is get_command_validator()