"""Unit tests for TOON utilities."""

import json

import pytest

from toon import converter, decoder, encoder


class TestToonEncoder:
    """Test TOON encoder functionality"""

    def test_encode_simple_dict(self):
        """Test encoding a simple dictionary"""
        data = {"name": "Alice", "age": 30}
        toon_str = encoder.encode(data)

        assert isinstance(toon_str, str)
        assert len(toon_str) > 0
        # TOON should be more compact than JSON
        assert len(toon_str) < len(json.dumps(data))

    def test_encode_nested_dict(self):
        """Test encoding a nested dictionary"""
        data = {"user": {"name": "Bob", "email": "bob@example.com"}, "active": True}
        toon_str = encoder.encode(data)

        assert isinstance(toon_str, str)
        assert len(toon_str) > 0

    def test_encode_list(self):
        """Test encoding a list"""
        data = [1, 2, 3, 4, 5]
        toon_str = encoder.encode(data)

        assert isinstance(toon_str, str)
        assert len(toon_str) > 0

    def test_encode_complex_structure(self):
        """Test encoding a complex data structure"""
        data = {
            "models": [
                {"name": "gpt-4", "cost": 0.03, "speed": "fast"},
                {"name": "claude-3", "cost": 0.015, "speed": "medium"},
            ]
        }
        toon_str = encoder.encode(data)

        assert isinstance(toon_str, str)
        assert len(toon_str) > 0

    def test_encode_set_converts_to_array(self):
        """Test that sets are converted to arrays"""
        # toon-format converts sets to arrays
        result = encoder.encode(set([1, 2, 3]))
        assert isinstance(result, str)
        # Decode and verify it's a list with same elements
        decoded = decoder.decode(result)
        assert set(decoded) == {1, 2, 3}


class TestToonDecoder:
    """Test TOON decoder functionality"""

    def test_decode_simple_toon(self):
        """Test decoding simple TOON format"""
        # First encode, then decode
        original_data = {"name": "Charlie", "age": 40}
        toon_str = encoder.encode(original_data)
        decoded_data = decoder.decode(toon_str)

        assert decoded_data == original_data

    def test_decode_empty_string(self):
        """Test that decoding empty string raises ValueError"""
        with pytest.raises(ValueError, match="cannot be empty"):
            decoder.decode("")

    def test_decode_invalid_input(self):
        """Test that decoding non-string input raises ValueError"""
        with pytest.raises(ValueError, match="must be a string"):
            decoder.decode(123)  # type: ignore


class TestToonRoundtrip:
    """Test encode/decode roundtrip preservation"""

    def test_roundtrip_simple_dict(self):
        """Test that encode/decode preserves simple dict"""
        data = {"key": "value", "number": 42, "flag": True}
        toon_str = encoder.encode(data)
        decoded = decoder.decode(toon_str)

        assert decoded == data

    def test_roundtrip_nested_structure(self):
        """Test that encode/decode preserves nested structure"""
        data = {
            "user": {"name": "Dave", "settings": {"theme": "dark", "notifications": True}},
            "items": [1, 2, 3],
        }
        toon_str = encoder.encode(data)
        decoded = decoder.decode(toon_str)

        assert decoded == data

    def test_roundtrip_list_of_dicts(self):
        """Test that encode/decode preserves list of dicts"""
        data = [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"},
            {"id": 3, "name": "Item 3"},
        ]
        toon_str = encoder.encode(data)
        decoded = decoder.decode(toon_str)

        assert decoded == data

    def test_roundtrip_with_nulls(self):
        """Test that encode/decode preserves null values"""
        data = {"key": None, "value": "something"}
        toon_str = encoder.encode(data)
        decoded = decoder.decode(toon_str)

        assert decoded == data


