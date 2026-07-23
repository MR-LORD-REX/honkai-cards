from pathlib import Path
import json

from honkai_cards.api import BuildCardResponse


def test_build_card_response_parses_sample_payload():
    payload = {
        'uid': 800556377,
        'configType': 'dps',
        'character': {
            'id': '1005b1',
            'name': 'Kafka',
            'eidolon': 0,
            'level': 80,
            'rarity': 5,
            'element': {
                'name': 'Lightning',
                'icon': 'https://example.com/element.webp'
            },
            'path': {
                'name': 'Nihility',
                'icon': 'https://example.com/path.webp'
            },
            'icon': 'https://example.com/avatar.webp',
            'splashArt': 'https://example.com/splash.webp'
        },
        'lightCone': {
            'id': '21001',
            'name': 'Good Night and Sleep Well',
            'rarity': 4,
            'icon': 'https://example.com/cone.webp',
            'art': 'https://example.com/cone-art.webp',
            'superimpose': 5
        },
        'benchmark': {'percent': 0.37646339332727313, 'rank': 'F'},
        'teammates': [
            {
                'characterId': '1307b1',
                'icon': 'https://example.com/1307b1.webp',
                'eidolon': 0,
                'lightConeId': '23022',
                'lightConeIcon': 'https://example.com/23022.webp',
                'superimposition': 1
            }
        ],
        'scores': {
            'originalSimScore': 556273.8325891425,
            'benchmarkSimScore': 744277.6960370293,
            'perfectionSimScore': 950182.416882567,
            'benchmarkBaselineScore': 442765.5451288411
        },
        'baseStats': {
            'hp': {'name': 'HP', 'icon': 'https://example.com/hp.webp', 'value': 3154.182373046875, 'isPercent': False},
            'atk': {'name': 'ATK', 'icon': 'https://example.com/atk.webp', 'value': 3785.724609375, 'isPercent': False},
        },
        'combatStats': {
            'hp': {'name': 'HP', 'icon': 'https://example.com/hp.webp', 'value': 3154.182373046875, 'isPercent': False},
            'atk': {'name': 'ATK', 'icon': 'https://example.com/atk.webp', 'value': 3785.724609375, 'isPercent': False},
        },
        'relics': [
            {
                'part': 'Head',
                'set': 'Messenger Traversing Hackerspace',
                'icon': 'https://example.com/relic.webp',
                'charIcon': 'https://example.com/char.webp',
                'lvl': 15,
                'isMaxed': True,
                'grade': 5,
                'mainStat': {'name': 'HP', 'icon': 'https://example.com/hp.webp', 'value': 705.6, 'isPercent': False},
                'substats': [
                    {'name': 'DEF', 'icon': 'https://example.com/def.webp', 'value': 35.98692, 'isPercent': False, 'rolledTimes': 2}
                ],
                'score': {'value': 52.8, 'rank': 'S'}
            }
        ]
    }

    model = BuildCardResponse.model_validate(payload)

    assert model.uid == 800556377
    assert model.character.name == 'Kafka'
    assert model.relics[0].part == 'Head'
    assert model.relics[0].substats[0].rolledTimes == 2
