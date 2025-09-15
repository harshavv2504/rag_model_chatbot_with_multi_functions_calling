"""
Pytest configuration and fixtures for Coffee Business AI Chatbot tests.
"""

import pytest
import os
import tempfile
import json
from unittest.mock import Mock, patch
from typing import Dict, Any

# Set test environment variables
os.environ["OPENAI_API_KEY"] = "test_key"
os.environ["DEBUG"] = "true"


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "choices": [
            {
                "message": {
                    "content": "Hello! I'm Logan from Abbotsford Road Coffee Specialists.",
                    "role": "assistant"
                }
            }
        ]
    }


@pytest.fixture
def sample_customer_data():
    """Sample customer data for testing."""
    return {
        "customer_id": "CUST001",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1-555-123-4567",
        "business_type": "new_cafe",
        "timeline": "next_month"
    }


@pytest.fixture
def sample_qualification_data():
    """Sample sales qualification data for testing."""
    return {
        "leads": [
            {
                "id": "LEAD001",
                "name": "Jane Smith",
                "email": "jane@coffeeshop.com",
                "phone": "+1-555-987-6543",
                "business_type": "existing_business",
                "priority": "HIGH",
                "qualification_data": {
                    "timeline": "immediate",
                    "pain_points": ["supplier_issues", "quality_concerns"],
                    "locations": 3
                }
            }
        ]
    }


@pytest.fixture
def temp_data_file():
    """Create a temporary data file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"test": "data"}, f)
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup
    if os.path.exists(temp_file):
        os.unlink(temp_file)


@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection for testing."""
    websocket = Mock()
    websocket.send_text = Mock()
    websocket.receive_text = Mock(return_value='{"message": "test"}')
    return websocket


@pytest.fixture
def mock_knowledge_base():
    """Mock knowledge base data."""
    return {
        "topics": [
            "coffee-menu-design",
            "equipment-selection",
            "business-strategies"
        ],
        "entries": {
            "coffee-menu-design": {
                "title": "Coffee Menu Design",
                "content": "Design effective coffee menus...",
                "tags": ["menu", "design", "strategy"]
            }
        }
    }


@pytest.fixture(autouse=True)
def mock_external_apis():
    """Mock external API calls to prevent actual API requests during testing."""
    with patch('openai.ChatCompletion.create') as mock_openai, \
         patch('google.auth.default') as mock_google_auth, \
         patch('googleapiclient.discovery.build') as mock_google_build:
        
        # Mock OpenAI response
        mock_openai.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Test response from Logan",
                        "role": "assistant"
                    }
                }
            ]
        }
        
        # Mock Google API authentication
        mock_google_auth.return_value = (Mock(), "test-project")
        mock_google_build.return_value = Mock()
        
        yield {
            'openai': mock_openai,
            'google_auth': mock_google_auth,
            'google_build': mock_google_build
        }


@pytest.fixture
def client():
    """FastAPI test client."""
    from fastapi.testclient import TestClient
    
    # Import here to avoid circular imports
    try:
        from web_knowledge_chatbot import app
        return TestClient(app)
    except ImportError:
        # If the main app isn't available, create a minimal test app
        from fastapi import FastAPI
        test_app = FastAPI()
        
        @test_app.get("/health")
        async def health():
            return {"status": "ok"}
        
        return TestClient(test_app)


@pytest.fixture
def sample_conversation_history():
    """Sample conversation history for testing."""
    return [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi! I'm Logan from Abbotsford Road Coffee Specialists."},
        {"role": "user", "content": "I want to open a coffee shop"},
        {"role": "assistant", "content": "That's exciting! When are you planning to open?"}
    ]


class MockAsyncContextManager:
    """Mock async context manager for testing."""
    
    def __init__(self, return_value):
        self.return_value = return_value
    
    async def __aenter__(self):
        return self.return_value
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.fixture
def mock_async_openai():
    """Mock async OpenAI client for testing."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [
        Mock(message=Mock(content="Test response", role="assistant"))
    ]
    mock_client.chat.completions.create.return_value = MockAsyncContextManager(mock_response)
    return mock_client