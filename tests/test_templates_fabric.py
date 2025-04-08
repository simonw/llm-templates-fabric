import pytest
from unittest.mock import patch, Mock


def test_fabric_template_loader_both_prompts():
    from llm_templates_fabric import fabric_template_loader

    with patch("httpx.get") as mock_get:
        # Mock successful responses for both system and user prompts
        mock_system_response = Mock()
        mock_system_response.status_code = 200
        mock_system_response.text = "This is the system prompt"

        mock_user_response = Mock()
        mock_user_response.status_code = 200
        mock_user_response.text = "This is the user prompt"

        # Configure the mock to return different responses for different URLs
        def get_side_effect(url):
            if "system.md" in url:
                return mock_system_response
            if "user.md" in url:
                return mock_user_response
            return Mock(status_code=404)

        mock_get.side_effect = get_side_effect

        # Test loading a template
        template = fabric_template_loader("test_template")

        # Verify the template has both prompts
        assert template.system == "This is the system prompt"
        assert template.prompt == "This is the user prompt"


def test_fabric_template_loader_system_only():
    from llm_templates_fabric import fabric_template_loader

    with patch("httpx.get") as mock_get:
        # Mock successful response for system prompt only
        mock_system_response = Mock()
        mock_system_response.status_code = 200
        mock_system_response.text = "This is the system prompt"

        mock_user_response = Mock()
        mock_user_response.status_code = 404

        # Configure the mock to return different responses for different URLs
        def get_side_effect(url):
            if "system.md" in url:
                return mock_system_response
            if "user.md" in url:
                return mock_user_response
            return Mock(status_code=404)

        mock_get.side_effect = get_side_effect

        # Test loading a template
        template = fabric_template_loader("test_template")

        # Verify the template has only system prompt
        assert template.system == "This is the system prompt"
        # The Template class always sets prompt attribute even if None
        assert template.prompt is None


def test_fabric_template_loader_user_only():
    from llm_templates_fabric import fabric_template_loader

    with patch("httpx.get") as mock_get:
        # Mock successful response for user prompt only
        mock_system_response = Mock()
        mock_system_response.status_code = 404

        mock_user_response = Mock()
        mock_user_response.status_code = 200
        mock_user_response.text = "This is the user prompt"

        # Configure the mock to return different responses for different URLs
        def get_side_effect(url):
            if "system.md" in url:
                return mock_system_response
            if "user.md" in url:
                return mock_user_response
            return Mock(status_code=404)

        mock_get.side_effect = get_side_effect

        # Test loading a template
        template = fabric_template_loader("test_template")

        # Verify the template has only user prompt
        # The Template class always sets system attribute even if None
        assert template.system is None
        assert template.prompt == "This is the user prompt"


def test_fabric_template_loader_not_found():
    from llm_templates_fabric import fabric_template_loader

    with patch("httpx.get") as mock_get:
        # Mock failed responses for both prompts
        mock_response = Mock()
        mock_response.status_code = 404

        mock_get.return_value = mock_response

        # Test loading a non-existent template
        with pytest.raises(ValueError, match="not found in Fabric repository"):
            fabric_template_loader("nonexistent_template")
