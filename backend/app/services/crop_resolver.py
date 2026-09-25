"""Crop and variety canonicalization resolver service."""

import re
from typing import Optional
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.crop import Crop
from app.models.crop_alias import CropAlias
from app.models.source_mapping import CropSourceMapping, VarietySourceMapping
from app.models.variety import Variety
from app.models.variety_alias import VarietyAlias


def _clean_str(text: str) -> str:
    """Normalize input string: strip, lowercase, collapse whitespace."""
    if not text:
        return ""
    text = text.strip().lower()
    return re.sub(r"\s+", " ", text)


def resolve_crop(
    name_or_alias: str,
    db: Session,
    source_code: Optional[str] = None,
    external_code: Optional[str] = None,
) -> Optional[Crop]:
    """Resolve any raw, regional, or provider string to a canonical Crop entity.

    Precedence:
    0. Exact external ID or source-code mapping in CropSourceMapping
    1. Exact match on Crop.canonical_name or Crop.name
    2. Exact match on Crop.tamil_name
    3. Case-insensitive lookup in CropAlias
    4. Substring / clean matching
    """
    clean = _clean_str(name_or_alias)

    # 0. Deterministic external source mapping lookup
    if source_code:
        s_code = source_code.strip().lower()
        if external_code:
            mapping = (
                db.query(CropSourceMapping)
                .filter(
                    CropSourceMapping.source_code == s_code,
                    func.lower(CropSourceMapping.external_code) == external_code.strip().lower(),
                )
                .first()
            )
            if mapping and mapping.crop and mapping.crop.is_active:
                return mapping.crop

        if clean:
            mapping = (
                db.query(CropSourceMapping)
                .filter(
                    CropSourceMapping.source_code == s_code,
                    (func.lower(CropSourceMapping.external_name) == clean)
                    | (func.lower(CropSourceMapping.external_code) == clean),
                )
                .first()
            )
            if mapping and mapping.crop and mapping.crop.is_active:
                return mapping.crop
    if not clean:
        return None

    # 1. Exact match on canonical_name or name
    crop = (
        db.query(Crop)
        .filter(
            func.lower(Crop.canonical_name) == clean,
            Crop.is_active.is_(True),
        )
        .first()
    )
    if crop:
        return crop

    crop = (
        db.query(Crop)
        .filter(
            func.lower(Crop.name) == clean,
            Crop.is_active.is_(True),
        )
        .first()
    )
    if crop:
        return crop

    # 2. Match on tamil_name
    crop = (
        db.query(Crop)
        .filter(
            Crop.tamil_name == name_or_alias.strip(),
            Crop.is_active.is_(True),
        )
        .first()
    )
    if crop:
        return crop

    # 3. Match in CropAlias
    alias = db.query(CropAlias).filter(func.lower(CropAlias.alias) == clean).first()
    if alias and alias.crop and alias.crop.is_active:
        return alias.crop

    # 4. Partial / word boundary match in CropAlias
    alias = db.query(CropAlias).filter(func.lower(CropAlias.alias).like(f"%{clean}%")).first()
    if alias and alias.crop and alias.crop.is_active:
        return alias.crop

    return None


def resolve_variety(
    crop_id: UUID,
    variety_or_alias: str,
    db: Session,
    source_code: Optional[str] = None,
    external_code: Optional[str] = None,
) -> Optional[Variety]:
    """Resolve a variety or varietal alias for a specific crop."""
    clean = _clean_str(variety_or_alias)

    # 0. Deterministic external variety source mapping lookup
    if source_code:
        s_code = source_code.strip().lower()
        if external_code:
            mapping = (
                db.query(VarietySourceMapping)
                .filter(
                    VarietySourceMapping.variety_id.in_(
                        db.query(Variety.id).filter(Variety.crop_id == crop_id)
                    ),
                    VarietySourceMapping.source_code == s_code,
                    VarietySourceMapping.external_code == external_code.strip(),
                )
                .first()
            )
            if mapping and mapping.variety:
                return mapping.variety

        if clean:
            mapping = (
                db.query(VarietySourceMapping)
                .filter(
                    VarietySourceMapping.variety_id.in_(
                        db.query(Variety.id).filter(Variety.crop_id == crop_id)
                    ),
                    VarietySourceMapping.source_code == s_code,
                    (func.lower(VarietySourceMapping.external_name) == clean)
                    | (VarietySourceMapping.external_code == clean),
                )
                .first()
            )
            if mapping and mapping.variety:
                return mapping.variety

    if not clean:
        return None

    # 1. Direct name / canonical_name on Variety
    variety = (
        db.query(Variety)
        .filter(
            Variety.crop_id == crop_id,
            (func.lower(Variety.canonical_name) == clean) | (func.lower(Variety.name) == clean),
        )
        .first()
    )
    if variety:
        return variety

    # 2. Match in VarietyAlias
    valias = (
        db.query(VarietyAlias)
        .join(Variety)
        .filter(
            Variety.crop_id == crop_id,
            func.lower(VarietyAlias.alias) == clean,
        )
        .first()
    )
    if valias:
        return valias.variety

    return None
