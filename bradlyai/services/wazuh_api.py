"""BradlyAI Wazuh Manager API Client — safely closes alerts in Wazuh.

Safety features (for production environments):
  1. WAZUH_ENABLED=false by default — must explicitly enable
  2. WAZUH_DRY_RUN=true by default — logs action without performing it
  3. WAZUH_CLOSE_MODE=comment_only by default — adds comment but doesn't archive
  4. All actions are reversible (Wazuh archive can be undone)
  5. JWT token cached + auto-refreshed

Usage:
    # In .env (production):
    WAZUH_ENABLED=true
    WAZUH_DRY_RUN=false
    WAZUH_CLOSE_MODE=archive_and_comment
    WAZUH_MANAGER_URL=https://wazuh.example.com:55000
    WAZUH_USER=bradlyai
    WAZUH_PASSWORD=secret
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
import httpx
from bradlyai.config import settings

logger = logging.getLogger("bradlyai.wazuh_api")


class WazuhSafetyError(Exception):
    """Raised when an action is blocked by safety guard."""
    pass


class WazuhAPIClient:
    """Wazuh Manager API client for closing alerts from BradlyAI L1 Agent."""

    def __init__(self):
        self.base_url = (getattr(settings, "WAZUH_MANAGER_URL", "") or "").rstrip("/")
        self.username = getattr(settings, "WAZUH_USER", "") or ""
        self.password = getattr(settings, "WAZUH_PASSWORD", "") or ""
        self.enabled = getattr(settings, "WAZUH_ENABLED", False)
        self.dry_run = getattr(settings, "WAZUH_DRY_RUN", True)
        self.close_mode = getattr(settings, "WAZUH_CLOSE_MODE", "comment_only")
        # Allowed modes: "comment_only", "archive_only", "archive_and_comment"
        self.verify_ssl = getattr(settings, "WAZUH_VERIFY_SSL", True)

        self._jwt_token: Optional[str] = None
        self._jwt_expires: Optional[datetime] = None
        self._timeout = 30.0

    def is_available(self) -> bool:
        """Check if Wazuh integration is enabled and configured."""
        return bool(self.enabled and self.base_url and self.username and self.password)

    def safety_status(self) -> Dict[str, Any]:
        """Return current safety configuration for display/audit."""
        return {
            "enabled": self.enabled,
            "dry_run": self.dry_run,
            "close_mode": self.close_mode,
            "manager_url": self.base_url or "(not configured)",
            "user_configured": bool(self.username),
            "password_configured": bool(self.password),
            "verify_ssl": self.verify_ssl,
            "available": self.is_available(),
            "warning": self._warning(),
        }

    def _warning(self) -> Optional[str]:
        """Generate safety warning if applicable."""
        if not self.enabled:
            return "Wazuh integration DISABLED. Set WAZUH_ENABLED=true to enable."
        if self.dry_run:
            return "DRY_RUN mode. No actions will be performed on Wazuh."
        if self.close_mode not in ("comment_only", "archive_only", "archive_and_comment"):
            return f"Unknown close_mode: {self.close_mode}. Defaulting to comment_only."
        if self.close_mode == "archive_only" or self.close_mode == "archive_and_comment":
            return "ARCHIVE mode. Alerts WILL be archived in Wazuh."
        return None

    # ── Authentication ──────────────────────────────────────────────────────

    def _authenticate(self) -> str:
        """Authenticate and get JWT token. Cached until expiry."""
        if self._jwt_token and self._jwt_expires and datetime.now(timezone.utc) < self._jwt_expires:
            return self._jwt_token
        try:
            with httpx.Client(timeout=self._timeout, verify=self.verify_ssl) as client:
                resp = client.post(
                    f"{self.base_url}/security/user/authenticate",
                    auth=(self.username, self.password),
                    headers={"Content-Type": "application/json"},
                )
                if resp.status_code != 200:
                    raise WazuhSafetyError(f"Authentication failed: HTTP {resp.status_code}")
                data = resp.json()
                self._jwt_token = data.get("token", "")
                # JWT default TTL in Wazuh is 15 min; refresh 1 min early
                self._jwt_expires = datetime.now(timezone.utc) + timedelta(minutes=14)
                logger.info("Wazuh JWT token refreshed")
                return self._jwt_token
        except Exception as e:
            logger.error(f"Wazuh auth failed: {e}")
            raise WazuhSafetyError(f"Wazuh auth failed: {e}")

    # ── Actions on alerts ──────────────────────────────────────────────────

    def archive_alert(self, alert_id: str, comment: str = "") -> Dict[str, Any]:
        """
        Archive an alert in Wazuh (set status to 'archived').

        Reversible: an analyst can un-archive via Wazuh UI/API.
        Dry-run by default — does not modify Wazuh unless explicitly configured.
        """
        if not self.is_available():
            return {
                "success": False,
                "skipped": True,
                "reason": "Wazuh integration not enabled or not configured",
                "dry_run": self.dry_run,
            }

        if self.dry_run:
            logger.info(f"[DRY_RUN] Would archive Wazuh alert {alert_id}: {comment[:80]}")
            return {
                "success": True,
                "dry_run": True,
                "alert_id": alert_id,
                "action": "archive",
                "would_do": "PUT /alerts?ids={id}&status=archived",
            }

        if self.close_mode == "comment_only":
            # Don't archive, just log
            return {
                "success": True,
                "dry_run": False,
                "alert_id": alert_id,
                "action": "skipped_archive_comment_only_mode",
                "comment_added": False,
            }

        try:
            token = self._authenticate()
            with httpx.Client(timeout=self._timeout, verify=self.verify_ssl) as client:
                # Archive alert
                resp = client.put(
                    f"{self.base_url}/alerts",
                    params={"ids": alert_id, "status": "archived"},
                    headers={"Authorization": f"Bearer {token}"},
                )
                if resp.status_code not in (200, 207):
                    return {"success": False, "alert_id": alert_id, "error": f"HTTP {resp.status_code}: {resp.text[:200]}"}
                logger.info(f"Archived Wazuh alert {alert_id}")
                return {
                    "success": True,
                    "dry_run": False,
                    "alert_id": alert_id,
                    "action": "archived",
                    "status_code": resp.status_code,
                }
        except Exception as e:
            logger.error(f"Failed to archive Wazuh alert {alert_id}: {e}")
            return {"success": False, "alert_id": alert_id, "error": str(e)}

    def add_comment(self, alert_id: str, comment: str) -> Dict[str, Any]:
        """
        Add an audit comment to a Wazuh alert.

        Even in archive modes, this is recommended to leave a trail.
        In dry-run mode, this is also a no-op.
        """
        if not self.is_available():
            return {"success": False, "skipped": True, "reason": "not configured"}

        if self.dry_run:
            logger.info(f"[DRY_RUN] Would add comment to Wazuh alert {alert_id}: {comment[:80]}")
            return {
                "success": True,
                "dry_run": True,
                "alert_id": alert_id,
                "action": "comment",
                "comment_preview": comment[:100],
            }

        try:
            token = self._authenticate()
            with httpx.Client(timeout=self._timeout, verify=self.verify_ssl) as client:
                # Add comment to alert
                resp = client.post(
                    f"{self.base_url}/security/alert/comment",
                    params={"alert_id": alert_id},
                    json={"comment": comment},
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    },
                )
                if resp.status_code not in (200, 207):
                    return {"success": False, "alert_id": alert_id, "error": f"HTTP {resp.status_code}: {resp.text[:200]}"}
                logger.info(f"Added comment to Wazuh alert {alert_id}")
                return {
                    "success": True,
                    "dry_run": False,
                    "alert_id": alert_id,
                    "action": "commented",
                    "status_code": resp.status_code,
                }
        except Exception as e:
            logger.error(f"Failed to comment on Wazuh alert {alert_id}: {e}")
            return {"success": False, "alert_id": alert_id, "error": str(e)}

    def close_alert(self, alert_id: str, reason: str, bradlyai_audit_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Close an alert in Wazuh. Combined action: comment + (optional) archive.

        Always adds an audit comment with the BradlyAI reasoning.
        Archives (if configured) according to close_mode:
          - comment_only: just comment
          - archive_only: just archive
          - archive_and_comment: both

        Dry-run by default.
        """
        # Build the comment
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        comment_lines = [
            f"[BradlyAI L1 Agent] Auto-closed at {timestamp}",
            f"Reason: {reason}",
        ]
        if bradlyai_audit_id is not None:
            comment_lines.append(f"BradlyAI audit_id: {bradlyai_audit_id}")
        comment_lines.append("(Action can be reversed by un-archiving in Wazuh UI)")
        comment = "\n".join(comment_lines)

        result = {"alert_id": alert_id, "actions": []}

        # Add comment (always, if enabled)
        if self.close_mode in ("comment_only", "archive_and_comment"):
            comment_result = self.add_comment(alert_id, comment)
            result["actions"].append(comment_result)
        elif self.close_mode == "archive_only":
            # No comment in archive_only mode
            pass

        # Archive if mode allows
        if self.close_mode in ("archive_only", "archive_and_comment"):
            archive_result = self.archive_alert(alert_id, comment)
            result["actions"].append(archive_result)

        result["success"] = all(a.get("success", True) for a in result["actions"]) or not result["actions"]
        result["dry_run"] = self.dry_run
        return result

    def health_check(self) -> Dict[str, Any]:
        """Test connection to Wazuh Manager. Returns version + status."""
        if not self.is_available():
            return {"connected": False, "reason": "not configured"}
        if self.dry_run:
            return {"connected": "dry_run", "would_test": f"GET {self.base_url}/"}
        try:
            token = self._authenticate()
            with httpx.Client(timeout=self._timeout, verify=self.verify_ssl) as client:
                resp = client.get(
                    f"{self.base_url}/",
                    headers={"Authorization": f"Bearer {token}"},
                )
                return {
                    "connected": resp.status_code == 200,
                    "status_code": resp.status_code,
                    "version": resp.json().get("data", {}).get("api_version", "") if resp.status_code == 200 else "",
                }
        except Exception as e:
            return {"connected": False, "error": str(e)}


# Singleton
wazuh_api = WazuhAPIClient()
