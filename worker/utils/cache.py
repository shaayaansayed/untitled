import hashlib
import json
import os

from config.settings import settings


class DevelopmentCache:
    """Simple file-based cache for development"""

    @staticmethod
    def _get_cache_key(pdf_path: str, **kwargs) -> str:
        """Generate cache key from PDF path and parameters"""
        cache_input = f"{pdf_path}_{str(sorted(kwargs.items()))}"
        return hashlib.md5(cache_input.encode()).hexdigest()

    @staticmethod
    def get_cached_response(pdf_path: str, **kwargs) -> str:
        """Get cached response if it exists"""
        if not settings.DEVELOPMENT_MODE:
            return None

        cache_key = DevelopmentCache._get_cache_key(pdf_path, **kwargs)
        cache_file = os.path.join(settings.CACHE_DIR, f"{cache_key}.json")

        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                return json.load(f)["markdown"]

        return None

    @staticmethod
    def cache_response(pdf_path: str, markdown: str, **kwargs):
        """Cache the response for future use"""
        if not settings.DEVELOPMENT_MODE:
            return

        os.makedirs(settings.CACHE_DIR, exist_ok=True)
        cache_key = DevelopmentCache._get_cache_key(pdf_path, **kwargs)
        cache_file = os.path.join(settings.CACHE_DIR, f"{cache_key}.json")

        with open(cache_file, "w") as f:
            json.dump(
                {"pdf_path": pdf_path, "params": kwargs, "markdown": markdown},
                f,
                indent=2,
            )
