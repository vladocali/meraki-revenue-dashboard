# Caching utilities for Streamlit
import streamlit as st
from datetime import datetime, timedelta
from typing import Any, Callable
import hashlib
import json

def cached_function(ttl_seconds: int = 300):
    """Decorator for caching function results with TTL."""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            # Create cache key
            cache_key = f"{func.__name__}_{hashlib.md5(str(args).encode()).hexdigest()}"
            
            if cache_key not in st.session_state:
                st.session_state[cache_key] = {
                    'value': None,
                    'timestamp': None
                }
            
            cache_data = st.session_state[cache_key]
            now = datetime.now()
            
            # Check if cache is still valid
            if cache_data['timestamp'] is not None:
                age = (now - cache_data['timestamp']).total_seconds()
                if age < ttl_seconds:
                    return cache_data['value']
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_data['value'] = result
            cache_data['timestamp'] = now
            
            return result
        
        return wrapper
    return decorator

def clear_cache():
    """Clear all session cache."""
    for key in list(st.session_state.keys()):
        if isinstance(st.session_state[key], dict) and 'timestamp' in st.session_state[key]:
            del st.session_state[key]

def get_cache_status(key: str) -> dict:
    """Get status of a cache entry."""
    if key not in st.session_state:
        return {'exists': False, 'age': None}
    
    cache_data = st.session_state[key]
    age = (datetime.now() - cache_data['timestamp']).total_seconds()
    
    return {
        'exists': True,
        'age': age,
        'timestamp': cache_data['timestamp']
    }

def invalidate_cache_key(key: str):
    """Invalidate a specific cache key."""
    if key in st.session_state:
        del st.session_state[key]
