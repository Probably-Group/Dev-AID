#!/usr/bin/env python3
"""
Quick test script to verify google-genai migration works
"""
import os
import sys
from pathlib import Path

# Add router to path
sys.path.insert(0, str(Path(__file__).parent))

from router.api_clients import GoogleClient, Message  # noqa: E402


def test_google_client():
    """Test Google client with new google-genai SDK"""

    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️  GOOGLE_API_KEY not set - skipping test")
        print("   Set it with: export GOOGLE_API_KEY='your-key-here'")
        return False

    try:
        # Create client
        print("🔧 Creating GoogleClient...")
        client = GoogleClient(
            api_key=api_key,
            model_config={
                "provider": "google",
                "cost_per_1m_tokens": {"input": 0.35, "output": 1.05},
            },
        )
        print("✅ Client created successfully")

        # Test simple generation
        print("\n🧪 Testing single-turn generation...")
        messages = [
            Message(role="user", content="Say 'Hello from Google Gemini!' and nothing else.")
        ]

        response = client.send_request(
            messages=messages, model="gemini-2.0-flash-exp", max_tokens=50, temperature=0.0
        )

        print(f"✅ Response received: {response.content[:100]}")
        print(f"   Model: {response.model}")
        print(f"   Provider: {response.provider}")
        print(f"   Tokens: {response.tokens_used}")
        print(f"   Cost: ${response.cost:.6f}")
        print(f"   Latency: {response.latency_ms:.2f}ms")

        # Verify response structure
        assert response.content, "Response content is empty"
        assert response.model == "gemini-2.0-flash-exp", f"Model mismatch: {response.model}"
        assert response.provider == "google", f"Provider mismatch: {response.provider}"
        assert response.tokens_used["input"] > 0, "Input tokens not tracked"
        assert response.tokens_used["output"] > 0, "Output tokens not tracked"

        print("\n✅ All checks passed!")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {type(e).__name__}: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Google Gemini SDK Migration Test")
    print("=" * 60)

    success = test_google_client()

    print("\n" + "=" * 60)
    if success:
        print("✅ Migration verification PASSED")
        sys.exit(0)
    else:
        print("⚠️  Migration verification SKIPPED or FAILED")
        sys.exit(1)
