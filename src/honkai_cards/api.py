from __future__ import annotations

from typing import Any, Optional

import aiohttp
import enka
from pydantic import ValidationError

from .models.build_card import BuildCardResponse
from .models.profile import Character, Icons, Player, PlayerStats, Profile
from .models.customTeams import Teammate , Teammates

CHARACTER_CARD_URL = (
    "https://github.com/fribbels/hsr-optimizer/raw/main/public/assets"
    "/image/character_preview/{char_id}.webp"
)


class BuildAPI:

    def __init__(self, base_url: str = "https://ilcapitano01-gi-card-api.hf.space") -> None:
        self.base_url = base_url.rstrip("/")

    async def get_build(
        self,
        uid: str | int,
        slot: int, *,
        benchmark: bool = True,
        session: Optional[aiohttp.ClientSession] = None
    ) -> BuildCardResponse:

        payload = {"uid": str(uid), "slot": slot, "benchmark": benchmark}
        url = f"{self.base_url}/getcals"

        if session is None:
            async with aiohttp.ClientSession() as client:
                return await self._request_build_card(client, url, payload)

        return await self._request_build_card(session, url, payload)
    
    async def get_custom_build(
        self,
        uid: str | int,
        slot: int, *,
        team: list[Teammate] , 
        benchmark: bool = True,
        session: Optional[aiohttp.ClientSession] = None
    ) -> BuildCardResponse:
        
        payload = {"uid": str(uid), "slot": slot, "benchmark": benchmark,"teammates":[t.model_dump() for t in team]}
        url = f"{self.base_url}/get_custom_cals"

        if session is None:
            async with aiohttp.ClientSession() as client:
                return await self._request_build_card(client, url, payload)

        return await self._request_build_card(session, url, payload)
        
    async def _request_build_card(self, session: aiohttp.ClientSession, url: str, payload: dict[str, Any]) -> BuildCardResponse:
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            data = await response.json()
        try:
            return BuildCardResponse.model_validate(data)
        except ValidationError as exc:
            raise ValueError("The response did not match the expected build-card schema") from exc

    async def get_profile(self, uid: str | int) -> Profile:
        async with enka.HSRClient() as client:
            showcase = await client.fetch_showcase(uid)

        player = Player(
            nickname=showcase.player.nickname,
            signature=showcase.player.signature,
            uid=showcase.player.uid,
            level=showcase.player.level,
            equilibrium_level=showcase.player.equilibrium_level,
            friend_count=showcase.player.friend_count,
            stats=PlayerStats(
                achievement_count=showcase.player.stats.achievement_count,
                light_cone_count=showcase.player.stats.light_cone_count,
                character_count=showcase.player.stats.character_count,
                max_simulated_universe_world=showcase.player.stats.max_simulated_universe_world or 0,
                book_count=showcase.player.stats.book_count or 0,
                relic_count=showcase.player.stats.relic_count or 0,
                music_count=showcase.player.stats.music_count or 0,
            ),
            icon=showcase.player.icon,
        )

        characters = [
            Character(
                id=char.id,
                icons=Icons(
                    character_id=str(char.icon.character_id),
                    round=char.icon.round,
                    gacha=char.icon.gacha,
                    card=CHARACTER_CARD_URL.format(char_id=char.id),
                ),
                eidolon=char.eidolons_unlocked,
                name=char.name,
                lvl=char.level,
                rarity=char.rarity,
                path=char.path.value,
                element=char.element.value,
            )
            for char in showcase.characters
        ]

        return Profile(characters=characters, player=player)