"""BradlyAI GreyNoise Integration — real-time internet scanner intelligence.

GreyNoise Community API: https://api.greynoise.io/v3/community/{ip}
  - Free, no auth required
  - Returns scanner classifications for any IP
  - "noise" = mass-scanning the internet (often benign like Shodan)
  - "riot" = benign service like Google DNS or NTP
  - Perfect test source for L1 Agent's scanner detection rules

Usage:
  # Test a single IP
  curl /api/v1/l1/greynoise/check/104.248.144.124

  # Run a batch test (sends IPs through L1 Agent decision engine)
  curl -X POST /api/v1/l1/greynoise/test-batch -d '{"ips": [...]}'
"""
import logging
from typing import Optional, Dict, Any, List
import httpx
from datetime import datetime, timezone

logger = logging.getLogger("bradlyai.greynoise")


class GreyNoiseClient:
    """GreyNoise Community API client. No auth required."""

    BASE_URL = "https://api.greynoise.io/v3/community"
    TIMEOUT = 10.0

    def __init__(self):
        self.last_call: Optional[datetime] = None
        self.cache: Dict[str, Dict[str, Any]] = {}  # IP -> response
        self.cache_ttl_seconds = 3600  # 1 hour

    def query(self, ip: str) -> Optional[Dict[str, Any]]:
        """Query GreyNoise for a single IP. Returns None on error."""
        # Check cache
        if ip in self.cache:
            entry = self.cache[ip]
            if entry.get("_cached_at"):
                age = (datetime.now(timezone.utc) - entry["_cached_at"]).total_seconds()
                if age < self.cache_ttl_seconds:
                    return entry
        try:
            with httpx.Client(timeout=self.TIMEOUT) as client:
                resp = client.get(
                    f"{self.BASE_URL}/{ip}",
                    headers={"User-Agent": "BradlyAI-L1-Test/1.0"},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    data["_cached_at"] = datetime.now(timezone.utc)
                    self.cache[ip] = data
                    return data
                elif resp.status_code == 404:
                    # IP not in GreyNoise database
                    return {
                        "ip": ip,
                        "noise": False,
                        "riot": False,
                        "message": "IP not in GreyNoise database",
                        "_cached_at": datetime.now(timezone.utc),
                    }
                else:
                    logger.warning(f"GreyNoise API returned {resp.status_code} for {ip}")
                    return None
        except Exception as e:
            logger.warning(f"GreyNoise query failed for {ip}: {e}")
            return None

    def classify(self, ip: str) -> Dict[str, Any]:
        """Convert GreyNoise response to a verdict for L1 Agent.

        Returns:
            {
                "verdict": "FP" | "REAL" | "UNKNOWN",
                "confidence": 0.0 - 1.0,
                "reason": "human-readable explanation",
                "raw": <greynoise response>,
            }
        """
        response = self.query(ip)
        if not response:
            return {
                "verdict": "UNKNOWN",
                "confidence": 0.3,
                "reason": "GreyNoise lookup failed (network error)",
                "raw": None,
            }

        noise = response.get("noise", False)
        riot = response.get("riot", False)
        classification = response.get("classification", "")
        name = response.get("name", "")

        # RIOT = benign service (Google DNS, Cloudflare, etc.) → FP
        if riot:
            return {
                "verdict": "FP",
                "confidence": 0.95,
                "reason": f"RIOT (benign service): {name or 'known good service'}",
                "raw": response,
            }

        # noise=true = mass scanner, often benign (Shodan, Censys) → FP
        if noise:
            # If classified as "benign" by GreyNoise → very confident FP
            if classification == "benign":
                return {
                    "verdict": "FP",
                    "confidence": 0.95,
                    "reason": f"Known benign scanner: {name or 'internet scanner'}",
                    "raw": response,
                }
            # Otherwise it's a scanner doing reconnaissance → FP (it's just scanning, not attacking)
            return {
                "verdict": "FP",
                "confidence": 0.85,
                "reason": f"Internet scanner (reconnaissance, not active attack): {name or 'mass scanner'}",
                "raw": response,
            }

        # Not in any category → real (not seen by GreyNoise = suspicious)
        return {
            "verdict": "REAL",
            "confidence": 0.6,  # Not super confident — GreyNoise just doesn't see it
            "reason": "IP not seen scanning by GreyNoise — treat as suspicious",
            "raw": response,
        }

    def query_batch(self, ips: List[str]) -> Dict[str, Dict[str, Any]]:
        """Query multiple IPs. Returns {ip: response} dict."""
        return {ip: self.query(ip) for ip in ips}


greynoise_client = GreyNoiseClient()
