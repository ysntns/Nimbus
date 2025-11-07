# Contributing to Nimbus

First off, thank you for considering contributing to Nimbus! It's people like you that make Nimbus such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by respect, professionalism, and collaboration. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps to reproduce the problem**
* **Provide specific examples**
* **Describe the behavior you observed and what you expected**
* **Include screenshots if possible**
* **Include your environment details** (OS, Python version, Nimbus version)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a detailed description of the suggested enhancement**
* **Explain why this enhancement would be useful**
* **List any alternative solutions you've considered**

### Pull Requests

* Fill in the required template
* Follow the Python style guide (PEP 8)
* Include appropriate test cases
* Update documentation as needed
* End all files with a newline

## Development Setup

1. Fork and clone the repository
```bash
git clone https://github.com/ysntns/nimbus.git
cd nimbus
```

2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies
```bash
pip install -r requirements.txt
pip install -e ".[dev]"
```

4. Create a branch
```bash
git checkout -b feature/your-feature-name
```

## Style Guidelines

### Python Style Guide

* Follow PEP 8
* Use meaningful variable and function names
* Add docstrings to all functions, classes, and modules
* Keep functions focused and concise
* Use type hints where appropriate

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests after the first line

Example:
```
Add incremental backup feature

- Implement manifest tracking
- Add file change detection
- Update tests

Closes #123
```

### Testing

* Write unit tests for new features
* Ensure all tests pass before submitting PR
* Aim for high code coverage

Run tests:
```bash
pytest tests/
pytest --cov=app tests/
```

### Code Review Process

1. The maintainer will review your PR
2. Changes may be requested
3. Once approved, your PR will be merged

## Project Structure

```
nimbus/
├── app/
│   ├── core/       # Core functionality
│   ├── gui/        # GUI application
│   ├── cli/        # CLI interface
│   ├── cloud/      # Cloud integrations
│   └── utils/      # Utilities
├── tests/          # Test files
├── docs/           # Documentation
└── config/         # Configuration files
```

## Additional Notes

### Issue and Pull Request Labels

* `bug` - Something isn't working
* `enhancement` - New feature or request
* `documentation` - Documentation improvements
* `good first issue` - Good for newcomers
* `help wanted` - Extra attention needed

## Questions?

Feel free to contact the maintainer:
* Email: ysn.tnss@gmail.com
* GitHub: @ysntns

## Recognition

Contributors will be recognized in the project README and release notes.

Thank you for your contributions! 🙏
