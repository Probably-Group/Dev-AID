"""
VCR.py configuration for API client testing

This module provides VCR configuration to record and replay HTTP interactions
for testing AI API clients without incurring costs or exposing API keys.
"""

import vcr
import os
from pathlib import Path


# Cassettes directory
CASSETTES_DIR = Path(__file__).parent / "cassettes"
CASSETTES_DIR.mkdir(exist_ok=True)


def scrub_request(request):
    """
    Sanitize request to remove sensitive data before recording.

    This prevents API keys from being committed to cassettes.
    """
    # Remove authorization headers
    if 'authorization' in request.headers:
        request.headers['authorization'] = ['REDACTED']

    if 'x-api-key' in request.headers:
        request.headers['x-api-key'] = ['REDACTED']

    # Anthropic API key header
    if 'anthropic-api-key' in request.headers:
        request.headers['anthropic-api-key'] = ['REDACTED']

    # OpenAI API key header
    if 'openai-api-key' in request.headers:
        request.headers['openai-api-key'] = ['REDACTED']

    return request


def scrub_response(response):
    """
    Sanitize response to remove sensitive data before recording.
    """
    # Response bodies typically don't contain secrets, but check anyway
    return response


# VCR instance with custom configuration
api_vcr = vcr.VCR(
    cassette_library_dir=str(CASSETTES_DIR),
    record_mode='once',  # Record once, then replay
    match_on=['method', 'scheme', 'host', 'port', 'path', 'query'],
    filter_headers=['authorization', 'x-api-key', 'anthropic-api-key', 'openai-api-key'],
    before_record_request=scrub_request,
    before_record_response=scrub_response,
    decode_compressed_response=True,
)


# Pytest fixture-friendly decorator
def use_cassette(cassette_name):
    """
    Decorator to use a VCR cassette for a test.

    Usage:
        @use_cassette('anthropic_simple_request.yaml')
        def test_anthropic_api():
            # Test code here
            pass
    """
    return api_vcr.use_cassette(cassette_name)
