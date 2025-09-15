# Contributing to Coffee Business AI Chatbot

Thank you for your interest in contributing to the Coffee Business AI Chatbot! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues

1. **Search existing issues** first to avoid duplicates
2. **Use the issue template** when creating new issues
3. **Provide detailed information** including:
   - Steps to reproduce the issue
   - Expected vs actual behavior
   - Environment details (Python version, OS, etc.)
   - Error messages or logs

### Submitting Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Follow the development setup** instructions in README.md
3. **Make your changes** following our coding standards
4. **Add tests** for new functionality
5. **Update documentation** if needed
6. **Test your changes** thoroughly
7. **Submit a pull request** with a clear description

## 🛠️ Development Setup

### Prerequisites
- Python 3.8+
- Git
- OpenAI API key (for testing)

### Local Development
```bash
# Clone your fork
git clone https://github.com/yourusername/coffee-business-chatbot.git
cd coffee-business-chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run tests
python -m pytest tests/

# Start development server
python web_knowledge_chatbot.py
```

## 📝 Coding Standards

### Python Style Guide
- Follow **PEP 8** style guidelines
- Use **type hints** where appropriate
- Write **docstrings** for all functions and classes
- Keep functions **small and focused**
- Use **meaningful variable names**

### Code Formatting
```bash
# Install formatting tools
pip install black isort flake8

# Format code
black .
isort .

# Check style
flake8 .
```

### Example Code Style
```python
from typing import Dict, List, Optional

def process_customer_data(
    customer_info: Dict[str, str], 
    validation_rules: Optional[List[str]] = None
) -> Dict[str, any]:
    """
    Process and validate customer information.
    
    Args:
        customer_info: Dictionary containing customer details
        validation_rules: Optional list of validation rules to apply
        
    Returns:
        Dictionary with processed customer data and validation status
        
    Raises:
        ValueError: If required customer information is missing
    """
    if not customer_info.get('email'):
        raise ValueError("Customer email is required")
    
    # Process the data...
    return processed_data
```

## 🧪 Testing Guidelines

### Test Structure
```
tests/
├── unit/
│   ├── test_knowledge_base.py
│   ├── test_sales_qualification.py
│   └── test_customer_management.py
├── integration/
│   ├── test_api_endpoints.py
│   └── test_websocket_communication.py
└── fixtures/
    ├── sample_customers.json
    └── mock_responses.py
```

### Writing Tests
- Write **unit tests** for individual functions
- Create **integration tests** for API endpoints
- Use **meaningful test names** that describe the scenario
- Include **both positive and negative test cases**
- Mock external API calls (OpenAI, Google APIs)

### Test Example
```python
import pytest
from unittest.mock import Mock, patch

def test_extract_qualification_data_valid_input():
    """Test qualification data extraction with valid customer input."""
    # Arrange
    customer_input = "I'm planning to open a café next month"
    expected_data = {"timeline": "next month", "business_type": "new_cafe"}
    
    # Act
    result = extract_qualification_data(customer_input)
    
    # Assert
    assert result["timeline"] == expected_data["timeline"]
    assert result["business_type"] == expected_data["business_type"]

@patch('openai.ChatCompletion.create')
def test_chatbot_response_with_api_error(mock_openai):
    """Test chatbot handles OpenAI API errors gracefully."""
    # Arrange
    mock_openai.side_effect = Exception("API Error")
    
    # Act & Assert
    with pytest.raises(Exception):
        generate_chatbot_response("Hello")
```

## 📚 Documentation

### Code Documentation
- Write **clear docstrings** for all public functions
- Include **parameter descriptions** and **return values**
- Document **exceptions** that may be raised
- Add **usage examples** for complex functions

### Knowledge Base Updates
- Follow **MDX format** for knowledge base files
- Include **metadata** at the top of each file
- Use **consistent headings** and structure
- Validate **content accuracy** with coffee industry experts

### API Documentation
- Document **all endpoints** with examples
- Include **request/response schemas**
- Provide **error code explanations**
- Add **authentication requirements**

## 🔧 Feature Development

### Adding New Features

1. **Create an issue** describing the feature
2. **Design the feature** with community input
3. **Break down** into smaller tasks
4. **Implement incrementally** with tests
5. **Update documentation**
6. **Get code review** before merging

### Feature Categories

#### Knowledge Base Features
- New coffee business topics
- Enhanced search capabilities
- Content management tools

#### Sales Features
- Lead qualification improvements
- CRM integrations
- Analytics and reporting

#### Technical Features
- Performance optimizations
- New AI capabilities
- Integration improvements

## 🐛 Bug Fixes

### Bug Fix Process
1. **Reproduce the bug** locally
2. **Write a failing test** that demonstrates the issue
3. **Fix the bug** with minimal changes
4. **Ensure the test passes**
5. **Check for regressions**
6. **Update documentation** if needed

### Priority Levels
- **Critical**: Security issues, data loss, system crashes
- **High**: Major functionality broken, significant user impact
- **Medium**: Minor functionality issues, workarounds available
- **Low**: Cosmetic issues, nice-to-have improvements

## 🔍 Code Review Guidelines

### For Authors
- **Keep PRs small** and focused
- **Write clear commit messages**
- **Test thoroughly** before submitting
- **Respond promptly** to review feedback
- **Update based on feedback**

### For Reviewers
- **Be constructive** and helpful
- **Focus on code quality** and maintainability
- **Check for security issues**
- **Verify tests are adequate**
- **Approve when ready**

### Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance impact considered
- [ ] Backward compatibility maintained

## 🚀 Release Process

### Version Numbering
We follow **Semantic Versioning** (SemVer):
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Release Steps
1. **Update version** in relevant files
2. **Update CHANGELOG.md**
3. **Create release branch**
4. **Run full test suite**
5. **Create GitHub release**
6. **Deploy to production**

## 📞 Getting Help

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Email**: [email] for security issues

### Response Times
- **Critical issues**: Within 24 hours
- **Bug reports**: Within 3-5 days
- **Feature requests**: Within 1 week
- **General questions**: Within 1 week

## 🏆 Recognition

Contributors will be recognized in:
- **README.md** contributors section
- **Release notes** for significant contributions
- **GitHub contributors** page

Thank you for contributing to the Coffee Business AI Chatbot! 🙏

---

*This project is maintained by the community and welcomes contributions from developers of all skill levels.*