import importlib
import sys

from honkai_cards.utils.asset_manager import AssetCache


def test_importing_relics_does_not_require_running_loop():
    for module_name in ["honkai_cards.characters.relics", "honkai_cards.utils.asset_manager"]:
        sys.modules.pop(module_name, None)

    relics_module = importlib.import_module("honkai_cards.characters.relics")

    assert relics_module.AM is not None


def test_local_relic_assets_resolve_from_packaged_files():
    cache = AssetCache()

    assert cache.get_local("relic_bg") is not None
    assert cache.get_local("lvl_max") is not None
    assert cache.get_local("up_arrow") is not None
