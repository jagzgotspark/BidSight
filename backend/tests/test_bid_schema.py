import pytest
from pydantic import ValidationError

from app.schemas.bid import BidUpdate


def test_bid_update_accepts_match_score() -> None:
    updated = BidUpdate(stage="won", notes="Follow-up sent", match_score=92.5)

    assert updated.stage == "won"
    assert updated.notes == "Follow-up sent"
    assert updated.match_score == 92.5


def test_bid_update_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        BidUpdate(stage="new", unexpected="value")
