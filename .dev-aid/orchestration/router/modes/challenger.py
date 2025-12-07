"""
Challenger Mode - Primary generates, challenger reviews
"""

from typing import Any, Dict

from ..api_clients import Message, create_client
from ..context_builder import ContextBuilder, build_system_prompt


class ChallengerMode:
    """Challenger mode: Two-model review workflow"""

    def __init__(self, config_loader, context_builder: ContextBuilder):
        """
        Initialize challenger mode

        Args:
            config_loader: ConfigLoader instance
            context_builder: ContextBuilder instance
        """
        self.config = config_loader
        self.context_builder = context_builder

    def execute(self, request: str, force_challenge: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Execute request in challenger mode

        Args:
            request: User request
            force_challenge: Force challenger review even if not security-sensitive
            **kwargs: Additional parameters

        Returns:
            Result dictionary
        """
        # Get challenger configuration
        routing_config = self.config.get_routing_config()
        challenger_config = routing_config.get("modes", {}).get("challenger", {})

        primary_model_name = challenger_config.get("primary_model", "claude-sonnet")
        challenger_model_name = challenger_config.get("challenger_model", "gemini-flash")

        # Check if challenge is needed
        should_challenge = force_challenge or self._should_challenge(request, challenger_config)

        if not should_challenge:
            # Just use primary model (like solo mode)
            return self._execute_primary_only(request, primary_model_name, **kwargs)

        # Execute full challenger workflow
        return self._execute_with_challenge(
            request, primary_model_name, challenger_model_name, challenger_config, **kwargs
        )

    def _should_challenge(self, request: str, challenger_config: Dict[str, Any]) -> bool:
        """Check if request should trigger challenger review"""
        review_triggers = challenger_config.get("review_triggers", [])

        request_lower = request.lower()

        for trigger in review_triggers:
            if trigger.lower() in request_lower:
                return True

        return False

    def _execute_primary_only(
        self, request: str, primary_model_name: str, **kwargs
    ) -> Dict[str, Any]:
        """Execute with primary model only (no challenge)"""

        # Get model config
        model_config = self.config.get_model_config(primary_model_name)
        if not model_config:
            model_config = self.config.get_model_config(self.config.get_default_model())
            primary_model_name = self.config.get_default_model()

        provider = model_config["provider"]

        # Validate
        is_valid, error = self.config.validate_provider(provider)
        if not is_valid:
            raise RuntimeError(error)

        # Get API key and create client
        api_key = self.config.get_api_key(provider)
        client = create_client(provider, api_key, model_config)

        # Build context
        context = self.context_builder.build_context()

        # Add MCP context if provided
        if "mcp_context" in kwargs and kwargs["mcp_context"]:
            context.mcp_context = kwargs["mcp_context"]

        system_prompt = build_system_prompt(context, self.context_builder)

        # Prepare messages
        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=request),
        ]

        # Execute
        model_id = model_config.get("id", primary_model_name)

        try:
            response = client.send_request(messages=messages, model=model_id, **kwargs)

            return {
                "success": True,
                "mode": "challenger",
                "challenged": False,
                "reason": "No challenge triggers found",
                "primary_model": primary_model_name,
                "response": response.content,
                "tokens_used": response.tokens_used,
                "cost": response.cost,
                "latency_ms": response.latency_ms,
            }

        except Exception as e:
            return {"success": False, "mode": "challenger", "challenged": False, "error": str(e)}

    def _execute_with_challenge(
        self,
        request: str,
        primary_model_name: str,
        challenger_model_name: str,
        challenger_config: Dict[str, Any],
        **kwargs,
    ) -> Dict[str, Any]:
        """Execute full two-model challenger workflow"""

        # Step 1: Primary generates solution
        primary_result = self._execute_with_model(
            request, primary_model_name, role="primary", **kwargs
        )

        if not primary_result["success"]:
            return primary_result

        primary_response = primary_result["response"]

        # Step 2: Challenger reviews
        review_prompt = self._build_review_prompt(request, primary_response)

        challenger_result = self._execute_with_model(
            review_prompt, challenger_model_name, role="challenger", **kwargs
        )

        if not challenger_result["success"]:
            # Return primary response even if challenger fails
            return {
                **primary_result,
                "challenged": True,
                "challenger_failed": True,
                "challenger_error": challenger_result.get("error"),
            }

        challenger_review = challenger_result["response"]

        # Step 3: Check if issues found (simple heuristic)
        has_issues = self._parse_review_for_issues(challenger_review)

        # Step 4: Refine if needed (optional - check config)
        auto_refine_on = challenger_config.get("auto_refine_on", ["HIGH", "CRITICAL"])
        should_refine = has_issues and any(
            severity in challenger_review.upper() for severity in auto_refine_on
        )

        refined_response = None
        refinement_result = None

        if should_refine:
            refinement_result = self._execute_refinement(
                request, primary_response, challenger_review, primary_model_name, **kwargs
            )

            if refinement_result["success"]:
                refined_response = refinement_result["response"]

        # Calculate total cost and tokens
        total_cost = primary_result["cost"] + challenger_result["cost"]
        total_tokens = {
            "input": primary_result["tokens_used"]["input"]
            + challenger_result["tokens_used"]["input"],
            "output": primary_result["tokens_used"]["output"]
            + challenger_result["tokens_used"]["output"],
        }

        if refinement_result:
            total_cost += refinement_result["cost"]
            total_tokens["input"] += refinement_result["tokens_used"]["input"]
            total_tokens["output"] += refinement_result["tokens_used"]["output"]

        # Build result
        return {
            "success": True,
            "mode": "challenger",
            "challenged": True,
            "primary_model": primary_model_name,
            "challenger_model": challenger_model_name,
            "primary_response": primary_response,
            "challenger_review": challenger_review,
            "issues_found": has_issues,
            "refined": refined_response is not None,
            "refined_response": refined_response,
            "final_response": refined_response if refined_response else primary_response,
            "tokens_used": total_tokens,
            "cost": total_cost,
            "latency_ms": (
                primary_result["latency_ms"]
                + challenger_result["latency_ms"]
                + (refinement_result["latency_ms"] if refinement_result else 0)
            ),
        }

    def _execute_with_model(
        self, request: str, model_name: str, role: str = "primary", **kwargs
    ) -> Dict[str, Any]:
        """Execute request with a specific model"""

        # Get model config
        model_config = self.config.get_model_config(model_name)

        if not model_config:
            return {"success": False, "error": f"Model configuration not found: {model_name}"}

        provider = model_config["provider"]

        # Validate provider
        is_valid, error = self.config.validate_provider(provider)
        if not is_valid:
            return {"success": False, "error": error}

        # Get API key and create client
        api_key = self.config.get_api_key(provider)
        client = create_client(provider, api_key, model_config)

        # Build context
        context = self.context_builder.build_context()

        # Add MCP context if provided
        if "mcp_context" in kwargs and kwargs["mcp_context"]:
            context.mcp_context = kwargs["mcp_context"]

        system_prompt = build_system_prompt(context, self.context_builder)

        # Prepare messages
        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=request),
        ]

        # Execute
        model_id = model_config.get("id", model_name)

        try:
            response = client.send_request(messages=messages, model=model_id, **kwargs)

            return {
                "success": True,
                "role": role,
                "model": model_name,
                "provider": provider,
                "response": response.content,
                "tokens_used": response.tokens_used,
                "cost": response.cost,
                "latency_ms": response.latency_ms,
            }

        except Exception as e:
            return {"success": False, "role": role, "model": model_name, "error": str(e)}

    def _build_review_prompt(self, original_request: str, primary_response: str) -> str:
        """Build prompt for challenger to review primary's response"""

        return f"""You are an expert code reviewer. Review the following solution for:

1. **Security Issues** (OWASP Top 10, injection vulnerabilities, authentication/authorization flaws)
2. **Logic Errors** (edge cases, error handling, data validation)
3. **Performance Issues** (inefficient algorithms, resource leaks, scalability)
4. **Code Quality** (maintainability, readability, best practices)

Original Request:
{original_request}

Proposed Solution:
{primary_response}

Provide your review in this format:

**SEVERITY**: [LOW/MEDIUM/HIGH/CRITICAL]

**Issues Found:**
1. [Issue description]
   - Impact: [What could go wrong]
   - Recommendation: [How to fix]

2. [Next issue...]

If no issues found, respond with:
**SEVERITY**: NONE
**Issues Found:** None - implementation looks good!
"""

    def _parse_review_for_issues(self, review: str) -> bool:
        """Check if challenger found any issues"""
        review_upper = review.upper()

        # Check for "no issues" indicators
        no_issues_indicators = [
            "SEVERITY: NONE",
            "SEVERITY**: NONE",
            "NO ISSUES",
            "LOOKS GOOD",
            "IMPLEMENTATION LOOKS GOOD",
        ]

        for indicator in no_issues_indicators:
            if indicator in review_upper:
                return False

        # Check for severity levels (indicates issues)
        if any(
            severity in review_upper
            for severity in [
                "SEVERITY: LOW",
                "SEVERITY: MEDIUM",
                "SEVERITY: HIGH",
                "SEVERITY: CRITICAL",
            ]
        ):
            return True

        # Default: assume issues if review is substantial
        return len(review) > 100

    def _execute_refinement(
        self,
        original_request: str,
        primary_response: str,
        challenger_review: str,
        primary_model_name: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """Execute refinement step based on challenger feedback"""

        refinement_prompt = f"""Based on the following code review feedback, please refine the solution:

Original Request:
{original_request}

Your Previous Solution:
{primary_response}

Code Review Feedback:
{challenger_review}

Please provide an improved solution that addresses the identified issues.
"""

        return self._execute_with_model(
            refinement_prompt, primary_model_name, role="refinement", **kwargs
        )

    def get_info(self) -> Dict[str, Any]:
        """Get information about challenger mode configuration"""
        routing_config = self.config.get_routing_config()
        challenger_config = routing_config.get("modes", {}).get("challenger", {})

        return {
            "mode": "challenger",
            "description": "Primary generates, challenger reviews",
            "enabled": challenger_config.get("enabled", True),
            "primary_model": challenger_config.get("primary_model", "claude-sonnet"),
            "challenger_model": challenger_config.get("challenger_model", "gemini-flash"),
            "auto_refine_on": challenger_config.get("auto_refine_on", ["HIGH", "CRITICAL"]),
            "review_triggers": challenger_config.get("review_triggers", []),
        }
