"""Supabase client configuration and initialization."""

from supabase import create_client, Client
from app.core.config import settings


def get_supabase_client() -> Client:
    """
    Create and return a Supabase client instance.
    
    Returns:
        Supabase client instance
        
    Raises:
        ValueError: If Supabase URL or key is not configured
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise ValueError(
            "Supabase is not configured. Please set SUPABASE_URL and SUPABASE_KEY environment variables."
        )
    
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


# Global client instance (lazy initialization)
_supabase_client: Client | None = None


def get_supabase() -> Client:
    """
    Get or create the global Supabase client instance.
    
    Returns:
        Supabase client instance
    """
    global _supabase_client
    
    if _supabase_client is None:
        _supabase_client = get_supabase_client()
    
    return _supabase_client
