"""Tests for Price and Crop API endpoints."""

from datetime import date, timedelta
from decimal import Decimal

from app.models.crop import Crop
from app.models.market import Market
from app.models.market_price import MarketPrice


def test_prices_and_crops_api(client, db):
    # Setup test Crop and Market
    crop = db.query(Crop).filter(Crop.name == "turmeric").first()
    if not crop:
        crop = Crop(name="turmeric", tamil_name="மஞ்சள்", unit="kg", category="spice")
        db.add(crop)
        db.commit()
        db.refresh(crop)

    market = db.query(Market).filter(Market.name == "Erode Test Mandi").first()
    if not market:
        market = Market(
            name="Erode Test Mandi", district="Erode", state="Tamil Nadu", market_type="mandi"
        )
        db.add(market)
        db.commit()
        db.refresh(market)

    # Insert 3 days of price records
    today = date.today()
    for i in range(3):
        p_date = today - timedelta(days=i)
        existing = (
            db.query(MarketPrice)
            .filter(
                MarketPrice.crop_id == crop.id,
                MarketPrice.market_id == market.id,
                MarketPrice.price_date == p_date,
            )
            .first()
        )
        if not existing:
            mp = MarketPrice(
                crop_id=crop.id,
                market_id=market.id,
                district="Erode",
                min_price=Decimal("140.00"),
                max_price=Decimal("160.00"),
                modal_price=Decimal(str(150.00 + (i * 2))),
                price_date=p_date,
                source="ceda",
            )
            db.add(mp)
    db.commit()

    # 1. Test /api/crops
    crop_res = client.get("/api/crops/")
    assert crop_res.status_code == 200
    crops_data = crop_res.json()["crops"]
    assert any(c["name"] == "turmeric" for c in crops_data)

    # 2. Test /api/prices/latest
    latest_res = client.get("/api/prices/latest?district=Erode")
    assert latest_res.status_code == 200
    prices = latest_res.json()["prices"]
    assert len(prices) >= 1
    assert any(p["crop_name"] == "turmeric" for p in prices)

    # 3. Test /api/prices/history
    history_res = client.get(f"/api/prices/history?crop_id={crop.id}&market_id={market.id}&days=30")
    assert history_res.status_code == 200
    history_data = history_res.json()
    assert history_data["period_days"] == 30
    assert len(history_data["history"]) >= 3

    # 4. Test /api/prices/trend
    trend_res = client.get(f"/api/prices/trend?crop_id={crop.id}&market_id={market.id}")
    assert trend_res.status_code == 200
    trend_data = trend_res.json()
    assert "trend" in trend_data

    # 5. Test /api/prices/anomalies
    anomalies_res = client.get(
        f"/api/prices/anomalies?crop_id={crop.id}&market_id={market.id}&window=30"
    )
    assert anomalies_res.status_code == 200
    assert "anomalies" in anomalies_res.json()
