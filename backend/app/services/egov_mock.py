import json
import os
from typing import Optional

DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")

class EGovMock:
    def __init__(self):
        self.mock_enabled = os.getenv("EGOV_MOCK", "true").lower() == "true"
        self._citizens = []
        if self.mock_enabled:
            _path = os.path.join(DATA_DIR, "citizens.json")
            if os.path.exists(_path):
                with open(_path, "r", encoding="utf-8") as f:
                    self._citizens = json.load(f)

    def get_citizen_by_iin(self, iin: str) -> Optional[dict]:
        if not self.mock_enabled:
            raise Exception("Mock disabled. Actual eGov integration required.")
        for citizen in self._citizens:
            if citizen.get("iin") == iin:
                return citizen
        return None

egov_mock = EGovMock()
