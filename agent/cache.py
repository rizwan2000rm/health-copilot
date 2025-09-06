"""
Response caching module for the AI Fitness Coach.

This module provides a simple file-based caching system to store and retrieve
AI responses for faster repeated queries.
"""

import os
import json
import hashlib
from typing import Optional


class ResponseCache:
    """Simple file-based cache for AI responses."""
    
    def __init__(self, cache_file: str = "response_cache.json"):
        """
        Initialize the response cache.
        
        Args:
            cache_file: Path to the cache file for persistence
        """
        self.cache_file = cache_file
        self.cache = self.load_cache()
    
    def load_cache(self) -> dict:
        """Load cache from file."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def save_cache(self) -> None:
        """Save cache to file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f)
        except Exception:
            pass
    
    def get_cache_key(self, query: str) -> str:
        """
        Generate cache key for query.
        
        Args:
            query: The user query to generate a key for
            
        Returns:
            MD5 hash of the normalized query
        """
        return hashlib.md5(query.lower().strip().encode()).hexdigest()
    
    def get(self, query: str) -> Optional[str]:
        """
        Get cached response for a query.
        
        Args:
            query: The user query
            
        Returns:
            Cached response if found, None otherwise
        """
        key = self.get_cache_key(query)
        return self.cache.get(key)
    
    def set(self, query: str, response: str) -> None:
        """
        Cache a response for a query.
        
        Args:
            query: The user query
            response: The AI response to cache
        """
        key = self.get_cache_key(query)
        self.cache[key] = response
        self.save_cache()
    
    def clear(self) -> None:
        """Clear all cached responses."""
        self.cache = {}
        self.save_cache()
    
    def size(self) -> int:
        """Get the number of cached responses."""
        return len(self.cache)
