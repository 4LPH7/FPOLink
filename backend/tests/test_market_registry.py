"""Tests for market registry and market alias resolution."""

import uuid

from app.models.geography import District, State
from app.models.market import Market
from app.models.market_alias import MarketAlias
from app.services.market_resolver import resolve_market


def test_market_alias_resolution(db):
    """Verify raw mandi strings and codes resolve to canonical Market entities."""
    state = State(name=f"TN-Mkt-{uuid.uuid4().hex[:4]}", code=f"M{uuid.uuid4().hex[:2].upper()}")
    db.add(state)
    db.commit()

    district = District(state_id=state.id, name="Erode", code=f"EDM-{uuid.uuid4().hex[:4]}")
    db.add(district)
    db.commit()

    mkt_name = f"Perundurai Test Market {uuid.uuid4().hex[:4]}"
    alias1_name = f"Perundurai Mandi Test {uuid.uuid4().hex[:4]}"
    alias2_name = f"AGMARKNET_PERUNDURAI_TEST_{uuid.uuid4().hex[:4]}"

    market = Market(
        name=mkt_name,
        code=f"MKT-PRD-{uuid.uuid4().hex[:4]}",
        district="Erode",
        district_id=district.id,
        market_type="regulated_market",
        is_active=True,
    )
    db.add(market)
    db.commit()

    alias1 = MarketAlias(market_id=market.id, alias=alias1_name, source="general")
    alias2 = MarketAlias(market_id=market.id, alias=alias2_name, source="agmarknet")
    db.add_all([alias1, alias2])
    db.commit()

    # 1. Exact code
    assert resolve_market(market.code, db=db).id == market.id

    # 2. Exact name
    assert resolve_market(mkt_name, db=db).id == market.id

    # 3. Aliases
    assert resolve_market(alias1_name, db=db).id == market.id
    assert resolve_market(alias1_name.lower(), db=db).id == market.id
    assert resolve_market(alias2_name, db=db).id == market.id

    # 4. Unknown market
    assert resolve_market("NonExistent_Unknown_Market", db=db) is None


def test_api_v1_markets_resolve(client, db):
    """Test GET and POST /api/v1/markets endpoints."""
    market = Market(
        name=f"Erode Turmeric Yard {uuid.uuid4().hex[:4]}",
        code=f"MKT-ETY-{uuid.uuid4().hex[:4]}",
        district="Erode",
        market_type="regulated_market",
        is_active=True,
    )
    db.add(market)
    db.commit()

    alias = MarketAlias(market_id=market.id, alias=f"Erode Semi Mandi {uuid.uuid4().hex[:4]}")
    db.add(alias)
    db.commit()

    # 1. GET /api/v1/markets
    r = client.get("/api/v1/markets")
    assert r.status_code == 200
    markets = r.json()
    assert any(m["id"] == str(market.id) for m in markets)

    # 2. POST /api/v1/markets/resolve
    r2 = client.post("/api/v1/markets/resolve", json={"text": alias.alias})
    assert r2.status_code == 200
    data = r2.json()
    assert data["matched"] is True
    assert data["market"]["id"] == str(market.id)
