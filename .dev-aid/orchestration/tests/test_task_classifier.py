import pytest

from router.task_classifier import TaskClassifier, TaskType


class TestTaskClassifier:
    @pytest.fixture
    def classifier(self):
        return TaskClassifier()

    def test_classify_massive_context(self, classifier):
        # Priority by token count
        task_type, keywords, conf = classifier.classify("simple request", context_size=100001)
        assert task_type == TaskType.MASSIVE_CONTEXT
        assert conf == 1.0

        # Priority by keyword
        task_type, keywords, conf = classifier.classify("Analyze the entire repository")
        assert task_type == TaskType.MASSIVE_CONTEXT

    def test_classify_security(self, classifier):
        task_type, keywords, conf = classifier.classify("Check for SQL injection vulnerabilities")
        assert task_type == TaskType.SECURITY_AUDIT
        assert "sql injection" in keywords[0]

    def test_classify_code_gen(self, classifier):
        task_type, keywords, conf = classifier.classify("Write a python function to sort list")
        assert task_type == TaskType.CODE_GENERATION

    def test_classify_fallback(self, classifier):
        task_type, keywords, conf = classifier.classify("Hello world")
        assert task_type == TaskType.CODE_GENERATION  # Defaults to code gen if no match
        assert conf == 0.5

    def test_get_model_for_task(self, classifier):
        config = {
            "modes": {"ensemble": {"task_routes": {"security_audit": "custom-security-model"}}}
        }

        # Custom mapping
        model = classifier.get_model_for_task(TaskType.SECURITY_AUDIT, config)
        assert model == "custom-security-model"

        # Default mapping
        model = classifier.get_model_for_task(TaskType.CODE_GENERATION, config)
        assert model == "claude-sonnet"

    def test_explain_classification(self, classifier):
        explanation = classifier.explain_classification(TaskType.DEBUGGING, ["bug"], 0.8)
        assert "Bug investigation" in explanation
        assert "80%" in explanation
