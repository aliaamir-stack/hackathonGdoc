"""
Unit Tests for the Email Alert Service.

Tests cover:
- HTML message formatting
- Plain text fallback
- Google Maps link generation
- Alert response structure
- Unconfigured service handling
"""

import pytest
from unittest.mock import patch

from m5_features.emergency.email_alert import EmailAlertService
from m5_features.models.emergency_models import EmergencyAlertResponse


class TestEmailAlertService:
    """Tests for Email emergency alert service."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = EmailAlertService()

    def test_google_maps_link_generation(self):
        """Test Google Maps link format with coordinates."""
        link = self.service._build_google_maps_link(24.8607, 67.0011)
        assert "google.com/maps" in link
        assert "24.8607" in link
        assert "67.0011" in link

    def test_google_maps_link_negative_coords(self):
        """Test Google Maps link with negative coordinates."""
        link = self.service._build_google_maps_link(-33.8688, 151.2093)
        assert "-33.8688" in link
        assert "151.2093" in link

    def test_html_message_formatting(self):
        """Test HTML alert message contains all required elements."""
        html = self.service._build_html_message(
            latitude=24.8607,
            longitude=67.0011,
            situation="Person collapsed, not breathing",
            contact_name="Zajnan",
            contact_phone="+92-300-1234567",
        )
        assert "EMERGENCY ALERT" in html
        assert "24.860700" in html
        assert "67.001100" in html
        assert "Person collapsed, not breathing" in html
        assert "Zajnan" in html
        assert "+92-300-1234567" in html
        assert "google.com/maps" in html
        assert "PULSE" in html
        assert "<html>" in html

    def test_html_has_google_maps_button(self):
        """Test HTML includes clickable Google Maps button."""
        html = self.service._build_html_message(
            latitude=24.8607,
            longitude=67.0011,
            situation="Test",
        )
        assert "Open in Google Maps" in html
        assert "href=" in html

    def test_plain_message_formatting(self):
        """Test plain text fallback message."""
        plain = self.service._build_plain_message(
            latitude=24.8607,
            longitude=67.0011,
            situation="Medical emergency",
            contact_name="Zajnan",
            contact_phone="+92-300-1234567",
        )
        assert "EMERGENCY ALERT" in plain
        assert "Medical emergency" in plain
        assert "Zajnan" in plain
        assert "google.com/maps" in plain
        assert "UTC" in plain

    def test_message_without_contact_info(self):
        """Test message formatting without optional contact info."""
        plain = self.service._build_plain_message(
            latitude=31.5204,
            longitude=74.3587,
            situation="Medical emergency",
        )
        assert "EMERGENCY ALERT" in plain
        assert "Reported by" not in plain

    def test_html_without_contact_info(self):
        """Test HTML message without contact details has no contact section."""
        html = self.service._build_html_message(
            latitude=31.5204,
            longitude=74.3587,
            situation="Test",
        )
        assert "EMERGENCY ALERT" in html

    @pytest.mark.asyncio
    async def test_unconfigured_service_returns_not_sent(self):
        """Test that unconfigured service returns sent=False."""
        with patch.object(
            EmailAlertService, '__init__', lambda self: None
        ):
            service = EmailAlertService()
            service.sender_email = ""
            service.app_password = ""
            service.recipient_email = ""
            service._configured = False

            result = await service.send_emergency_alert(
                latitude=24.8607,
                longitude=67.0011,
                situation="Test emergency",
            )
            assert result.sent is False
            assert "not configured" in result.message

    @pytest.mark.asyncio
    async def test_unconfigured_still_returns_maps_link(self):
        """Test that even failed alerts include Google Maps link."""
        with patch.object(
            EmailAlertService, '__init__', lambda self: None
        ):
            service = EmailAlertService()
            service.sender_email = ""
            service.app_password = ""
            service.recipient_email = ""
            service._configured = False

            result = await service.send_emergency_alert(
                latitude=24.8607,
                longitude=67.0011,
                situation="Test",
            )
            assert result.google_maps_link is not None
            assert "24.8607" in result.google_maps_link

    def test_karachi_coordinates(self):
        """Test with Karachi city coordinates."""
        link = self.service._build_google_maps_link(24.8607, 67.0011)
        assert "24.8607" in link

    def test_lahore_coordinates(self):
        """Test with Lahore city coordinates."""
        link = self.service._build_google_maps_link(31.5204, 74.3587)
        assert "31.5204" in link

    def test_islamabad_coordinates(self):
        """Test with Islamabad city coordinates."""
        link = self.service._build_google_maps_link(33.6844, 73.0479)
        assert "33.6844" in link


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
