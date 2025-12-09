from __future__ import annotations

from typing import Dict, List

from flask import current_app
from sqlalchemy import or_

from integrations import CatalogClientError, build_external_catalog_client
from models import Book


def search_books(query: str) -> Dict[str, List]:
    """Return local titles and, if configured, external suggestions."""
    books_query = Book.query
    if query:
        like = f"%{query}%"
        books_query = books_query.filter(or_(Book.title.ilike(like), Book.author.ilike(like)))
    local_books = books_query.order_by(Book.title).all()

    external_books: List[dict] = []
    base_url = current_app.config.get("EXTERNAL_API_BASE_URL", "")
    token = current_app.config.get("EXTERNAL_API_TOKEN", "")
    if base_url:
        client = build_external_catalog_client(base_url, token)
        if client.enabled:
            try:
                external_books = _normalize_external_results(client.search(query))
            except CatalogClientError as exc:
                current_app.logger.warning("External catalog lookup failed: %s", exc)

    return {"local": local_books, "external": external_books}


def _normalize_external_results(payload: List[dict]) -> List[dict]:
    normalized: List[dict] = []
    for entry in payload or []:
        title = entry.get("title") or entry.get("name") or "Untitled"
        author = entry.get("author") or entry.get("authors") or entry.get("creator") or "Unknown"
        normalized.append(
            {
                "title": title,
                "author": author,
                "source_url": entry.get("url") or entry.get("link"),
            }
        )
    return normalized
