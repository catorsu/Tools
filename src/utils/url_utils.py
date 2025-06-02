"""
URL utility functions for the crawler
"""

from urllib.parse import urljoin, urlparse, urlunparse
import re


def normalize_url(url):
    """
    Normalize a URL by removing fragments and ensuring proper format
    """
    parsed = urlparse(url)
    # Remove fragment (everything after #)
    normalized = urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            "",  # No fragment
        )
    )
    return normalized


def is_valid_url(url):
    """
    Check if a URL is valid
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def resolve_relative_url(base_url, relative_url):
    """
    Resolve a relative URL against a base URL
    """
    return urljoin(base_url, relative_url)


def url_matches_prefix(url, prefix):
    """
    Check if a URL starts with the given prefix
    """
    return url.startswith(prefix)


def get_domain_from_url(url):
    """
    Extract domain from URL
    """
    parsed = urlparse(url)
    return parsed.netloc


def clean_url_for_display(url):
    """
    Clean URL for display purposes
    """
    return url.strip()
