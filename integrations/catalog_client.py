from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests


class CatalogClientError(RuntimeError):
    """Raised when the external catalog cannot be reached."""


@dataclass
class ExternalCatalogClient:
    base_url: str
    token: Optional[str] = None
    session: Optional[requests.Session] = None

    def __post_init__(self) -> None:
        self.base_url = (self.base_url or "").rstrip("/")
        self.session = self.session or requests.Session()

    @property
    def enabled(self) -> bool:
        return bool(self.base_url)

    def search(self, query: str) -> List[Dict[str, Any]]:
        if not self.enabled or not query:
            return []
        try:
            response = self.session.get(
                f"{self.base_url}/search",
                params={"q": query},
                headers=self._headers(),
                timeout=5,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise CatalogClientError(str(exc)) from exc
        data = response.json()
        return data.get("results", data) if isinstance(data, dict) else data

    def _headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers


def build_external_catalog_client(base_url: str, token: Optional[str]) -> ExternalCatalogClient:
    return ExternalCatalogClient(base_url=base_url, token=token)
