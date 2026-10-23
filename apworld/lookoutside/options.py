"""Player options. Every feature defaults off so existing YAMLs keep their pool."""

from dataclasses import dataclass

from Options import PerGameCommonOptions, Toggle


class ActivityChecks(Toggle):
    """Adds three optional checks: cooking your first and third meal, and crafting
    your first item. You keep the food and the crafted item. These checks only
    ever hold filler, so they never block anyone's progression."""
    display_name = "Activity Checks"


class CompanionUpgrades(Toggle):
    """Adds one upgrade item per recruitable companion, plus a filler-only check
    when each companion first joins your party. Each upgrade is a passive that
    fits the companion's playstyle and adds to their normal abilities, such as
    Sophie starting battles hidden or Rat Child catching up in level. Upgrades
    received before recruitment apply once that companion joins."""
    display_name = "Companion Upgrades"


@dataclass
class LookOutsideOptions(PerGameCommonOptions):
    activity_checks: ActivityChecks
    companion_upgrades: CompanionUpgrades
