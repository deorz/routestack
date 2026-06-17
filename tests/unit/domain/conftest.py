import sys
from pathlib import Path
from uuid import uuid4

import pytest

from domain.subscriptions.subscription import Subscription

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture
def subscription() -> Subscription:
    return Subscription(
        client_id=uuid4(),
        public_id="public-id-test",
        access_token_hash="hash-abc",
        name="Starter",
    )
