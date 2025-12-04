from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from flask import current_app


def send_email(subject: str, to: str, body_text: str, body_html: str | None = None) -> bool:
    """Send an email using SMTP configured via env vars.

    Falls back to logging the message (development) when SMTP not configured.
    Returns True when email was 'sent' or logged, False on error.
    """
    try:
        mail_from = os.getenv("MAIL_FROM", os.getenv("SMTP_USER") or "no-reply@example.dev")
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", "0") or 0)
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASS")

        current_app.logger.info(f"Mail config: host={smtp_host}, port={smtp_port}, user={smtp_user}")

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = mail_from
        msg["To"] = to
        msg.set_content(body_text)
        if body_html:
            msg.add_alternative(body_html, subtype="html")

        if smtp_host and smtp_port and smtp_user and smtp_pass:
            # attempt real SMTP
            try:
                current_app.logger.info(f"Attempting SMTP connection to {smtp_host}:{smtp_port}")
                if smtp_port == 465:
                    server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10)
                else:
                    server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
                    server.starttls()
                current_app.logger.info(f"TLS/SSL established, logging in as {smtp_user}")
                server.login(smtp_user, smtp_pass)
                current_app.logger.info(f"Login successful, sending to {to}")
                server.send_message(msg)
                server.quit()
                current_app.logger.info(f"Email sent successfully to {to}")
                return True
            except smtplib.SMTPAuthenticationError as e:
                current_app.logger.error(f"SMTP Auth failed: {e}")
                # fall through to logging
            except smtplib.SMTPException as e:
                current_app.logger.error(f"SMTP error: {e}")
                # fall through to logging
            except Exception as e:
                # fall through to logging
                current_app.logger.error(f"SMTP send failed, falling back to log: {e}")

        # Fallback: log the email to app logger for development
        current_app.logger.warning(f"--- EMAIL Fallback (SMTP not configured or failed) ---\nTo: {to}\nSubject: {subject}\n{body_text}\n---------------------")
        return True
    except Exception as exc:
        try:
            current_app.logger.exception(f"send_email error: {exc}")
        except Exception:
            pass
        return False
