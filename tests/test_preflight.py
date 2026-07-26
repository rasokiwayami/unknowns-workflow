import json
import unittest

from unknowns_harness.preflight import check_capabilities


class CapabilityPreflightTests(unittest.TestCase):
    def test_non_object_manifest_is_rejected(self) -> None:
        result = check_capabilities(
            ["ledger"],
            required=("ledger",),
        )

        self.assertFalse(result.ready)
        self.assertEqual(result.rejections[0].code, "invalid_manifest")
        self.assertEqual(result.rejections[0].capability, "manifest")

    def test_all_required_components_are_ready(self) -> None:
        result = check_capabilities(
            {"capabilities": {"ledger": True, "implementation_notes": True}},
            required=("ledger", "implementation_notes"),
        )

        self.assertTrue(result.ready)
        self.assertEqual(result.rejections, ())

    def test_missing_component_has_typed_rejection_and_local_remedy(self) -> None:
        result = check_capabilities(
            {"capabilities": {"ledger": True}},
            required=("ledger", "implementation_notes"),
        )

        self.assertFalse(result.ready)
        rejection = result.rejections[0]
        self.assertEqual(rejection.code, "missing_capability")
        self.assertEqual(rejection.capability, "implementation_notes")
        self.assertIn("capabilities.implementation_notes", rejection.remedy)

    def test_false_component_is_missing_instead_of_silent_zero(self) -> None:
        result = check_capabilities(
            {"capabilities": {"ledger": False}},
            required=("ledger",),
        )

        self.assertFalse(result.ready)
        self.assertEqual(result.rejections[0].capability, "ledger")

    def test_type_confused_capabilities_object_is_rejected(self) -> None:
        result = check_capabilities(
            {"capabilities": ["ledger"]},
            required=("ledger",),
        )

        self.assertFalse(result.ready)
        self.assertEqual(result.rejections[0].code, "invalid_manifest")
        self.assertEqual(result.rejections[0].capability, "manifest.capabilities")

    def test_type_confused_capability_value_is_rejected(self) -> None:
        result = check_capabilities(
            {"capabilities": {"ledger": "yes"}},
            required=("ledger",),
        )

        self.assertFalse(result.ready)
        self.assertEqual(result.rejections[0].code, "invalid_manifest")
        self.assertEqual(result.rejections[0].capability, "ledger")

    def test_json_output_is_deterministic(self) -> None:
        manifest = {"capabilities": {"zeta": False, "alpha": False}}

        first = check_capabilities(
            manifest, required=("zeta", "alpha")
        ).to_json()
        second = check_capabilities(
            manifest, required=("alpha", "zeta")
        ).to_json()

        self.assertEqual(first, second)
        self.assertEqual(json.loads(first)["summary"], {"ready": 0, "required": 2})


if __name__ == "__main__":
    unittest.main()
