"""
Fast batch seeder for Render production DB.
Imports data from seed_statewide_foundation.py but does bulk inserts
with single transactions rather than per-row commits.
Run with: python backend/scripts/seed_render_fast.py
"""

# ruff: noqa: E402
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Import all data constants from the foundation script
from app.models.crop import Crop
from app.models.crop_alias import CropAlias
from app.models.data_quality import DataSource
from app.models.geography import District, State, Taluk
from app.models.market import Market
from app.models.market_alias import MarketAlias
from app.models.variety import Variety
from app.models.variety_alias import VarietyAlias
from scripts.seed_statewide_foundation import (
    DATA_SOURCES,
    STATEWIDE_MARKETS,
    TALUKS_BY_DISTRICT,
    TIER_A_CROPS,
    TN_DISTRICTS,
)


def run():
    db = SessionLocal()
    print("=" * 60)
    print("FPOLink — Fast Batch Seeder for Render DB")
    print("=" * 60)

    try:
        # ── 1. State ──────────────────────────────────────────────
        state = db.query(State).filter(State.code == "TN").first()
        if not state:
            state = State(name="Tamil Nadu", code="TN")
            db.add(state)
            db.flush()
        print(f"✓ State: {state.name}")

        # ── 2. Districts (batch) ───────────────────────────────────
        existing_districts = {d.name: d for d in db.query(District).all()}
        district_map = {}
        new_districts = []
        for name, code in TN_DISTRICTS:
            if name in existing_districts:
                d = existing_districts[name]
                if not d.code:
                    d.code = code
                if not d.state_id:
                    d.state_id = state.id
                district_map[name] = d
            else:
                d = District(name=name, code=code, state_id=state.id)
                db.add(d)
                new_districts.append(d)
                district_map[name] = d
        db.flush()
        for d in district_map.values():
            db.refresh(d)
        print(f"✓ Districts: {len(TN_DISTRICTS)} total ({len(new_districts)} new)")

        # ── 3. Taluks (batch) ──────────────────────────────────────
        existing_taluks = set((t.name, str(t.district_id)) for t in db.query(Taluk).all())
        taluks_created = 0
        for dist_name, taluks in TALUKS_BY_DISTRICT.items():
            dist_obj = district_map.get(dist_name)
            if not dist_obj:
                continue
            for t_name, _ in taluks:
                key = (t_name, str(dist_obj.id))
                if key not in existing_taluks:
                    db.add(Taluk(name=t_name, district_id=dist_obj.id))
                    existing_taluks.add(key)
                    taluks_created += 1
        db.flush()
        print(f"✓ Taluks: {taluks_created} newly created")

        # ── 4. Crops & varieties (batch) ───────────────────────────
        existing_crops = {c.name: c for c in db.query(Crop).all()}
        existing_aliases = set((str(a.crop_id), a.alias) for a in db.query(CropAlias).all())
        crops_created = 0
        for cdata in TIER_A_CROPS:
            if cdata["name"] in existing_crops:
                crop = existing_crops[cdata["name"]]
                crop.canonical_name = cdata["canonical_name"]
                crop.tamil_name = cdata["tamil_name"]
                crop.unit = cdata["unit"]
                crop.is_active = True
            else:
                crop = Crop(
                    name=cdata["name"],
                    canonical_name=cdata["canonical_name"],
                    scientific_name=cdata["scientific_name"],
                    category=cdata["category"],
                    tamil_name=cdata["tamil_name"],
                    unit=cdata["unit"],
                    is_active=True,
                )
                db.add(crop)
                crops_created += 1
                existing_crops[cdata["name"]] = crop
        db.flush()
        for crop in existing_crops.values():
            db.refresh(crop)

        # Aliases
        aliases_created = 0
        for cdata in TIER_A_CROPS:
            crop = existing_crops[cdata["name"]]
            for alias_str in cdata["aliases"]:
                a = alias_str.strip().lower()
                key = (str(crop.id), a)
                if key not in existing_aliases:
                    db.add(CropAlias(crop_id=crop.id, alias=a, source="canonical"))
                    existing_aliases.add(key)
                    aliases_created += 1
        db.flush()

        # Varieties
        variety_map = {}
        existing_varieties_objs = {(str(v.crop_id), v.name): v for v in db.query(Variety).all()}
        varieties_created = 0
        for cdata in TIER_A_CROPS:
            crop = existing_crops[cdata["name"]]
            for v_name, v_aliases in cdata.get("varieties", []):
                key = (str(crop.id), v_name)
                if key in existing_varieties_objs:
                    var_obj = existing_varieties_objs[key]
                else:
                    var_obj = Variety(crop_id=crop.id, name=v_name, canonical_name=v_name)
                    db.add(var_obj)
                    varieties_created += 1
                    existing_varieties_objs[key] = var_obj
                variety_map[key] = var_obj
        db.flush()

        # Variety aliases
        existing_var_aliases = set(
            (str(va.variety_id), va.alias) for va in db.query(VarietyAlias).all()
        )
        for cdata in TIER_A_CROPS:
            crop = existing_crops[cdata["name"]]
            for v_name, v_aliases in cdata.get("varieties", []):
                key = (str(crop.id), v_name)
                var_obj = variety_map.get(key)
                if not var_obj:
                    continue
                db.refresh(var_obj)
                for va_str in v_aliases:
                    va = va_str.strip().lower()
                    vkey = (str(var_obj.id), va)
                    if vkey not in existing_var_aliases:
                        db.add(VarietyAlias(variety_id=var_obj.id, alias=va, source="canonical"))
                        existing_var_aliases.add(vkey)
        db.flush()

        print(
            f"✓ Crops: {len(TIER_A_CROPS)} ({crops_created} new), "
            f"{aliases_created} aliases, {varieties_created} varieties"
        )

        # ── 5. Markets (batch) ──────────────────────────────────────
        existing_markets = {m.name: m for m in db.query(Market).all()}
        markets_created = 0
        for mdata in STATEWIDE_MARKETS:
            dist_obj = district_map.get(mdata["district"])
            dist_id = dist_obj.id if dist_obj else None
            canonical = mdata.get("canonical_name", mdata["name"].lower())
            if mdata["name"] in existing_markets:
                m = existing_markets[mdata["name"]]
                m.canonical_name = canonical
                m.district_id = dist_id
                m.latitude = mdata["lat"]
                m.longitude = mdata["lon"]
                m.is_active = True
            else:
                m = Market(
                    name=mdata["name"],
                    canonical_name=canonical,
                    tamil_name=mdata.get("tamil_name"),
                    code=mdata["code"],
                    district=mdata["district"],
                    district_id=dist_id,
                    state="Tamil Nadu",
                    market_type=mdata.get("market_type", "regulated_market"),
                    is_regulated=True,
                    e_nam=mdata.get("e_nam", False),
                    operating_status="active",
                    latitude=mdata["lat"],
                    longitude=mdata["lon"],
                    is_active=True,
                )
                db.add(m)
                markets_created += 1
                existing_markets[mdata["name"]] = m
        db.flush()
        for m in existing_markets.values():
            db.refresh(m)

        # Market aliases (batch)
        existing_maliases = set((str(ma.market_id), ma.alias) for ma in db.query(MarketAlias).all())
        maliases_created = 0
        for mdata in STATEWIDE_MARKETS:
            m = existing_markets.get(mdata["name"])
            if not m:
                continue
            for ma_str in mdata.get("aliases", []):
                a = ma_str.strip().lower()
                key = (str(m.id), a)
                if key not in existing_maliases:
                    db.add(MarketAlias(market_id=m.id, alias=a, source="canonical"))
                    existing_maliases.add(key)
                    maliases_created += 1
        db.flush()
        print(
            f"✓ Markets: {len(STATEWIDE_MARKETS)} ({markets_created} new), "
            f"{maliases_created} aliases"
        )

        # ── 6. Data Sources ─────────────────────────────────────────
        existing_ds = {d.code: d for d in db.query(DataSource).all()}
        ds_created = 0
        for ds in DATA_SOURCES:
            if ds["code"] not in existing_ds:
                db.add(
                    DataSource(
                        name=ds["name"], code=ds["code"], priority=ds["priority"], is_active=True
                    )
                )
                ds_created += 1
        db.flush()
        print(f"✓ Data Sources: {len(DATA_SOURCES)} ({ds_created} new)")

        # ── 7. Single commit for everything ─────────────────────────
        db.commit()
        print("\n✅ ALL DONE — committed in one transaction batch")

    except Exception as e:
        db.rollback()
        print(f"\n❌ SEED FAILED: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    run()
