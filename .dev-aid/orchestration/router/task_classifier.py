"""
Task Classifier for Ensemble Mode

Classifies user requests into task types to route to appropriate model:
- massive_context: Large codebase analysis
- code_generation: Writing/refactoring code
- security_audit: Security review
- documentation: Writing docs
- debugging: Finding/fixing bugs
- complex_reasoning: Architecture decisions
"""

from typing import Tuple, List
import re


class TaskClassifier:
    """Classifies tasks based on keywords and patterns"""

    # Task type definitions with keywords
    TASK_PATTERNS = {
        "massive_context": [
            # Phrases indicating large scope
            r"\b(entire|whole|all|every)\s+(codebase|repository|project|files?)\b",
            r"\banalyze\s+everything\b",
            r"\bread\s+all\b",
            r"\brevie w\s+entire\b",
            r"\b(100|200|many)\s+files\b",
            r"\brepository[- ]wide\b",
            # File count indicators
            r"\b(scan|search|find|analyze)\s+(all|every)\b",
        ],

        "security_audit": [
            # Security keywords
            r"\b(security|vulnerability|vulnerabilities|exploit|owasp)\b",
            r"\bsecure\s+(code|audit|review)\b",
            r"\b(penetration|pen)[-\s]test\b",
            r"\b(auth|authentication|authorization)\s+(bug|issue|vulnerability)\b",
            r"\b(sql\s+injection|xss|csrf|rce)\b",
            r"\b(credential|password|token|secret)\s+(leak|exposure)\b",
            r"\bsecurity\s+scan\b",
        ],

        "code_generation": [
            # Code writing keywords
            r"\b(implement|create|write|build|develop|code)\b",
            r"\b(function|class|method|component|module)\b",
            r"\b(feature|functionality)\b",
            r"\b(add|new)\s+\w+\s+(function|class|endpoint)\b",
            r"\brefactor(ing)?\b",
            r"\brewrite\b",
        ],

        "documentation": [
            # Documentation keywords
            r"\b(document|documentation|readme|docs)\b",
            r"\b(write|create|generate)\s+(docs|documentation|readme|guide)\b",
            r"\b(explain|describe|document)\s+how\b",
            r"\b(api|function|class)\s+documentation\b",
            r"\bcode\s+comments\b",
            r"\btutorial\b",
            r"\buser\s+guide\b",
        ],

        "debugging": [
            # Bug/error keywords
            r"\b(bug|error|issue|problem|broken|failing|failed)\b",
            r"\b(fix|debug|troubleshoot|investigate)\b",
            r"\b(not\s+working|doesn't\s+work|isn't\s+working)\b",
            r"\b(exception|crash|failure)\b",
            r"\bwhy\s+(is|does)\b",
            r"\bstack\s+trace\b",
        ],

        "complex_reasoning": [
            # Architecture/design keywords
            r"\b(architecture|design|structure)\b",
            r"\b(trade[-\s]?off|tradeoff)s?\b",
            r"\b(evaluate|compare|recommend|suggest)\b",
            r"\b(should\s+i|which\s+(approach|method|pattern))\b",
            r"\b(best\s+practice|optimal|strategy)\b",
            r"\b(pros\s+and\s+cons|advantages|disadvantages)\b",
            r"\bdesign\s+pattern\b",
        ]
    }

    def classify(self, request: str, context_size: int = 0) -> Tuple[str, List[str], float]:
        """
        Classify a user request into task type

        Args:
            request: User request string
            context_size: Estimated context size in tokens

        Returns:
            Tuple of (task_type, matched_keywords, confidence)
        """
        request_lower = request.lower()

        # Check for massive context first (high priority)
        if context_size > 100_000:
            return "massive_context", ["large_context"], 1.0

        # Score each task type
        scores = {}
        matched_keywords = {}

        for task_type, patterns in self.TASK_PATTERNS.items():
            score = 0
            matches = []

            for pattern in patterns:
                if re.search(pattern, request_lower):
                    score += 1
                    matches.append(pattern)

            if score > 0:
                scores[task_type] = score
                matched_keywords[task_type] = matches

        # If no matches, default to code_generation
        if not scores:
            return "code_generation", ["default"], 0.5

        # Get task type with highest score
        best_task = max(scores, key=scores.get)
        confidence = min(scores[best_task] / 3.0, 1.0)  # Normalize to 0-1

        return best_task, matched_keywords[best_task], confidence

    def get_model_for_task(self, task_type: str, routing_config: dict) -> str:
        """
        Get recommended model for task type

        Args:
            task_type: Task type from classify()
            routing_config: Routing configuration

        Returns:
            Model name
        """
        task_routes = routing_config.get("modes", {}).get("ensemble", {}).get("task_routes", {})

        # Default mappings if not in config
        default_routes = {
            "massive_context": "gemini-flash",
            "code_generation": "claude-sonnet",
            "security_audit": "claude-sonnet",
            "documentation": "gpt-4o",
            "debugging": "claude-sonnet",
            "complex_reasoning": "claude-opus"
        }

        return task_routes.get(task_type, default_routes.get(task_type, "claude-sonnet"))

    def explain_classification(self, task_type: str, matched_keywords: List[str], confidence: float) -> str:
        """
        Generate human-readable explanation of classification

        Args:
            task_type: Classified task type
            matched_keywords: Keywords that matched
            confidence: Confidence score (0-1)

        Returns:
            Explanation string
        """
        explanations = {
            "massive_context": "Large-scale codebase analysis requiring extensive context",
            "code_generation": "Code writing, implementation, or refactoring task",
            "security_audit": "Security review or vulnerability assessment",
            "documentation": "Documentation writing or explanation task",
            "debugging": "Bug investigation and fixing",
            "complex_reasoning": "Architectural design or strategic decision"
        }

        explanation = explanations.get(task_type, "General development task")
        confidence_str = f"{confidence * 100:.0f}%"

        return f"{explanation} (confidence: {confidence_str})"


# Example usage
if __name__ == "__main__":
    classifier = TaskClassifier()

    test_requests = [
        "Analyze the entire codebase and find all API endpoints",
        "Implement user authentication with OAuth2",
        "Check for SQL injection vulnerabilities",
        "Write API documentation for the auth module",
        "Fix the bug in login.ts - user can't sign in",
        "Should we use microservices or monolithic architecture?",
    ]

    print("🎯 Task Classification Examples\n")
    print("=" * 70)

    for request in test_requests:
        task_type, keywords, confidence = classifier.classify(request)
        explanation = classifier.explain_classification(task_type, keywords, confidence)

        print(f"\nRequest: \"{request}\"")
        print(f"  → Task Type: {task_type}")
        print(f"  → Explanation: {explanation}")
        print(f"  → Matched Patterns: {len(keywords)}")
