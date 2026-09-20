"""Tests for Cassandra visual observations."""

from __future__ import annotations

import unittest

from cassandra.observation.vision import (
    VisualCounter,
    VisualObservation,
)


class VisualCounterTests(unittest.TestCase):
    """Verify visually observed counters."""

    def test_counter_can_have_unknown_identity(self) -> None:
        counter = VisualCounter(
            value=176,
        )

        self.assertEqual(counter.value, 176)
        self.assertIsNone(counter.identity)

    def test_counter_can_have_known_identity(self) -> None:
        counter = VisualCounter(
            value=34,
            identity="wood",
        )

        self.assertEqual(counter.identity, "wood")


class VisualObservationTests(unittest.TestCase):
    """Verify structured visual observations."""

    def test_observation_stores_visible_state(self) -> None:
        observation = VisualObservation(
            screen_state="main_menu",
            visible_text=[
                "Start",
                "Load",
                "Save",
            ],
            counters=[
                VisualCounter(value=176),
                VisualCounter(value=34),
            ],
            visible_elements=[
                "menu",
                "farm preview",
            ],
            uncertainties=[
                "Resource identities are unknown.",
            ],
        )

        self.assertEqual(
            observation.screen_state,
            "main_menu",
        )
        self.assertEqual(
            observation.visible_text,
            ["Start", "Load", "Save"],
        )
        self.assertEqual(
            len(observation.counters),
            2,
        )
        self.assertEqual(
            observation.uncertainties,
            ["Resource identities are unknown."],
        )

    def test_observation_defaults_to_empty_collections(self) -> None:
        observation = VisualObservation()

        self.assertIsNone(observation.screen_state)
        self.assertEqual(observation.visible_text, [])
        self.assertEqual(observation.counters, [])
        self.assertEqual(observation.visible_elements, [])
        self.assertEqual(observation.uncertainties, [])
        self.assertEqual(observation.metadata, {})

    def test_observation_serializes_to_dictionary(self) -> None:
        observation = VisualObservation(
            screen_state="main_menu",
            visible_text=["Start", "Load"],
            counters=[
                VisualCounter(
                    value=176,
                    identity=None,
                ),
            ],
            uncertainties=[
                "Resource identity unknown.",
            ],
        )

        result = observation.to_dict()

        self.assertEqual(
            result["screen_state"],
            "main_menu",
        )
        self.assertEqual(
            result["visible_text"],
            ["Start", "Load"],
        )
        self.assertEqual(
            result["counters"],
            [
                {
                    "value": 176,
                    "identity": None,
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()