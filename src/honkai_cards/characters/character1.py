from PIL import Image, ImageFont, ImageDraw, ImageFilter
import asyncio

from ..models.build_card import BuildCardResponse, LightCone
from ..utils.asset_manager import asset_manager as AM, Fonts
from ..utils.image import paste, paste_text, align_center_paste, align_center_paste_text, paste_center, crop_from_center, paste_border

from .relics import build_relic_panel
from .stats import build_stats_panel

f35 = Fonts.get("bold", 35)
f25 = Fonts.get("bold",25)


async def render_lc(lc: LightCone) -> Image.Image:
    async def make_name_bg():
        name_bg = Image.new("RGBA", (450, 55), (0, 0, 0, 124))
        nd = ImageDraw.Draw(name_bg)
        txt = f"S{lc.superimpose} - {lc.name}"
        await asyncio.to_thread(align_center_paste_text, nd, txt, f25, 12)
        return name_bg

    name_bg, lc_bg, lc_icon = await asyncio.gather(
        make_name_bg(),
        asyncio.to_thread(Image.new, "RGBA", (845, 298), (0, 0, 0, 124)),
        AM.get_asset_from_url(lc.art, (904, 1260)),
    )

    if lc_icon:
        lc_icon = await asyncio.to_thread(crop_from_center, lc_icon, (845, 298), y_offset=-150)
        paste(lc_icon,name_bg,(377, 227))
        await   asyncio.to_thread(paste, lc_bg, lc_icon, (0, 0))
        
    return lc_bg


async def build_character1(char: BuildCardResponse) -> Image.Image:
    async def make_uid_bg():
        uid_bg = Image.new("RGBA", (188, 55), (0, 0, 0, 124))
        uid_draw = ImageDraw.Draw(uid_bg)
        txt = f"{char.uid}"
        await asyncio.to_thread(align_center_paste_text, uid_draw, txt, f35, 12)
        return uid_bg

    async def make_char_bg():
        char_bg = Image.new("RGBA", (845, 1439), (0, 0, 0, 124))
        char_bg = await asyncio.to_thread(char_bg.filter, ImageFilter.GaussianBlur(50))
        return char_bg

    uid_bg, char_bg, port1, port2 = await asyncio.gather(
        make_uid_bg(),
        make_char_bg(),
        AM.get_asset_from_url(char.character.portrait, (3800, 3800)),
        AM.get_asset_from_url(char.character.portrait, (2048, 2048)),
    )

    bg = Image.new("RGBA", (2200, 1760), (0, 0, 0, 124))

    if port1:
        bg = await asyncio.to_thread(crop_from_center, port1, (2200, 1760))
        bg = await asyncio.to_thread(bg.filter, ImageFilter.GaussianBlur(50))
        port2 = await asyncio.to_thread(crop_from_center, port2, (845, 1439))
        await asyncio.gather(
            asyncio.to_thread(paste, port2, uid_bg, (16, 1367)),
            asyncio.to_thread(paste_border, port2, 4),
        )

    lc_task = None
    if char.lightCone:
        lc_task = asyncio.ensure_future(render_lc(char.lightCone))

    rc, st, _, lc = await asyncio.gather(
        build_relic_panel(char.relics),
        build_stats_panel(char),
        asyncio.to_thread(paste, char_bg, port2, (0, 0)),
        lc_task if lc_task else asyncio.sleep(0, result=None),
    )

    if lc is not None:
        await asyncio.to_thread(paste, bg, lc, (8, 1457))

    await asyncio.gather(
        asyncio.to_thread(paste, bg, rc, (1350, 0)),
        asyncio.to_thread(paste, bg, st, (861, 8)),
        asyncio.to_thread(paste, bg, char_bg, (8, 8)),
    )

    return bg