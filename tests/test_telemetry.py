import json
import unittest

from unknowns_harness.telemetry import telemetry_event


class TelemetryTests(unittest.TestCase):
    def test_event_json_is_stable_and_contains_no_implicit_timestamp(self) -> None:
        event = telemetry_event(
            "capability_preflight",
            outcome="rejected",
            details={"missing": ["implementation_notes"]},
        )

        self.assertEqual(
            event.to_json(),
            json.dumps(
                {
                    "details": {"missing": ["implementation_notes"]},
                    "event": "capability_preflight",
                    "outcome": "rejected",
                },
                sort_keys=True,
                separators=(",", ":"),
            ),
        )


if __name__ == "__main__":
    unittest.main()
