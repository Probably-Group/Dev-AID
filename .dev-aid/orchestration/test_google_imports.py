#!/usr/bin/env python3
"""
Verify google-genai SDK imports and client instantiation
"""

import sys
from pathlib import Path

# Add router to path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test that new google-genai imports work"""
    print("🔧 Testing imports...")

    try:
        from google import genai
        from google.genai import types

        print("✅ google.genai imports successful")

        # Verify client can be instantiated
        client = genai.Client(api_key="dummy-key-for-testing")
        print(f"✅ Client instantiated: {type(client)}")

        # Verify types are available
        config = types.GenerateContentConfig(temperature=0.7, max_output_tokens=100)
        print(f"✅ GenerateContentConfig created: {type(config)}")

        return True

    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        return False


def test_client_class():
    """Test that GoogleClient class works with new SDK"""
    print("\n🔧 Testing GoogleClient class...")

    try:
        from router.api_clients import GoogleClient

        # Instantiate client
        client = GoogleClient(
            api_key="dummy-key-for-testing",
            model_config={
                "provider": "google",
                "cost_per_1m_tokens": {"input": 0.35, "output": 1.05},
            },
        )

        print(f"✅ GoogleClient instantiated: {type(client)}")
        print(f"   Provider: {client.provider}")
        print(f"   Has client: {hasattr(client, 'client')}")
        print(f"   Has types: {hasattr(client, 'types')}")

        return True

    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Google Gemini SDK Import Verification")
    print("=" * 60)

    success = test_imports() and test_client_class()

    print("\n" + "=" * 60)
    if success:
        print("✅ All import checks PASSED")
        print("\nThe google-genai migration is syntactically correct.")
        print("To test with live API, set GOOGLE_API_KEY and run:")
        print("  python test_google_migration.py")
        sys.exit(0)
    else:
        print("❌ Import checks FAILED")
        sys.exit(1)
