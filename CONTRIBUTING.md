# Contributing to Tracify

Thank you for your interest in contributing to Tracify! 🎨

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/opencv-sketch-effects.git`
3. Install dependencies: `uv sync --all-groups`
4. Install pre-commit hooks: `uv run pre-commit install`

## Development Workflow

### Making Changes

1. Create a new branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Run quality checks: `make ci` (or see commands below)
4. Commit your changes with clear messages
5. Push to your fork: `git push origin feature/your-feature-name`
6. Open a Pull Request

### Code Quality Standards

Before submitting a PR, ensure all checks pass:

```bash
# Run all checks at once
make ci

# Or run individually:
make lint          # Code linting
make format-check  # Code formatting check
make typecheck     # Type checking
make test          # Run tests with coverage
make security      # Security scanning
```

### Code Style

- **Formatting**: We use `ruff format` (follows Black style)
- **Line length**: 100 characters
- **Type hints**: Required for all functions
- **Docstrings**: Google style for all public functions

Example:

```python
def process_image(image: np.ndarray, effect: str) -> np.ndarray:
    """Apply effect to an image.

    Args:
        image: Input image in BGR format.
        effect: Name of the effect to apply.

    Returns:
        Processed image.

    Raises:
        ValueError: If effect is unknown.
    """
    # Implementation
```

### Testing

- Write tests for all new features
- Maintain or improve test coverage (current: >90%)
- Include both unit tests and integration tests
- Test edge cases (empty arrays, 1x1 images, large images, etc.)

Run tests:

```bash
make test         # With coverage
make test-fast    # Without coverage
```

### Commit Messages

We encourage (but don't require) conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `style:` Code style/formatting
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance tasks

Examples:
```
feat: add gaussian blur intensity slider
fix: handle corrupted image files gracefully
docs: update installation instructions
```

## Pull Request Guidelines

### Before Submitting

1. ✅ All tests pass: `make test`
2. ✅ Code is formatted: `make format`
3. ✅ No linting errors: `make lint`
4. ✅ Type checking passes: `make typecheck`
5. ✅ Security checks pass: `make security`
6. ✅ Update documentation if needed
7. ✅ Add tests for new features

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Added/updated tests
- [ ] All tests pass locally
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
```

## Questions?

- Open an issue for bugs or feature requests
- Join discussions in existing issues
- Check README.md for basic information

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for making Tracify better! 🙌
