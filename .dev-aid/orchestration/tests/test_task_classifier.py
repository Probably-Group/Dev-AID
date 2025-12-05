"""
Unit tests for task_classifier.py
"""

import pytest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from router.task_classifier import TaskClassifier, TaskType


class TestTaskClassifier:
    """Test suite for TaskClassifier"""

    @pytest.fixture
    def classifier(self):
        """Create TaskClassifier instance"""
        return TaskClassifier()

    def test_classify_massive_context_keywords(self, classifier):
        """Test classification of massive context tasks by keywords"""
        test_cases = [
            "Analyze the entire codebase for performance issues",
            "Search through all files to find API endpoints",
            "Review the whole repository structure",
            "Scan every file for security vulnerabilities"
        ]

        for prompt in test_cases:
            task_type, confidence = classifier.classify(prompt)
            assert task_type == TaskType.MASSIVE_CONTEXT
            assert confidence > 0.7

    def test_classify_code_generation_keywords(self, classifier):
        """Test classification of code generation tasks"""
        test_cases = [
            "Implement user authentication",
            "Write a function to validate emails",
            "Create a new API endpoint for user registration",
            "Refactor the database query logic"
        ]

        for prompt in test_cases:
            task_type, confidence = classifier.classify(prompt)
            assert task_type == TaskType.CODE_GENERATION
            assert confidence > 0.6

    def test_classify_security_audit_keywords(self, classifier):
        """Test classification of security tasks"""
        test_cases = [
            "Review this authentication code for security issues",
            "Check for SQL injection vulnerabilities",
            "Audit the password hashing implementation",
            "Validate OAuth2 security implementation"
        ]

        for prompt in test_cases:
            task_type, confidence = classifier.classify(prompt)
            assert task_type == TaskType.SECURITY_AUDIT
            assert confidence > 0.7

    def test_classify_documentation_keywords(self, classifier):
        """Test classification of documentation tasks"""
        test_cases = [
            "Write documentation for this API",
            "Generate a README for this project",
            "Document the authentication flow",
            "Create API reference docs"
        ]

        for prompt in test_cases:
            task_type, confidence = classifier.classify(prompt)
            assert task_type == TaskType.DOCUMENTATION
            assert confidence > 0.6

    def test_classify_debugging_keywords(self, classifier):
        """Test classification of debugging tasks"""
        test_cases = [
            "Fix the bug in user login",
            "Debug this error message",
            "Troubleshoot the database connection issue",
            "Find out why the API is returning 500 errors"
        ]

        for prompt in test_cases:
            task_type, confidence = classifier.classify(prompt)
            assert task_type == TaskType.DEBUGGING
            assert confidence > 0.6

    def test_classify_complex_reasoning_keywords(self, classifier):
        """Test classification of complex reasoning tasks"""
        test_cases = [
            "Design the system architecture for our microservices",
            "Evaluate different database options for our use case",
            "Plan the migration from monolith to microservices",
            "Analyze trade-offs between REST and GraphQL"
        ]

        for prompt in test_cases:
            task_type, confidence = classifier.classify(prompt)
            assert task_type == TaskType.COMPLEX_REASONING
            assert confidence > 0.6

    def test_classify_general_fallback(self, classifier):
        """Test fallback to GENERAL for unclear prompts"""
        test_cases = [
            "Hello",
            "What is Python?",
            "Tell me about React",
            "How does HTTP work?"
        ]

        for prompt in test_cases:
            task_type, confidence = classifier.classify(prompt)
            assert task_type == TaskType.GENERAL
            assert confidence <= 0.5

    def test_classify_empty_prompt(self, classifier):
        """Test classification of empty prompt"""
        task_type, confidence = classifier.classify("")

        assert task_type == TaskType.GENERAL
        assert confidence == 0.0

    def test_classify_case_insensitive(self, classifier):
        """Test that classification is case-insensitive"""
        prompts = [
            "IMPLEMENT authentication",
            "Implement AUTHENTICATION",
            "implement authentication"
        ]

        results = [classifier.classify(p) for p in prompts]

        # All should classify the same
        assert len(set(r[0] for r in results)) == 1
        assert all(r[0] == TaskType.CODE_GENERATION for r in results)

    def test_classify_multiple_keywords(self, classifier):
        """Test prompts with multiple keywords from different categories"""
        # Should prioritize higher-confidence category
        prompt = "Implement secure authentication and write documentation"

        task_type, confidence = classifier.classify(prompt)

        # Should detect code_generation (implement) or security (secure)
        assert task_type in [TaskType.CODE_GENERATION, TaskType.SECURITY_AUDIT]
        assert confidence > 0.6

    def test_get_task_description(self, classifier):
        """Test getting task type descriptions"""
        descriptions = {
            TaskType.MASSIVE_CONTEXT: classifier.get_task_description(TaskType.MASSIVE_CONTEXT),
            TaskType.CODE_GENERATION: classifier.get_task_description(TaskType.CODE_GENERATION),
            TaskType.SECURITY_AUDIT: classifier.get_task_description(TaskType.SECURITY_AUDIT),
            TaskType.DOCUMENTATION: classifier.get_task_description(TaskType.DOCUMENTATION),
            TaskType.DEBUGGING: classifier.get_task_description(TaskType.DEBUGGING),
            TaskType.COMPLEX_REASONING: classifier.get_task_description(TaskType.COMPLEX_REASONING),
            TaskType.GENERAL: classifier.get_task_description(TaskType.GENERAL)
        }

        # All should have non-empty descriptions
        assert all(desc for desc in descriptions.values())

        # Descriptions should be unique
        assert len(set(descriptions.values())) == len(descriptions)


class TestTaskType:
    """Test TaskType enum"""

    def test_task_type_values(self):
        """Test TaskType enum values"""
        expected_types = [
            "massive_context",
            "code_generation",
            "security_audit",
            "documentation",
            "debugging",
            "complex_reasoning",
            "general"
        ]

        actual_types = [t.value for t in TaskType]

        assert set(actual_types) == set(expected_types)

    def test_task_type_from_string(self):
        """Test creating TaskType from string"""
        assert TaskType("code_generation") == TaskType.CODE_GENERATION
        assert TaskType("massive_context") == TaskType.MASSIVE_CONTEXT

    def test_task_type_comparison(self):
        """Test TaskType equality"""
        assert TaskType.CODE_GENERATION == TaskType.CODE_GENERATION
        assert TaskType.CODE_GENERATION != TaskType.SECURITY_AUDIT


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
