#!/usr/bin/env python3
"""
Test Data Factory - Mock Data Generator

Generates realistic mock data from schema definitions for testing.
Supports Pydantic models, TypeScript interfaces, JSON Schema, and SQL schemas.
"""

import csv
import json
import random
import re
import string
import sys
from datetime import datetime, timedelta
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional


class DataFactory:
    """Generates realistic test data from schemas"""

    def __init__(self, seed: Optional[int] = None):
        if seed:
            random.seed(seed)

        # Sample data pools for realistic generation
        self.first_names = [
            "Alice",
            "Bob",
            "Charlie",
            "Diana",
            "Eve",
            "Frank",
            "Grace",
            "Henry",
            "Ivy",
            "Jack",
        ]
        self.last_names = [
            "Smith",
            "Johnson",
            "Williams",
            "Brown",
            "Jones",
            "Garcia",
            "Miller",
            "Davis",
            "Rodriguez",
            "Martinez",
        ]
        self.domains = ["example.com", "test.com", "demo.org", "sample.net"]
        self.cities = [
            "New York",
            "Los Angeles",
            "Chicago",
            "Houston",
            "Phoenix",
            "Philadelphia",
            "San Antonio",
            "San Diego",
        ]
        self.states = ["CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI"]

    def generate_string(self, constraints: Optional[Dict[Any, Any]] = None) -> str:
        """Generate random string with constraints"""
        constraints = constraints or {}
        min_length = constraints.get("minLength", 1)
        max_length = constraints.get("maxLength", 50)
        pattern = constraints.get("pattern")

        if pattern:
            # Simple pattern matching for common cases
            if pattern == "email":
                first = random.choice(self.first_names).lower()
                last = random.choice(self.last_names).lower()
                domain = random.choice(self.domains)
                return f"{first}.{last}@{domain}"
            elif pattern == "url":
                return f"https://www.{random.choice(self.domains)}/path"
            elif pattern == "uuid":
                import uuid

                return str(uuid.uuid4())

        length = random.randint(min_length, max_length)
        return "".join(random.choices(string.ascii_letters, k=length))

    def generate_int(self, constraints: Optional[Dict[Any, Any]] = None) -> int:
        """Generate random integer with constraints"""
        constraints = constraints or {}
        minimum = constraints.get("minimum", 0)
        maximum = constraints.get("maximum", 1000)
        return random.randint(minimum, maximum)

    def generate_float(self, constraints: Optional[Dict[Any, Any]] = None) -> float:
        """Generate random float with constraints"""
        constraints = constraints or {}
        minimum = constraints.get("minimum", 0.0)
        maximum = constraints.get("maximum", 1000.0)
        return round(random.uniform(minimum, maximum), 2)

    def generate_bool(self) -> bool:
        """Generate random boolean"""
        return random.choice([True, False])

    def generate_datetime(self, constraints: Optional[Dict[Any, Any]] = None) -> str:
        """Generate random datetime"""
        constraints = constraints or {}
        days_ago = random.randint(0, 365)
        dt = datetime.now() - timedelta(days=days_ago)
        return dt.isoformat()

    def generate_email(self) -> str:
        """Generate realistic email"""
        first = random.choice(self.first_names).lower()
        last = random.choice(self.last_names).lower()
        domain = random.choice(self.domains)
        return f"{first}.{last}@{domain}"

    def generate_phone(self) -> str:
        """Generate realistic phone number"""
        area = random.randint(200, 999)
        prefix = random.randint(200, 999)
        line = random.randint(1000, 9999)
        return f"({area}) {prefix}-{line}"

    def generate_address(self) -> Dict:
        """Generate realistic address"""
        return {
            "street": f"{random.randint(1, 9999)} {random.choice(self.last_names)} St",
            "city": random.choice(self.cities),
            "state": random.choice(self.states),
            "zipCode": f"{random.randint(10000, 99999)}",
        }

    def parse_json_schema(self, schema: Dict) -> List[Dict]:
        """Parse JSON Schema and generate data"""
        schema.get("type")
        properties = schema.get("properties", {})
        required = schema.get("required", [])

        generated = []

        # Generate field value based on type
        for field_name, field_schema in properties.items():
            field_type = field_schema.get("type")
            field_value: Any = None

            if field_type == "string":
                if field_schema.get("format") == "email":
                    field_value = self.generate_email()
                elif field_schema.get("format") == "date-time":
                    field_value = self.generate_datetime()
                else:
                    field_value = self.generate_string(field_schema)

            elif field_type == "integer":
                field_value = self.generate_int(field_schema)

            elif field_type == "number":
                field_value = self.generate_float(field_schema)

            elif field_type == "boolean":
                field_value = self.generate_bool()

            elif field_type == "array":
                items = field_schema.get("items", {})
                count = random.randint(1, 5)
                field_value = [self.generate_from_type(items.get("type")) for _ in range(count)]

            generated.append(
                {"field": field_name, "value": field_value, "required": field_name in required}
            )

        return generated

    def generate_from_type(self, type_name: str) -> Any:
        """Generate value based on type name"""
        type_map = {
            "string": self.generate_string(),
            "str": self.generate_string(),
            "integer": self.generate_int(),
            "int": self.generate_int(),
            "number": self.generate_float(),
            "float": self.generate_float(),
            "boolean": self.generate_bool(),
            "bool": self.generate_bool(),
            "datetime": self.generate_datetime(),
            "email": self.generate_email(),
            "phone": self.generate_phone(),
        }
        return type_map.get(type_name, self.generate_string())

    def parse_pydantic_model(self, model_code: str) -> Dict:
        """Parse Pydantic model definition"""
        # Simple regex-based parsing
        fields = {}
        for line in model_code.split("\n"):
            # Match: field_name: Type = Field(...)
            match = re.match(r"\s+(\w+):\s*(\w+)(?:\[.*?\])?\s*=?\s*.*", line)
            if match:
                field_name, field_type = match.groups()
                fields[field_name] = field_type.lower()

        return fields

    def parse_typescript_interface(self, interface_code: str) -> Dict:
        """Parse TypeScript interface"""
        fields = {}
        for line in interface_code.split("\n"):
            # Match: fieldName: type;
            match = re.match(r"\s+(\w+)\??\s*:\s*(\w+)", line)
            if match:
                field_name, field_type = match.groups()
                fields[field_name] = field_type.lower()

        return fields

    def generate_from_schema(self, schema: Dict, count: int = 1) -> List[Dict]:
        """Generate multiple records from schema"""
        records = []

        # Detect schema type
        if "properties" in schema:  # JSON Schema
            for _ in range(count):
                record = {}
                for field_data in self.parse_json_schema(schema):
                    record[field_data["field"]] = field_data["value"]
                records.append(record)
        else:
            # Simple field map
            for _ in range(count):
                record = {}
                for field_name, field_type in schema.items():
                    record[field_name] = self.generate_from_type(field_type)
                records.append(record)

        return records

    def generate_from_file(self, file_path: Path, count: int = 10) -> List[Dict]:
        """Generate data from schema file"""
        content = file_path.read_text()

        # Detect file type
        if file_path.suffix == ".json":
            schema = json.loads(content)
            return self.generate_from_schema(schema, count)

        elif file_path.suffix == ".py":
            # Parse Pydantic model
            fields = self.parse_pydantic_model(content)
            return self.generate_from_schema(fields, count)

        elif file_path.suffix in [".ts", ".tsx"]:
            # Parse TypeScript interface
            fields = self.parse_typescript_interface(content)
            return self.generate_from_schema(fields, count)

        raise ValueError(f"Unsupported file type: {file_path.suffix}")

    def output_json(self, records: List[Dict]) -> str:
        """Output as JSON"""
        return json.dumps(records, indent=2)

    def output_csv(self, records: List[Dict]) -> str:
        """Output as CSV"""
        if not records:
            return ""

        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)
        return output.getvalue()

    @staticmethod
    def _sql_escape(value: str) -> str:
        """Escape a string value for SQL by doubling single quotes."""
        return value.replace("'", "''")

    @staticmethod
    def _sql_identifier(name: str) -> str:
        """Quote a SQL identifier and reject dangerous characters."""
        if not name.isidentifier() and not all(c.isalnum() or c == "_" for c in name):
            raise ValueError(f"Invalid SQL identifier: {name}")
        return f'"{name}"'

    def output_sql(self, records: List[Dict], table_name: str = "test_table") -> str:
        """Output as SQL INSERT statements (with proper escaping)"""
        if not records:
            return ""

        safe_table = self._sql_identifier(table_name)

        sql_statements = []
        for record in records:
            columns = ", ".join(self._sql_identifier(k) for k in record.keys())
            escaped_values = []
            for v in record.values():
                if v is None:
                    escaped_values.append("NULL")
                elif isinstance(v, str):
                    escaped_values.append(f"'{self._sql_escape(v)}'")
                elif isinstance(v, bool):
                    escaped_values.append("TRUE" if v else "FALSE")
                else:
                    escaped_values.append(str(v))
            values = ", ".join(escaped_values)
            sql_statements.append(f"INSERT INTO {safe_table} ({columns}) VALUES ({values});")

        return "\n".join(sql_statements)

    def run(
        self,
        schema_file: Path,
        count: int = 10,
        format: str = "json",
        output_file: Optional[Path] = None,
    ):
        """Main execution"""
        print(f"🔍 Reading schema from: {schema_file}")

        # Generate data
        records = self.generate_from_file(schema_file, count)

        print(f"✅ Generated {len(records)} records")

        # Format output
        if format == "json":
            output = self.output_json(records)
        elif format == "csv":
            output = self.output_csv(records)
        elif format == "sql":
            output = self.output_sql(records)
        else:
            raise ValueError(f"Unsupported format: {format}")

        # Write or print
        if output_file:
            output_file.write_text(output)
            print(f"✅ Saved to: {output_file}")
        else:
            print("\n" + output)

        return 0


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate realistic test data from schemas")
    parser.add_argument(
        "schema", type=Path, help="Schema file (JSON Schema, Pydantic model, TypeScript interface)"
    )
    parser.add_argument(
        "-c", "--count", type=int, default=10, help="Number of records to generate (default: 10)"
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["json", "csv", "sql"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument("-o", "--output", type=Path, help="Output file (default: stdout)")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")

    args = parser.parse_args()

    factory = DataFactory(seed=args.seed)
    return factory.run(args.schema, args.count, args.format, args.output)


if __name__ == "__main__":
    sys.exit(main())
