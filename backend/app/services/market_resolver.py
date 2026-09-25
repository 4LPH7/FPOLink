"""Market canonicalization resolver service."""

import re
from typing import Optional
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.market import Market
from app.models.market_alias import MarketAlias
from app.models.source_mapping import MarketSourceMapping


def _clean_str(text: str) -> str:
    """Normalize input string: strip, lowercase, collapse whitespace."""
    if not text:
        return ""
    text = text.strip().lower()
    return re.sub(r"\s+", " ", text)


def resolve_market(
    name_or_alias: str,
    district_id: Optional[UUID] = None,
    db: Session = None,
    source_code: Optional[str] = None,
    external_code: Optional[str] = None,
) -> Optional[Market]:
    """Resolve any raw mandi string or code to a canonical Market entity.

    Precedence:
    0. Exact external ID or source-code mapping in MarketSourceMapping
    1. Exact match on Market.code
    2. Exact match on Market.canonical_name or Market.name (filtered by district_id if provided)
    3. Case-insensitive lookup in MarketAlias
    4. Substring / fuzzy match in Market.name or MarketAlias
    """
    clean = _clean_str(name_or_alias)

    # 0. Deterministic external source mapping lookup
    if db is not None and source_code:
        s_code = source_code.strip().lower()
        if external_code:
            mapping = (
                db.query(MarketSourceMapping)
                .filter(
                    MarketSourceMapping.source_code == s_code,
                    func.lower(MarketSourceMapping.external_code) == external_code.strip().lower(),
                )
                .first()
            )
            if mapping and mapping.market and mapping.market.is_active:
                if not district_id or mapping.market.district_id == district_id:
                    return mapping.market

        if clean:
            mapping = (
                db.query(MarketSourceMapping)
                .filter(
                    MarketSourceMapping.source_code == s_code,
                    (func.lower(MarketSourceMapping.external_name) == clean)
                    | (func.lower(MarketSourceMapping.external_code) == clean),
                )
                .first()
            )
            if mapping and mapping.market and mapping.market.is_active:
                if not district_id or mapping.market.district_id == district_id:
                    return mapping.market

    if not clean or db is None:
        return None

    # 1. Match on code
    market = (
        db.query(Market)
        .filter(
            func.lower(Market.code) == clean,
            Market.is_active.is_(True),
        )
        .first()
    )
    if market:
        return market

    # 2. Match on canonical_name or name
    query = db.query(Market).filter(
        (func.lower(Market.name) == clean) | (func.lower(Market.canonical_name) == clean),
        Market.is_active.is_(True),
    )
    if district_id:
        scoped = query.filter(Market.district_id == district_id).first()
        if scoped:
            return scoped
    market = query.first()
    if market:
        return market

    # 3. Match in MarketAlias
    alias_query = (
        db.query(MarketAlias)
        .join(Market)
        .filter(
            func.lower(MarketAlias.alias) == clean,
            Market.is_active.is_(True),
        )
    )
    if district_id:
        scoped_alias = alias_query.filter(Market.district_id == district_id).first()
        if scoped_alias and scoped_alias.market:
            return scoped_alias.market
    alias = alias_query.first()
    if alias and alias.market:
        return alias.market

    # 4. Partial substring match in Market.name
    partial = db.query(Market).filter(
        func.lower(Market.name).like(f"%{clean}%"),
        Market.is_active.is_(True),
    )
    if district_id:
        scoped_p = partial.filter(Market.district_id == district_id).first()
        if scoped_p:
            return scoped_p
    return partial.first()
