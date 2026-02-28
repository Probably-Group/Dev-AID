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
        assert any("security" in kw or "vulnerability" in kw for kw in keywords)

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

    def test_classify_documentation(self, classifier):
        task_type, keywords, conf = classifier.classify("write documentation for the API")
        assert task_type == TaskType.DOCUMENTATION

    def test_classify_debugging(self, classifier):
        task_type, keywords, conf = classifier.classify("debug this error, find the bug")
        assert task_type == TaskType.DEBUGGING

    def test_classify_complex_reasoning(self, classifier):
        task_type, keywords, conf = classifier.classify(
            "design the architecture and evaluate trade-offs"
        )
        assert task_type == TaskType.COMPLEX_REASONING

    def test_confidence_cap(self, classifier):
        # Input with many matching keywords — confidence should never exceed 1.0
        task_type, keywords, conf = classifier.classify(
            "fix the bug error problem broken failing crash exception"
        )
        assert conf <= 1.0

    def test_get_model_for_task_defaults(self, classifier):
        empty_config: dict = {}
        assert (
            classifier.get_model_for_task(TaskType.MASSIVE_CONTEXT, empty_config) == "gemini-flash"
        )
        assert classifier.get_model_for_task(TaskType.DOCUMENTATION, empty_config) == "gpt-4o"
        assert classifier.get_model_for_task(TaskType.DEBUGGING, empty_config) == "claude-sonnet"

    def test_explain_all_types(self, classifier):
        for task_type in TaskType:
            explanation = classifier.explain_classification(task_type, ["test"], 0.5)
            assert "50%" in explanation

    def test_classify_competing_patterns(self, classifier):
        # Security keywords dominate: "vulnerability" + "security" + "sql injection"
        task_type, keywords, conf = classifier.classify(
            "check for sql injection vulnerability in the security module"
        )
        assert task_type == TaskType.SECURITY_AUDIT
