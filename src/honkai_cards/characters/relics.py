from PIL import Image , ImageFont, ImageDraw , ImageFilter
import asyncio

from ..models.build_card import Relic
from ..utils.asset_manager import asset_manager as AM , Fonts
from ..utils.image import paste_border

f30=Fonts.get("bold",30)

async def get_up_arrow(rolled:int)->Image.Image:
    if rolled>1:
        ar=await AM.get_local_asset("up_arrow",(8,12))
        if ar is None:
            ar = Image.new("RGBA",(8,12),(0,0,0,0))
        new=Image.new("RGBA",(8*rolled,12),(0,0,0,0))
        for i in range(rolled-1):
            new.alpha_composite(ar,(i*8,0))
        return new
    else:
        new=Image.new("RGBA",(8,12),(0,0,0,0))
        return new

async def get_rolled_icons(rolls:list[int])->list[Image.Image]:
    icons=[]
    for rolled in rolls:
        icon=await get_up_arrow(rolled)
        icons.append(icon)
    return icons
    
def paste(
    bg:Image.Image,
    overlay:Image.Image,
    position:tuple[int,int],
):
    bg.alpha_composite(overlay,position)
    
def paste_text(
    draw:ImageDraw.ImageDraw,
    text:str,
    position:tuple[int,int],
    font:ImageFont.FreeTypeFont,
    fill:tuple[int,int,int,int]=(255,255,255,255),
):
    draw.text(position,text,font=font,fill=fill)
    
async def get_sub_stat_icon(subs:Relic)->list[Image.Image]:
    icons=[]
    for sub in subs.substats:
        icon=await AM.get_asset_from_url(sub.icon,(43,43))
        if icon:
            icons.append(icon)
    return icons

async def build_relic(relic:Relic)->Image.Image:
    relic_bg=Image.new("RGBA",(413,576),(0,0,0,124))
    relic_bg.filter(ImageFilter.GaussianBlur(40))
    paste_border(relic_bg,4)
    if not relic_bg:
        raise RuntimeError("relic bg not found")
    relic_draw=ImageDraw.Draw(relic_bg)
    
    icon_main = await AM.get_asset_from_url(relic.icon,(103,103))
    icon_character = await AM.get_asset_from_url(relic.charIcon,(97,97))
    icon_lvl_max = await AM.get_local_asset('lvl_max',(28,28))
    icon_main_stat = await AM.get_asset_from_url(relic.mainStat.icon,(43,43))
    sub_stat_icons = await get_sub_stat_icon(relic)
    score_icon = await AM.get_local_asset("score",(43,43))
    rolled_icons = await get_rolled_icons([sub.rolledTimes or 1 for sub in relic.substats])

    t=[]
    if score_icon is not None:
        t.append(asyncio.to_thread(paste,relic_bg,score_icon,(20,506)))
        t.append(asyncio.to_thread(paste_text,relic_draw,"Score",(68,510),f30,(255,255,255,255)))
        
    if relic.score.value>0:
        t.append(asyncio.to_thread(paste_text,relic_draw,f"{relic.score.value:.1f}({relic.score.rank})",(270,510),f30,(255,255,255,255)))

    if icon_lvl_max is not None and relic.isMaxed:
        t.append(asyncio.to_thread(paste,relic_bg,icon_lvl_max,(162,63)))
    t.append(asyncio.to_thread(paste_text,relic_draw,f"+{relic.lvl}",(200,58),f30,(255,255,255,255)))
    if icon_main is not None:
        t.append(asyncio.to_thread(paste,relic_bg,icon_main,(26,25)))
    if icon_character is not None:
        t.append(asyncio.to_thread(paste,relic_bg,icon_character,(288,28)))
    if icon_main_stat is not None:
        t.append(asyncio.to_thread(paste,relic_bg,icon_main_stat,(20,180)))
    t.append(asyncio.to_thread(paste_text,relic_draw,f"{relic.mainStat.name}",(68,185),f30,(255,255,255,255)))
    mv=f"{relic.mainStat.value:.1f}" if not relic.mainStat.isPercent else f"{relic.mainStat.value:.1f}%"
    t.append(asyncio.to_thread(paste_text,relic_draw,mv,(315,185),f30,(255,255,255,255)))

    for index, (icon, sub, roll) in enumerate(zip(sub_stat_icons, relic.substats, rolled_icons)):
        t.append(asyncio.to_thread(paste,relic_bg,icon,(20,277+index*43)))
        t.append(asyncio.to_thread(paste_text,relic_draw,f"{sub.name}",(68,282+index*43),f30,(255,255,255,255)))
        t.append(asyncio.to_thread(paste,relic_bg,roll,(251,293+index*43)))
        sval=f"{sub.value:.1f}" if not sub.isPercent else f"{sub.value:.1f}%"
        t.append(asyncio.to_thread(paste_text,relic_draw,f"{sval}",(315,282+index*43),f30,(255,255,255,255)))
        
    await asyncio.gather(*t)
    
    return relic_bg

async def build_relic_panel(relics:list[Relic])->Image.Image:
    bg=Image.new("RGBA",(844,1760),(0,0,0,0))

    positions=[
        (0,8),
        (431,8),
        (0,592),
        (431,592),
        (0,1176),
        (431,1176),
    ]

    relics=relics[:len(positions)]

    if not relics:
        return bg

    relic_imgs=await asyncio.gather(*(build_relic(r) for r in relics))

    await asyncio.gather(*(
        asyncio.to_thread(paste,bg,img,pos)
        for img,pos in zip(relic_imgs,positions)
    ))

    return bg