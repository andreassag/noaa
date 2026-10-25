"""Tests for backwards compatibility module."""

from noaa.client import NOAA as ClientNOAA
from noaa.climate import API, NOAA


class TestBackwardsCompatibility:
    """Tests for backwards compatibility."""

    def test_api_alias(self):
        """API should be alias for NOAA."""
        assert API is NOAA

    def test_noaa_is_client_noaa(self):
        """NOAA should be the client NOAA class."""
        assert NOAA is ClientNOAA

    def test_climate_export(self):
        """Climate should be exported and match NOAA."""
        from noaa.climate import Climate

        assert Climate is NOAA

    def test_can_create_client_with_api(self):
        """Should be able to create client using API alias."""
        client = API("test-token")
        assert isinstance(client, ClientNOAA)
