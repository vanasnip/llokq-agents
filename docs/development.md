# Development Guide

## Local Development Setup

This project uses pre-commit hooks for code quality checks instead of CI/CD on GitHub.

### Installing Pre-commit

```bash
# Install pre-commit (if not already installed)
pip install pre-commit

# Install the git hook scripts
pre-commit install

# (Optional) Run against all files
pre-commit run --all-files
```

### Pre-commit Checks

The following checks run automatically before each commit:

1. **Code Quality**
   - Black (code formatting)
   - Ruff (linting)
   - Trailing whitespace removal
   - End of file fixing

2. **File Validation**
   - YAML syntax check
   - JSON syntax check
   - Large file prevention (>1MB)
   - Merge conflict detection

3. **Python Specific**
   - Debug statement detection
   - Mixed line ending fixes
   - Setup.py validation

### Running Checks Manually

```bash
# Run all checks
pre-commit run --all-files

# Run specific check
pre-commit run black --all-files
pre-commit run ruff --all-files

# Update pre-commit hooks
pre-commit autoupdate
```

### Skipping Checks (Emergency Only)

```bash
# Skip pre-commit for emergency fixes
git commit --no-verify -m "Emergency fix"

# Or
SKIP=black,ruff git commit -m "Skip specific checks"
```

### Setting Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .[dev]

# Install pre-commit
pre-commit install
```

### Why No GitHub CI?

We've disabled GitHub Actions CI to:
- Reduce external dependencies
- Speed up development workflow
- Keep all checks local
- Avoid CI configuration complexity

All quality checks run locally via pre-commit hooks, ensuring code quality before it reaches the repository.

### Troubleshooting

#### Pre-commit Installation Issues

```bash
# Clear pre-commit cache
pre-commit clean

# Reinstall hooks
pre-commit uninstall
pre-commit install
```

#### Python Version Issues

```bash
# Ensure Python 3.8+ is installed
python --version

# Use specific Python version
PYTHON_PATH=/usr/bin/python3.11 pre-commit install
```

#### Hook Failures

If a hook fails:
1. Read the error message carefully
2. Fix the issue
3. Stage the fixes: `git add .`
4. Commit again

### Development Workflow

1. Make changes to code
2. Stage changes: `git add .`
3. Commit: `git commit -m "Your message"`
4. Pre-commit runs automatically
5. If checks fail, fix issues and retry
6. Push to remote: `git push`

### Code Style Guide

- **Line Length**: 100 characters (enforced by Black)
- **Import Order**: Standard library, third-party, local (enforced by Ruff)
- **Type Hints**: Encouraged but not required
- **Docstrings**: Google style preferred

### Testing

While not enforced by pre-commit, please run tests before pushing:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=unified

# Run specific test
pytest tests/unit/test_tools.py
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Install pre-commit hooks
4. Make your changes
5. Ensure all checks pass
6. Submit a pull request

Remember: Quality checks happen locally, not in CI!