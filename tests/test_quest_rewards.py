"""Character-quest checks never hold progression and always get a useful item."""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from audit_access import load_quest_rewards

REGISTRY = json.loads((ROOT / "apworld/lookoutside/vertical_slice.json").read_text(encoding="utf-8"))
QUESTS = load_quest_rewards()(REGISTRY)
BY_NAME = {row["name"]: row for row in REGISTRY["locations"]}


class QuestRewardTests(unittest.TestCase):
    def test_slow_and_timed_character_quests_are_covered(self):
        for name in ("Roach Leadership - Papier-Maché Crown", "Roach Leadership - Official Sash",
                     "Basement Sideroom Hole - Azure Greatsword", "Leigh's Call - Martin's Ring",
                     "Benjamin - Teeth Pendant", "Joel Resolution - Door Knob",
                     "Wilhelmina Defeated - Spellsword", "Sybil Resolution - Iris Key"):
            self.assertIn(name, QUESTS)

    def test_bosses_salvage_and_plain_pickups_are_not_quests(self):
        for name in ("Boss Salvage - Tank Gun", "Rat King Defeated - Rusty Crown",
                     "Apartment 33 Planter - Spare Apartment 33 Key", "Lumpy's Room - Straitjacket"):
            self.assertIn(name, BY_NAME)
            self.assertNotIn(name, QUESTS)

    def test_missable_quest_checks_stay_filler_only(self):
        self.assertTrue(BY_NAME["Pierre - Old Mail Visit"].get("missable"))
        self.assertNotIn("Pierre - Old Mail Visit", QUESTS)
        self.assertFalse(any(BY_NAME[name].get("missable") for name in QUESTS))

    def test_enough_useful_items_and_progression_room(self):
        self.assertEqual(len(QUESTS), 43)
        count = lambda kind: sum(row["quantity"] for row in REGISTRY["items"] if row["classification"] == kind)
        # A solo seed fills every quest check with its own useful items.
        self.assertGreaterEqual(count("useful"), len(QUESTS))
        open_locations = len(REGISTRY["locations"]) - len(QUESTS) - sum(bool(row.get("missable")) for row in REGISTRY["locations"])
        self.assertGreater(open_locations, 2 * count("progression"))


if __name__ == "__main__":
    unittest.main()
