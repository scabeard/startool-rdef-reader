# Contributing to NASA RDEF Reader

Thank you for considering contributing to the NASA RDEF Reader project! This document provides guidelines to help you get started.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Guidelines](#coding-guidelines)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)

## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

## How to Contribute

We welcome contributions through:

- **Bug Reports**: Found a bug? Please [open an issue](https://github.com/your-username/nasa-rdef-reader/issues) with details.
- **Feature Requests**: Have an idea? [Submit a feature request](https://github.com/your-username/nasa-rdef-reader/issues).
- **Pull Requests**: Ready to contribute code? Great! See [Submitting Changes](#submitting-changes) below.

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/nasa-rdef-reader.git
   cd nasa-rdef-reader
   ```

2. **Set up your environment**
   ```bash
   # Create a virtual environment
   python -m venv venv
   
   # Activate it
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   
   # Install in development mode
   pip install -e .
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

### Coding Guidelines

- **Python Version**: Target Python 3.7+
- **Code Style**: Follow PEP 8 and use [Black](https://black.readthedocs.io/) for formatting
- **Type Hints**: Consider adding type hints for better code documentation
- **Imports**: Organize imports using [isort](https://pycqa.github.io/isort/)
- **Line Length**: Keep lines under 88 characters (Black default)

### Testing

- **No External Dependencies**: The core library should work without external packages
- **GUI Testing**: Test the GUI functionality manually
- **File Format Support**: Test with various RDEF file formats when possible

### Documentation

- **Docstrings**: Use clear, descriptive docstrings for all public functions and classes
- **README**: Keep the README updated with installation and usage instructions
- **Examples**: Add examples for new features in the `examples/` directory

### Submitting Changes

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clear, descriptive commit messages
   - Ensure your code follows the project's style guidelines

3. **Test your changes**
   - Verify the GUI works correctly
   - Test with sample RDEF files if available

4. **Commit and push**
   ```bash
   git add .
   git commit -m "Add descriptive commit message"
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request**
   - Provide a clear PR description
   - Reference any related issues
   - Describe the changes and their purpose

## Getting Help

- **Issues**: Check existing [issues](https://github.com/your-username/nasa-rdef-reader/issues) first
- **Discussions**: Use GitHub Discussions for questions and community help
- **Documentation**: Review the project documentation

## Additional Notes

- **NASA Files**: This tool is designed for legacy NASA telemetry files. Your contributions help preserve and analyze important space data.
- **Cross-Platform**: Ensure your changes work on Windows, macOS, and Linux
- **Performance**: Keep performance in mind when working with large telemetry files

## Questions?

If you have questions not covered here, please open an [issue](https://github.com/your-username/nasa-rdef-reader/issues) or start a [discussion](https://github.com/your-username/nasa-rdef-reader/discussions).

Thank you for contributing to NASA RDEF Reader! 🚀
