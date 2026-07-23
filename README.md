# honkai-cards

[![PyPI version](https://img.shields.io/pypi/v/honkai_cards.svg)](https://pypi.org/project/honkai_cards/)
[![Python](https://img.shields.io/pypi/pyversions/honkai_cards.svg)](https://pypi.org/project/honkai_cards/)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-blue.svg)](https://github.com/MR-LORD-REX/honkai-cards/blob/main/LICENSE.txt)

A Python library that generates **Honkai: Star Rail** character showcase cards and player profile cards — optionally with DPS benchmarks.

**Repository:** [github.com/MR-LORD-REX/honkai-cards](https://github.com/MR-LORD-REX/honkai-cards)

---

## Features

- **Character cards** — full showcase art with relics, stats, and optional DPS benchmark
- **Profile cards** — player info plus showcase character roster
- **Async API** — `async with HSR()` context manager
- **Enka-powered profiles** — pulls live showcase data from your UID

---

## Installation

```bash
pip install honkai_cards
```

Or from source:

```bash
git clone https://github.com/MR-LORD-REX/honkai-cards.git
cd honkai-cards
pip install -e .
```

**Requirements:** Python 3.10+, network access (Enka + build API)

---

## Quick start

```python
import asyncio
from honkai_cards import HSR

async def main():
    async with HSR() as hsr:
        # Profile card
        profile = await hsr.profile(800000000)
        profile.card.save("profile.png")

        # Character card (slot 0–7, with DPS benchmark)
        card = await hsr.character(800000000, slot=0, benchmark=True)
        if card:
            card.save("character.png")

asyncio.run(main())
```

---

## API

### `HSR`

Main client. Use as an async context manager.

| Method | Returns | Description |
|--------|---------|-------------|
| `character(uid, slot=0, benchmark=True)` | `PIL.Image.Image \| None` | Character showcase card for the given slot |
| `profile(uid)` | `Profile1` | Profile card + list of showcase characters |

#### `character`

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `uid` | `int \| str` | — | In-game UID |
| `slot` | `int` | `0` | Showcase slot (`0`–`7`) |
| `benchmark` | `bool` | `True` | Include DPS benchmark on the card |

#### `profile`

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `uid` | `int \| str` | — | In-game UID |

`Profile1` fields:

- `card` — `PIL.Image.Image` profile card
- `characters` — list of `P1Char` (`slot`, `charid`)

---

## Examples

Runnable scripts live in [`examples/`](https://github.com/MR-LORD-REX/honkai-cards/tree/main/examples). Replace `UID` with your own before running.

### Character card

```python
"""Generate a character showcase card with DPS benchmark."""

import asyncio
from honkai_cards import HSR

UID = 713987091  # replace with your in-game UID

async def main() -> None:
    async with HSR() as hsr:
        card = await hsr.character(UID, slot=0, benchmark=True)

        if card is None:
            print("No character found for this slot.")
            return

        card.save("character_card.png")
        print("Saved character_card.png")
        card.show()

if __name__ == "__main__":
    asyncio.run(main())
```

```bash
python examples/character_card.py
```

### Profile card

```python
"""Generate a player profile card and list showcase characters."""

import asyncio
from honkai_cards import HSR

UID = 713987091  # replace with your in-game UID

async def main() -> None:
    async with HSR() as hsr:
        profile = await hsr.profile(UID)

        profile.card.save("profile_card.png")
        print("Saved profile_card.png")
        print("Showcase characters:", profile.characters)

        for char in profile.characters:
            print(f"  slot {char.slot}: character id {char.charid}")

if __name__ == "__main__":
    asyncio.run(main())
```

```bash
python examples/profile_card.py
```

### Full showcase

Fetches the profile card, then a character card for every showcase slot:

```bash
python examples/full_showcase.py
```

---

## Publishing a release

Releases are published to PyPI automatically when you push a version tag.

1. Bump `version` in [`pyproject.toml`](pyproject.toml) (e.g. `1.0.1`).
2. Commit, then tag and push:

```bash
git tag v1.0.1
git push origin v1.0.1
```

The [publish workflow](.github/workflows/publish.yml) will:

1. Verify the tag (`v1.0.1`) matches `project.version` in `pyproject.toml`
2. Build the sdist and wheel
3. Upload to [PyPI](https://pypi.org/project/honkai_cards/) using `PYPI_TOKEN`

### One-time setup

1. Create an API token on [pypi.org](https://pypi.org/manage/account/token/) (scope: project `honkai_cards`, or entire account).
2. In the GitHub repo → **Settings** → **Secrets and variables** → **Actions**, add:
   - Name: `PYPI_TOKEN`
   - Value: the token (`pypi-...`)
3. (Optional) Create a GitHub Environment named `pypi` for release protection rules.

---

## Project layout

```
honkai-cards/
├── examples/                 # Runnable demos
│   ├── character_card.py
│   ├── profile_card.py
│   └── full_showcase.py
├── src/honkai_cards/         # Library package
│   ├── client.py             # HSR public API
│   ├── api.py                # Data fetchers
│   ├── characters/           # Character card renderer
│   ├── profile/              # Profile card renderer
│   └── models/               # Pydantic models
├── pyproject.toml
└── .github/workflows/publish.yml
```

---

## License

[GPL-3.0](LICENSE.txt) — see `LICENSE.txt` for details.

---

## Credits

- Profile data via [Enka.Network](https://enka.network/)
- Benchmark data taken after running simulation made by [fribbels](https://fribbels.github.io/hsr-optimizer/)
- Built for the Honkai: Star Rail community
