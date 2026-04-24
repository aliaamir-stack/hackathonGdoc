"""
Telegram Emergency Alert Service — Send GPS emergency notifications.

Sends formatted emergency alert messages via Telegram bot
with GPS coordinates, Google Maps link, situation description,
and contact information.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from m5_features.config import settings
from m5_features.models.emergency_models import EmergencyAlertResponse

logger = logging.getLogger(__name__)


class TelegramAlertService:
    """
    Telegram bot-based emergency alert service.

    Sends emergency notifications with:
    - GPS coordinates
    - Google Maps link for navigation
    - Situation description
    - Contact information
    - Timestamp
    """

    def __init__(self):
        """Initialize with bot token and chat ID from config."""
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self._configured = bool(self.bot_token and self.chat_id)

        if self._configured:
            logger.info("Telegram alert service configured")
        else:
            logger.warning(
                "Telegram not configured — "
                "TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID required"
            )

    @property
    def is_configured(self) -> bool:
        """Check if Telegram service is properly configured."""
        return self._configured

    def _build_google_maps_link(
        self, latitude: float, longitude: float
    ) -> str:
        """Generate a Google Maps link for the given coordinates."""
        return f"https://www.google.com/maps?q={latitude},{longitude}"

    def _format_alert_message(
        self,
        latitude: float,
        longitude: float,
        situation: str,
        contact_name: Optional[str] = None,
        contact_phone: Optional[str] = None,
    ) -> str:
        """
        Format the emergency alert message for Telegram.

        Uses Telegram markdown formatting for readability.
        """
        maps_link = self._build_google_maps_link(latitude, longitude)
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        message_parts = [
            "🚨 *EMERGENCY ALERT — PULSE* 🚨",
            "",
            f"📍 *Location:*",
            f"   Lat: `{latitude:.6f}`",
            f"   Lng: `{longitude:.6f}`",
            f"   [Open in Google Maps]({maps_link})",
            "",
            f"⚠️ *Situation:*",
            f"   {situation}",
            "",
        ]

        if contact_name:
            message_parts.append(f"👤 *Reported by:* {contact_name}")
        if contact_phone:
            message_parts.append(f"📞 *Phone:* {contact_phone}")

        message_parts.extend([
            "",
            f"🕐 *Time:* {timestamp}",
            "",
            "⚡ *This alert was sent automatically by PULSE*",
            "⚡ *AI-Powered Community Health Intelligence Network*",
        ])

        return "\n".join(message_parts)

    async def send_emergency_alert(
        self,
        latitude: float,
        longitude: float,
        situation: str,
        contact_name: Optional[str] = None,
        contact_phone: Optional[str] = None,
    ) -> EmergencyAlertResponse:
        """
        Send an emergency alert message via Telegram.

        Args:
            latitude: GPS latitude of the emergency
            longitude: GPS longitude of the emergency
            situation: Brief description of the emergency
            contact_name: Optional name of the reporter
            contact_phone: Optional phone number for callback

        Returns:
            EmergencyAlertResponse with send status
        """
        maps_link = self._build_google_maps_link(latitude, longitude)
        timestamp = datetime.now(timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        )

        if not self._configured:
            logger.warning("Telegram not configured — alert not sent")
            return EmergencyAlertResponse(
                sent=False,
                message=(
                    "Telegram alert service not configured. "
                    "Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID."
                ),
                google_maps_link=maps_link,
                timestamp=timestamp,
            )

        try:
            import httpx

            # Format message
            message = self._format_alert_message(
                latitude=latitude,
                longitude=longitude,
                situation=situation,
                contact_name=contact_name,
                contact_phone=contact_phone,
            )

            # Send via Telegram Bot API
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": False,
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)

                if response.status_code == 200:
                    result = response.json()
                    if result.get("ok"):
                        logger.info(
                            f"Emergency alert sent successfully to chat {self.chat_id}"
                        )

                        # Also send location pin
                        await self._send_location(
                            client, latitude, longitude
                        )

                        return EmergencyAlertResponse(
                            sent=True,
                            message="Emergency alert sent via Telegram",
                            google_maps_link=maps_link,
                            timestamp=timestamp,
                        )

                logger.error(
                    f"Telegram API error: {response.status_code} — "
                    f"{response.text}"
                )
                return EmergencyAlertResponse(
                    sent=False,
                    message=f"Telegram API error: {response.status_code}",
                    google_maps_link=maps_link,
                    timestamp=timestamp,
                )

        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
            return EmergencyAlertResponse(
                sent=False,
                message=f"Alert failed: {str(e)}",
                google_maps_link=maps_link,
                timestamp=timestamp,
            )

    async def _send_location(
        self,
        client,
        latitude: float,
        longitude: float,
    ) -> None:
        """
        Send a location pin to the Telegram chat.

        This appears as a clickable map pin in Telegram,
        making it easy for the recipient to get directions.
        """
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendLocation"
            payload = {
                "chat_id": self.chat_id,
                "latitude": latitude,
                "longitude": longitude,
            }
            await client.post(url, json=payload)
            logger.info("Location pin sent to Telegram")
        except Exception as e:
            logger.warning(f"Failed to send location pin: {e}")


# Singleton instance
telegram_alert_service = TelegramAlertService()
