"""DEPRECATED — the v1 `Count`/`Duplicate` model pair was removed in the v2
schema migration. Duplicate detection is now unnecessary by design: the DB
enforces one row per (session, product, shelf_section, user) via unique
constraints on `first_counts`/`second_counts`, and cross-counter reconciliation
is handled by `AdjustmentService` (see app/services/adjustment_service.py),
which wraps `fn_detect_count_discrepancy()` / `fn_generate_adjustments()`.
This module is kept only so any stale imports fail loudly instead of via a
missing-module error, and is not wired into any router."""
from sqlalchemy.orm import Session
from typing import Optional, List


class DuplicateService:  # pragma: no cover - retained for backward-compat import safety only
    def __init__(self, db: Session):
        self.db = db
        raise NotImplementedError(
            "DuplicateService was removed in the v2 schema migration. "
            "Use AdjustmentService (app.services.adjustment_service) instead."
        )
