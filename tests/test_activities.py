"""Optional activities and companion upgrades stay separate from the audited 273-check registry."""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from audit_access import load_access

GRAPH = load_access()
REGISTRY = json.loads((ROOT / "apworld/lookoutside/vertical_slice.json").read_text(encoding="utf-8"))
ACTIVITIES = json.loads((ROOT / "apworld/lookoutside/activities.json").read_text(encoding="utf-8"))
DAILY_LIFE = json.loads((ROOT / "apworld/lookoutside/daily_life.json").read_text(encoding="utf-8"))
SUPPLIES = json.loads((ROOT / "apworld/lookoutside/supplies.json").read_text(encoding="utf-8"))
COMPANIONS = json.loads((ROOT / "apworld/lookoutside/companions.json").read_text(encoding="utf-8"))["companions"]


class ActivityTests(unittest.TestCase):
    def test_ids_and_names_never_collide_with_the_registry(self):
        locations = (REGISTRY["locations"] + ACTIVITIES["locations"] + DAILY_LIFE["locations"] +
                     [row["location"] for row in COMPANIONS])
        items = REGISTRY["items"] + [SUPPLIES["item"]] + [row["item"] for row in COMPANIONS]
        for rows in (locations, items):
            self.assertEqual(len({row["ap_id"] for row in rows}), len(rows))
            self.assertEqual(len({row["name"] for row in rows}), len(rows))
        self.assertEqual(len(REGISTRY["locations"]), 273)

    def test_each_location_brings_one_supply_cache(self):
        self.assertEqual(ACTIVITIES["items"], [{"name": SUPPLIES["item"]["name"], "quantity": len(ACTIVITIES["locations"])}])
        self.assertEqual(SUPPLIES["item"]["classification"], "filler")

    def test_supply_table_is_ordinary_consumables(self):
        ids = [row["id"] for row in SUPPLIES["table"]]
        self.assertEqual(len(set(ids)), len(ids))
        self.assertTrue(all(row["weight"] in (1, 3) for row in SUPPLIES["table"]))
        # Never a randomized registry item, so caches cannot duplicate progression.
        registry_items = {row["database_id"] for row in REGISTRY["items"] if row["kind"] == "item"}
        self.assertFalse(set(ids) & registry_items)
        plugin = (ROOT / "game_plugin/LookOutsideArchipelago.js").read_text(encoding="utf-8")
        self.assertIn(f'{SUPPLIES["item"]["ap_id"]}: Object.freeze({{"kind": "cache", "id": 1', plugin)

    def test_regions_exist_and_each_location_has_one_trigger(self):
        for row in ACTIVITIES["locations"]:
            self.assertIn(row["region"], GRAPH.regions)
            if "requires_region" in row:
                self.assertIn(row["requires_region"], GRAPH.regions)
            self.assertNotIn(row["key"], GRAPH.checks)
        self.assertEqual(sorted(row.get("meals", 0) for row in ACTIVITIES["locations"]), [0, 1, 3])

    def test_plugin_embeds_the_same_activity_ids(self):
        plugin = (ROOT / "game_plugin/LookOutsideArchipelago.js").read_text(encoding="utf-8")
        self.assertIn(f"const activityVersion = {ACTIVITIES['feature_version']};", plugin)
        for row in ACTIVITIES["locations"]:
            self.assertIn(f'"key": "{row["key"]}", "name": "{row["name"]}", "apId": {row["ap_id"]}', plugin)



class CompanionTests(unittest.TestCase):
    def test_one_join_check_and_one_useful_upgrade_per_companion(self):
        actors = [row["actor_id"] for row in COMPANIONS]
        self.assertEqual(len(set(actors)), len(actors), 17)
        # Wretch (9), Jacob (17) and Melt (18) are never recruited in this build.
        self.assertTrue({9, 17, 18}.isdisjoint(actors))
        for row in COMPANIONS:
            actor = row["actor_id"]
            self.assertEqual(row["location"]["ap_id"], 594000000 + actor)
            self.assertEqual(row["item"]["ap_id"], 540400000 + actor)
            self.assertEqual(row["item"]["classification"], "useful")
            self.assertTrue(row["effect"])
            self.assertLessEqual(set(row["effect"]), {
                "traits", "battle_state", "party_battle_state", "level_floor_below_leader", "intro_viewers",
                "rehide_chance"})
            # Only passive trait kinds; never skill seals, extra actions or equip changes.
            for code, _, value in row["effect"].get("traits", []):
                self.assertIn(code, {11, 14, 21, 22, 23, 32, 64})
                self.assertGreater(value, 0)

    def test_guide_prototypes_are_present(self):
        effects = {row["name"]: row["effect"] for row in COMPANIONS}
        self.assertEqual(effects["Sophie"], {"battle_state": 146, "rehide_chance": 0.5})
        self.assertEqual(effects["Rat Child"], {"battle_state": 115, "level_floor_below_leader": 2})

    def test_plugin_embeds_the_same_companion_data(self):
        plugin = (ROOT / "game_plugin/LookOutsideArchipelago.js").read_text(encoding="utf-8")
        for row in COMPANIONS:
            self.assertIn(f'"actorId": {row["actor_id"]}, "name": "{row["name"]}", '
                          f'"key": "{row["location"]["key"]}", "apId": {row["location"]["ap_id"]}', plugin)
            self.assertIn(f'{row["item"]["ap_id"]}: Object.freeze({{"kind": "upgrade", "id": {row["actor_id"]}', plugin)




class DailyLifeTests(unittest.TestCase):
    def test_three_filler_only_moments_with_one_supply_cache_each(self):
        self.assertEqual(len(DAILY_LIFE["locations"]), 3)
        self.assertEqual(DAILY_LIFE["items"], [{"name": "Supply Cache", "quantity": 3}])
        for row in DAILY_LIFE["locations"]:
            self.assertTrue(593000200 < row["ap_id"] < 593000300)
            self.assertIn(row["region"], GRAPH.regions)
            self.assertIn(row["trigger"]["switch_id"], {602, 603, 605})
            self.assertNotIn(row["key"], GRAPH.checks)

    def test_plugin_embeds_the_same_triggers(self):
        plugin = (ROOT / "game_plugin/LookOutsideArchipelago.js").read_text(encoding="utf-8")
        self.assertIn(f"const dailyLifeVersion = {DAILY_LIFE['feature_version']};", plugin)
        for row in DAILY_LIFE["locations"]:
            self.assertIn(f'"key": "{row["key"]}", "name": "{row["name"]}", "apId": {row["ap_id"]}', plugin)

class VersionTests(unittest.TestCase):
    def test_plugin_and_apworld_versions_match(self):
        manifest = json.loads((ROOT / "apworld/lookoutside/archipelago.json").read_text(encoding="utf-8"))
        plugin = (ROOT / "game_plugin/LookOutsideArchipelago.js").read_text(encoding="utf-8")
        self.assertIn(f'const pluginVersion = "{manifest["world_version"]}";', plugin)

if __name__ == "__main__":
    unittest.main()