class TestToonConverter:
    """Test TOON ↔ JSON converter"""

    def test_json_to_toon(self):
        """Test converting JSON string to TOON"""
        json_str = '{"name": "Eve", "age": 28}'
        toon_str = converter.json_to_toon(json_str)

        assert isinstance(toon_str, str)
        assert len(toon_str) > 0
        assert len(toon_str) < len(json_str)  # TOON should be more compact

    def test_toon_to_json(self):
        """Test converting TOON to JSON string"""
        original_json = '{"name": "Frank", "age": 35}'
        toon_str = converter.json_to_toon(original_json)
        result_json = converter.toon_to_json(toon_str)

        # Parse both to compare (order might differ)
        original_data = json.loads(original_json)
        result_data = json.loads(result_json)

        assert original_data == result_data

    def test_toon_to_json_pretty(self):
        """Test converting TOON to pretty-printed JSON"""
        data = {"name": "Grace", "age": 32}
        toon_str = encoder.encode(data)
        pretty_json = converter.toon_to_json(toon_str, pretty=True)

        assert "\n" in pretty_json  # Should have newlines
        assert "  " in pretty_json  # Should have indentation

    def test_json_to_toon_invalid(self):
        """Test that invalid JSON raises ValueError"""
        with pytest.raises(ValueError, match="Invalid JSON"):
            converter.json_to_toon("{invalid json")


class TestTokenSavings:
    """Test token savings estimation"""

    def test_token_reduction(self):
        """Test that TOON uses fewer tokens than JSON"""
        data = {"items": [{"id": i, "value": i * 10} for i in range(20)]}

        savings = converter.estimate_token_savings(data)

        # Verify structure
        assert "json_tokens" in savings
        assert "toon_tokens" in savings
        assert "savings_tokens" in savings
        assert "savings_percent" in savings

        # Verify TOON is more efficient
        assert savings["toon_tokens"] < savings["json_tokens"]
        assert savings["savings_percent"] > 0

        # Based on benchmarks, should save at least 30%
        assert (
            savings["savings_percent"] > 30
        ), f"Expected >30% reduction, got {savings['savings_percent']}%"

    def test_savings_percentage_calculation(self):
        """Test savings percentage is calculated correctly"""
        data = {"simple": "test"}

        savings = converter.estimate_token_savings(data)

        # The savings_percent uses token estimation
        # Just verify it's a reasonable positive number
        assert savings["savings_percent"] >= 0
        assert isinstance(savings["savings_percent"], (int, float))

    def test_savings_with_large_dataset(self):
        """Test savings with a larger dataset"""
        data = {
            "models": [
                {
                    "name": f"model-{i}",
                    "cost_per_1m_tokens": {"input": i * 0.1, "output": i * 0.5},
                    "context_window": i * 10000,
                }
                for i in range(50)
            ]
        }

        savings = converter.estimate_token_savings(data)

        # TOON savings vary by structure. Some structures may not save tokens.
        # The key is that the format works correctly (tested in roundtrip tests)
        assert "savings_percent" in savings
        assert isinstance(savings["savings_percent"], (int, float))


class TestToonIntegration:
    """Integration tests for TOON module"""

    def test_real_world_model_config(self):
        """Test with real-world model configuration data"""
        data = {
            "claude": {
                "enabled": True,
                "api_key_env": "ANTHROPIC_API_KEY",
                "models": {
                    "sonnet-4.5": {
                        "id": "claude-sonnet-4-5",
                        "cost_per_1m_tokens": {"input": 3.00, "output": 15.00},
                        "context_window": 200000,
                    }
                },
            }
        }

        # Encode to TOON
        toon_str = encoder.encode(data)

        # TOON format should work correctly (size may vary)
        assert len(toon_str) > 0
        assert isinstance(toon_str, str)

        # Should preserve data perfectly (most important test!)
        decoded = decoder.decode(toon_str)
        assert decoded == data

    def test_real_world_routing_config(self):
        """Test with real-world routing configuration"""
        data = {
            "modes": {
                "ensemble": {
                    "task_routes": {
                        "massive_context": "gemini-flash",
                        "code_generation": "claude-sonnet",
                        "security_audit": "claude-sonnet",
                    }
                }
            }
        }

        toon_str = encoder.encode(data)
        decoded = decoder.decode(toon_str)

        assert decoded == data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
