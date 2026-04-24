"""
OpenFDA Drug Lookup Service — Query FDA's public drug database.

Provides async HTTP client for querying the OpenFDA API:
- Drug NDC (National Drug Code) lookup
- Drug label/packaging information
- Active ingredient identification
- Side effects and contraindications
"""

import logging
from typing import Optional

import httpx

from m5_features.config import settings

logger = logging.getLogger(__name__)


class OpenFDAService:
    """
    Async client for the OpenFDA Drug API.

    Queries the free, no-key-required OpenFDA endpoints to retrieve
    official FDA drug data including active ingredients, dosage forms,
    manufacturer info, and safety warnings.
    """

    def __init__(self):
        """Initialize with default timeout and base URL."""
        self.base_url = settings.OPENFDA_BASE_URL
        self.timeout = httpx.Timeout(10.0, connect=5.0)

    async def search_by_name(
        self,
        drug_name: str,
        limit: int = 3,
    ) -> Optional[dict]:
        """
        Search for a drug by name using the OpenFDA label endpoint.

        Args:
            drug_name: Drug name to search for (generic or brand)
            limit: Maximum number of results to return

        Returns:
            API response dict with drug information, or None on failure
        """
        search_query = f'openfda.brand_name:"{drug_name}"+openfda.generic_name:"{drug_name}"'
        url = f"{settings.OPENFDA_LABEL_ENDPOINT}"
        params = {
            "search": search_query,
            "limit": limit,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    if results:
                        logger.info(
                            f"OpenFDA found {len(results)} results for '{drug_name}'"
                        )
                        return self._parse_label_result(results[0])
                    logger.info(f"No OpenFDA results for '{drug_name}'")
                    return None

                elif response.status_code == 404:
                    logger.info(f"Drug '{drug_name}' not found in OpenFDA")
                    return None
                else:
                    logger.warning(
                        f"OpenFDA API returned status {response.status_code}"
                    )
                    return None

        except httpx.TimeoutException:
            logger.error(f"OpenFDA request timed out for '{drug_name}'")
            return None
        except Exception as e:
            logger.error(f"OpenFDA request failed: {e}")
            return None

    async def search_by_ndc(self, ndc_code: str) -> Optional[dict]:
        """
        Search for a drug by NDC (National Drug Code).

        Args:
            ndc_code: NDC code in format XXXXX-XXXX-XX

        Returns:
            Drug information dict, or None if not found
        """
        url = settings.OPENFDA_NDC_ENDPOINT
        params = {
            "search": f'product_ndc:"{ndc_code}"',
            "limit": 1,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    if results:
                        return self._parse_ndc_result(results[0])
                    return None
                return None

        except Exception as e:
            logger.error(f"OpenFDA NDC lookup failed: {e}")
            return None

    def _parse_label_result(self, result: dict) -> dict:
        """
        Parse a raw OpenFDA label API result into a clean dict.

        Extracts the most relevant fields for medicine identification
        and safety information display.
        """
        openfda = result.get("openfda", {})

        return {
            "source": "openfda",
            "brand_name": self._first(openfda.get("brand_name", [])),
            "generic_name": self._first(openfda.get("generic_name", [])),
            "manufacturer": self._first(openfda.get("manufacturer_name", [])),
            "product_type": self._first(openfda.get("product_type", [])),
            "route": self._first(openfda.get("route", [])),
            "substance_name": self._first(openfda.get("substance_name", [])),
            "active_ingredients": openfda.get("substance_name", []),
            "dosage_form": self._first(openfda.get("dosage_form", [])),
            "indications": self._truncate(
                self._first(result.get("indications_and_usage", []))
            ),
            "warnings": self._truncate(
                self._first(result.get("warnings", []))
            ),
            "contraindications": self._truncate(
                self._first(result.get("contraindications", []))
            ),
            "adverse_reactions": self._truncate(
                self._first(result.get("adverse_reactions", []))
            ),
            "dosage_and_administration": self._truncate(
                self._first(result.get("dosage_and_administration", []))
            ),
        }

    def _parse_ndc_result(self, result: dict) -> dict:
        """Parse a raw OpenFDA NDC API result."""
        return {
            "source": "openfda_ndc",
            "product_ndc": result.get("product_ndc", ""),
            "brand_name": result.get("brand_name", ""),
            "generic_name": result.get("generic_name", ""),
            "dosage_form": result.get("dosage_form", ""),
            "route": self._first(result.get("route", [])),
            "manufacturer": result.get("labeler_name", ""),
            "active_ingredients": [
                {
                    "name": ing.get("name", ""),
                    "strength": ing.get("strength", ""),
                }
                for ing in result.get("active_ingredients", [])
            ],
            "packaging": [
                pkg.get("description", "")
                for pkg in result.get("packaging", [])
            ],
        }

    @staticmethod
    def _first(lst: list) -> Optional[str]:
        """Get the first element of a list, or None."""
        return lst[0] if lst else None

    @staticmethod
    def _truncate(text: Optional[str], max_len: int = 500) -> Optional[str]:
        """Truncate text to max length with ellipsis."""
        if text and len(text) > max_len:
            return text[:max_len] + "..."
        return text


# Singleton instance
openfda_service = OpenFDAService()
