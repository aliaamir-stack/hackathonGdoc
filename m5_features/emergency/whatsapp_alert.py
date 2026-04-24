"""
WhatsApp Emergency Alert Service — Send GPS emergency notifications.

Sends formatted emergency alert messages via WhatsApp
using the CallMeBot free API with GPS coordinates,
Google Maps link, and situation description.

Setup (one-time):
1. Save the number +34 644 31 22 77 in your phone contacts
2. Send "I allow callmebot to send me messages" to that number on WhatsApp
3. Wait for the confirmation and API key
4. Add your phone number and API key to .env
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import quote

import httpx

from m5_features.config import settings
from m5_features.models.emergency_models import EmergencyAlertResponse

logger = logging.getLogger(__name__)


class WhatsAppAlertService:
    """
    WhatsApp-based emergency alert service via CallMeBot API.

    Sends emergency notifications with:
    - GPS coordinates
    - Google Maps link for navigation
    - Situation description
    - Contact information
    - Timestamp
    """

    CALLMEBOT_URL = "https://api.callmebot.com/whatsapp.php"

    def __init__(self):
        """Initialize with phone number and API key from config."""
        self.phone_number = settings.WHATSAPP_PHONE
        self.api_key = settings.WHATSAPP_API_KEY
        self._configured = bool(self.phone_number and self.api_key)

        if self._configured:
            logger.info("WhatsApp alert service configured")
        else:
            logger.warning(
                "WhatsApp not configured — "
                "WHATSAPP_PHONE and WHATSAPP_API_KEY required"
            )

    @property
    def is_configured(self) -> bool:
        """Check if WhatsApp service is properly configured."""
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
        Format the emergency alert message for WhatsApp.

        Uses plain text formatting (WhatsApp supports *bold*).
        """
        maps_link = self._build_google_maps_link(latitude, longitude)
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        message_parts = [
            "🚨 *EMERGENCY ALERT — PULSE* 🚨",
            "",
            f"📍 *Location:*",
            f"   Lat: {latitude:.6f}",
            f"   Lng: {longitude:.6f}",
            f"   📌 {maps_link}",
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
            "⚡ _Sent by PULSE — AI Health Intelligence Network_",
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
        Send an emergency alert message via WhatsApp.

        Uses CallMeBot free API to deliver WhatsApp messages
        without needing a business account or paid service.

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
            logger.warning("WhatsApp not configured — alert not sent")
            return EmergencyAlertResponse(
                sent=False,
                message=(
                    "WhatsApp alert service not configured. "
                    "Set WHATSAPP_PHONE and WHATSAPP_API_KEY in .env"
                ),
                google_maps_link=maps_link,
                timestamp=timestamp,
            )

        try:
            # Format message
            message = self._format_alert_message(
                latitude=latitude,
                longitude=longitude,
                situation=situation,
                contact_name=contact_name,
                contact_phone=contact_phone,
            )

            # URL-encode the message for CallMeBot API
            encoded_message = quote(message)

            # Send via CallMeBot WhatsApp API
            url = (
                f"{self.CALLMEBOT_URL}"
                f"?phone={self.phone_number}"
                f"&text={encoded_message}"
                f"&apikey={self.api_key}"
            )

            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url)

                if response.status_code == 200:
                    response_text = response.text.lower()
                    if "message queued" in response_text or "sent" in response_text:
                        logger.info(
                            f"Emergency alert sent via WhatsApp to {self.phone_number}"
                        )
                        return EmergencyAlertResponse(
                            sent=True,
                            message="Emergency alert sent via WhatsApp",
                            google_maps_link=maps_link,
                            timestamp=timestamp,
                        )

                logger.error(
                    f"CallMeBot API error: {response.status_code} — "
                    f"{response.text[:200]}"
                )
                return EmergencyAlertResponse(
                    sent=False,
                    message=f"WhatsApp API error: {response.status_code}",
                    google_maps_link=maps_link,
                    timestamp=timestamp,
                )

        except httpx.TimeoutException:
            logger.error("WhatsApp alert request timed out")
            return EmergencyAlertResponse(
                sent=False,
                message="WhatsApp alert timed out — try again",
                google_maps_link=maps_link,
                timestamp=timestamp,
            )
        except Exception as e:
            logger.error(f"Failed to send WhatsApp alert: {e}")
            return EmergencyAlertResponse(
                sent=False,
                message=f"Alert failed: {str(e)}",
                google_maps_link=maps_link,
                timestamp=timestamp,
            )


# Singleton instance
whatsapp_alert_service = WhatsAppAlertService()
