"""
Unit Tests for the Telegram Alert Service.

Tests cover:
- Message formatting
- Google Maps link generation
- Alert response structure
- Unconfigured service handling
"""

import pytest
from unittest.mock import patch, AsyncMock

from m5_features.emergency.telegram_alert import TelegramAlertService
from m5_features.models.emergency_models import EmergencyAlertResponse


class TestTelegramAlertService:
    """Tests for Telegram emergency alert service."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = TelegramAlertService()

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

    def test_message_formatting(self):
        """Test alert message contains all required elements."""
        message = self.service._format_alert_message(
            latitude=24.8607,
            longitude=67.0011,
            situation="Person collapsed, not breathing",
            contact_name="Zajnan",
            contact_phone="+92-300-1234567",
        )
        assert "EMERGENCY ALERT" in message
        assert "24.8607" in message
        assert "67.0011" in message
        assert "Person collapsed, not breathing" in message
        assert "Zajnan" in message
        assert "+92-300-1234567" in message
        assert "google.com/maps" in message
        assert "PULSE" in message

    def test_message_without_contact_info(self):
        """Test message formatting without optional contact info."""
        message = self.service._format_alert_message(
            latitude=31.5204,
            longitude=74.3587,
            situation="Medical emergency",
        )
        assert "EMERGENCY ALERT" in message
        assert "Medical emergency" in message
        # Should not contain contact fields
        assert "Reported by" not in message
        assert "Phone" not in message

    def test_message_has_timestamp(self):
        """Test that message includes a timestamp."""
        message = self.service._format_alert_message(
            latitude=33.6844,
            longitude=73.0479,
            situation="Accident on highway",
        )
        assert "UTC" in message

    @pytest.mark.asyncio
    async def test_unconfigured_service_returns_not_sent(self):
        """Test that unconfigured service returns sent=False."""
        # Create service with empty credentials
        with patch.object(
            TelegramAlertService, '__init__', lambda self: None
        ):
            service = TelegramAlertService()
            service.bot_token = ""
            service.chat_id = ""
            service._configured = False

            result = await service.send_emergency_alert(
                latitude=24.8607,
                longitude=67.0011,
                situation="Test emergency",
            )
            assert result.sent is False
            assert "not configured" in result.message

    def test_karachi_coordinates(self):
        """Test with Karachi city coordinates."""
        link = self.service._build_google_maps_link(24.8607, 67.0011)
        assert "24.8607" in link
        assert "67.0011" in link

    def test_lahore_coordinates(self):
        """Test with Lahore city coordinates."""
        link = self.service._build_google_maps_link(31.5204, 74.3587)
        assert "31.5204" in link
        assert "74.3587" in link

    def test_islamabad_coordinates(self):
        """Test with Islamabad city coordinates."""
        link = self.service._build_google_maps_link(33.6844, 73.0479)
        assert "33.6844" in link
        assert "73.0479" in link


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
