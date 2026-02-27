# Reference implementation — extracted from senior-architect/SKILL.md for context reduction
#
# APIConsistencyChecker: Validates API design consistency across endpoints.
# Checks naming conventions (lowercase, plural nouns), response envelope
# uniformity, HTTP status code consistency, and CRUD completeness per resource.

from dataclasses import dataclass
from enum import Enum
import re


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


@dataclass
class EndpointDefinition:
    method: HTTPMethod
    path: str
    request_schema: dict | None
    response_schema: dict
    status_codes: list[int]


@dataclass
class APIConsistencyViolation:
    endpoint: str
    violation_type: str
    description: str
    recommendation: str


class APIConsistencyChecker:
    def __init__(self):
        self.endpoints: list[EndpointDefinition] = []
        self.violations: list[APIConsistencyViolation] = []

    def add_endpoint(self, endpoint: EndpointDefinition):
        self.endpoints.append(endpoint)

    def check_consistency(self) -> list[APIConsistencyViolation]:
        self.violations = []

        self._check_naming_conventions()
        self._check_response_structure()
        self._check_status_code_usage()
        self._check_crud_completeness()

        return self.violations

    def _check_naming_conventions(self):
        """Check URL path naming consistency."""
        for ep in self.endpoints:
            # Should use kebab-case or snake_case consistently
            if re.search(r"[A-Z]", ep.path):
                self.violations.append(
                    APIConsistencyViolation(
                        endpoint=f"{ep.method.value} {ep.path}",
                        violation_type="naming",
                        description="Path contains uppercase letters",
                        recommendation="Use lowercase with hyphens: /user-profiles instead of /userProfiles",
                    )
                )

            # Should use plural nouns for collections
            parts = ep.path.strip("/").split("/")
            if parts and not parts[0].endswith("s") and "{" not in parts[0]:
                self.violations.append(
                    APIConsistencyViolation(
                        endpoint=f"{ep.method.value} {ep.path}",
                        violation_type="naming",
                        description="Resource name should be plural",
                        recommendation=f"Use /{parts[0]}s instead of /{parts[0]}",
                    )
                )

    def _check_response_structure(self):
        """Check response envelope consistency."""
        envelope_patterns = set()

        for ep in self.endpoints:
            if ep.method == HTTPMethod.GET:
                keys = set(ep.response_schema.keys())
                # Track which wrapper pattern is used
                if "data" in keys:
                    envelope_patterns.add("data_wrapper")
                elif len(keys) == 1:
                    envelope_patterns.add(f"single_key:{list(keys)[0]}")
                else:
                    envelope_patterns.add("direct")

        if len(envelope_patterns) > 1:
            self.violations.append(
                APIConsistencyViolation(
                    endpoint="ALL GET endpoints",
                    violation_type="response_structure",
                    description=f"Inconsistent response envelopes: {envelope_patterns}",
                    recommendation="Use consistent envelope: { data: {...}, meta: {...} }",
                )
            )

    def _check_status_code_usage(self):
        """Check HTTP status code consistency."""
        post_codes = set()
        for ep in self.endpoints:
            if ep.method == HTTPMethod.POST:
                post_codes.update(ep.status_codes)

        if 200 in post_codes and 201 in post_codes:
            self.violations.append(
                APIConsistencyViolation(
                    endpoint="POST endpoints",
                    violation_type="status_codes",
                    description="Inconsistent success codes for POST (200 and 201 both used)",
                    recommendation="Use 201 Created for resource creation, 200 for actions",
                )
            )

    def _check_crud_completeness(self):
        """Check if CRUD operations are complete for resources."""
        resources: dict[str, set[HTTPMethod]] = {}

        for ep in self.endpoints:
            # Extract resource name from path
            parts = ep.path.strip("/").split("/")
            if parts:
                resource = parts[0]
                if resource not in resources:
                    resources[resource] = set()
                resources[resource].add(ep.method)

        for resource, methods in resources.items():
            if HTTPMethod.GET in methods and HTTPMethod.POST in methods:
                # If create and read exist, update and delete should too
                if HTTPMethod.PUT not in methods and HTTPMethod.PATCH not in methods:
                    self.violations.append(
                        APIConsistencyViolation(
                            endpoint=f"/{resource}",
                            violation_type="crud_completeness",
                            description="Missing update operation (PUT or PATCH)",
                            recommendation=f"Add PUT or PATCH /{resource}/{{id}} endpoint",
                        )
                    )
