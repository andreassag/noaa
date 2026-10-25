"""Backwards compatibility module - use noaa.client instead."""

from noaa.client import NOAA, Climate

# Alias for backwards compatibility
API = NOAA

__all__ = ["API", "Climate", "NOAA"]
