"""
Email Emergency Alert Service — Send GPS emergency notifications via Gmail.

Sends formatted emergency alert emails with:
- GPS coordinates and Google Maps link
- Situation description
- Contact information
- Timestamp

Setup:
1. Enable 2-Step Verification on your Gmail account
2. Go to myaccount.google.com → Security → App passwords
3. Create an app password for "Mail"
4. Add your email and app password to .env
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from typing import Optional

from m5_features.config import settings
from m5_features.models.emergency_models import EmergencyAlertResponse

logger = logging.getLogger(__name__)


class EmailAlertService:
    """
    Gmail SMTP-based emergency alert service.

    Sends formatted HTML emergency alert emails with:
    - GPS coordinates
    - Google Maps link for navigation
    - Situation description
    - Contact information
    - Timestamp
    """

    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587

    def __init__(self):
        """Initialize with Gmail credentials from config."""
        self.sender_email = settings.ALERT_EMAIL
        self.app_password = settings.ALERT_EMAIL_PASSWORD
        self.recipient_email = settings.ALERT_RECIPIENT_EMAIL or self.sender_email
        self._configured = bool(self.sender_email and self.app_password)

        if self._configured:
            logger.info("Email alert service configured")
        else:
            logger.warning(
                "Email alert not configured — "
                "ALERT_EMAIL and ALERT_EMAIL_PASSWORD required"
            )

    @property
    def is_configured(self) -> bool:
        """Check if email service is properly configured."""
        return self._configured

    def _build_google_maps_link(
        self, latitude: float, longitude: float
    ) -> str:
        """Generate a Google Maps link for the given coordinates."""
        return f"https://www.google.com/maps?q={latitude},{longitude}"

    def _build_html_message(
        self,
        latitude: float,
        longitude: float,
        situation: str,
        contact_name: Optional[str] = None,
        contact_phone: Optional[str] = None,
    ) -> str:
        """Build a rich HTML email body for the emergency alert."""
        maps_link = self._build_google_maps_link(latitude, longitude)
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        contact_section = ""
        if contact_name or contact_phone:
            contact_section = "<tr><td colspan='2' style='padding:12px;background:#f0f9ff;border-radius:8px;'>"
            if contact_name:
                contact_section += f"<strong>👤 Reported by:</strong> {contact_name}<br>"
            if contact_phone:
                contact_section += f"<strong>📞 Phone:</strong> {contact_phone}"
            contact_section += "</td></tr>"

        return f"""
        <html>
        <body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
            <div style="background:linear-gradient(135deg,#dc2626,#b91c1c);color:white;padding:20px;border-radius:12px;text-align:center;">
                <h1 style="margin:0;font-size:24px;">🚨 EMERGENCY ALERT</h1>
                <p style="margin:8px 0 0;font-size:14px;opacity:0.9;">PULSE — AI Health Intelligence Network</p>
            </div>

            <table style="width:100%;border-collapse:collapse;margin-top:20px;">
                <tr>
                    <td style="padding:16px;background:#fef2f2;border-radius:8px;border-left:4px solid #dc2626;">
                        <strong style="color:#dc2626;font-size:16px;">⚠️ Situation</strong><br>
                        <span style="font-size:15px;color:#1f2937;">{situation}</span>
                    </td>
                </tr>
            </table>

            <table style="width:100%;border-collapse:collapse;margin-top:16px;">
                <tr>
                    <td style="padding:16px;background:#f0fdf4;border-radius:8px;border-left:4px solid #16a34a;">
                        <strong style="color:#16a34a;font-size:16px;">📍 Location</strong><br>
                        <span style="font-size:14px;color:#374151;">
                            Latitude: <code>{latitude:.6f}</code><br>
                            Longitude: <code>{longitude:.6f}</code>
                        </span><br><br>
                        <a href="{maps_link}" style="display:inline-block;background:#16a34a;color:white;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:bold;">
                            📌 Open in Google Maps
                        </a>
                    </td>
                </tr>
            </table>

            <table style="width:100%;border-collapse:collapse;margin-top:16px;">
                {contact_section}
            </table>

            <div style="margin-top:20px;padding:12px;background:#f3f4f6;border-radius:8px;text-align:center;">
                <span style="font-size:12px;color:#6b7280;">
                    🕐 Sent at {timestamp}<br>
                    ⚡ Automated alert by PULSE Emergency System
                </span>
            </div>
        </body>
        </html>
        """

    def _build_plain_message(
        self,
        latitude: float,
        longitude: float,
        situation: str,
        contact_name: Optional[str] = None,
        contact_phone: Optional[str] = None,
    ) -> str:
        """Build a plain text fallback for email clients that don't support HTML."""
        maps_link = self._build_google_maps_link(latitude, longitude)
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        lines = [
            "🚨 EMERGENCY ALERT — PULSE 🚨",
            "",
            f"⚠️ SITUATION: {situation}",
            "",
            f"📍 LOCATION:",
            f"   Lat: {latitude:.6f}",
            f"   Lng: {longitude:.6f}",
            f"   Map: {maps_link}",
            "",
        ]
        if contact_name:
            lines.append(f"👤 Reported by: {contact_name}")
        if contact_phone:
            lines.append(f"📞 Phone: {contact_phone}")
        lines.extend([
            "",
            f"🕐 Time: {timestamp}",
            "⚡ Sent by PULSE — AI Health Intelligence Network",
        ])
        return "\n".join(lines)

    async def send_emergency_alert(
        self,
        latitude: float,
        longitude: float,
        situation: str,
        contact_name: Optional[str] = None,
        contact_phone: Optional[str] = None,
    ) -> EmergencyAlertResponse:
        """
        Send an emergency alert email via Gmail SMTP.

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
            logger.warning("Email alert not configured — alert not sent")
            return EmergencyAlertResponse(
                sent=False,
                message=(
                    "Email alert service not configured. "
                    "Set ALERT_EMAIL and ALERT_EMAIL_PASSWORD in .env"
                ),
                google_maps_link=maps_link,
                timestamp=timestamp,
            )

        try:
            # Build email
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"🚨 PULSE EMERGENCY ALERT — {situation[:50]}"
            msg["From"] = self.sender_email
            msg["To"] = self.recipient_email

            # Plain text version
            plain_body = self._build_plain_message(
                latitude, longitude, situation, contact_name, contact_phone
            )
            msg.attach(MIMEText(plain_body, "plain"))

            # HTML version
            html_body = self._build_html_message(
                latitude, longitude, situation, contact_name, contact_phone
            )
            msg.attach(MIMEText(html_body, "html"))

            # Send via Gmail SMTP
            with smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT) as server:
                server.starttls()
                server.login(self.sender_email, self.app_password)
                server.send_message(msg)

            logger.info(
                f"Emergency alert email sent to {self.recipient_email}"
            )
            return EmergencyAlertResponse(
                sent=True,
                message=f"Emergency alert sent to {self.recipient_email}",
                google_maps_link=maps_link,
                timestamp=timestamp,
            )

        except smtplib.SMTPAuthenticationError:
            logger.error("Gmail authentication failed — check app password")
            return EmergencyAlertResponse(
                sent=False,
                message="Email auth failed — check ALERT_EMAIL_PASSWORD (use Gmail App Password, not regular password)",
                google_maps_link=maps_link,
                timestamp=timestamp,
            )
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return EmergencyAlertResponse(
                sent=False,
                message=f"Email alert failed: {str(e)}",
                google_maps_link=maps_link,
                timestamp=timestamp,
            )


# Singleton instance
email_alert_service = EmailAlertService()
