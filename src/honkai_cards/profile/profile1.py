from PIL import Image, ImageFont, ImageDraw, ImageFilter
import asyncio

from ..models.profile import Player,Character,Profile
from ..utils.asset_manager import asset_manager as AM, Fonts
from ..utils.image import (
    paste, paste_text, 
    align_center_paste, 
    align_center_paste_text, 
    paste_center, crop_from_center, 
    paste_border , paste_text_center
)

f13=Fonts.get("bold",13)
f16=Fonts.get("bold",16)
f20=Fonts.get("bold",20)
f22=Fonts.get("bold",22)
f24=Fonts.get("bold",24)

async def render_char(main_bg:Image.Image,char:Character,idx:int,loc:str="t"):
    bg=None
    if char.rarity==4:
        bg=await AM.get_local_asset("char4",(244,345))
    else:
        bg=await AM.get_local_asset("char5",(244,345))
    draw=ImageDraw.Draw(bg)
    char_icon=await AM.get_asset_from_url(char.icons.card,(245,334))
    paste(bg,char_icon,(0,0))
    t=[]
    lv=f"Lv.{char.lvl} E{char.eidolon}"
    t.append(asyncio.to_thread(paste_text_center,bg,char.name,f22,262))
    t.append(asyncio.to_thread(align_center_paste_text,draw,lv,f24,307))
    await asyncio.gather(*t)
    if idx<3 and loc=="t":
        main_bg.alpha_composite(bg,(25+idx*273,63))
    else:
        bg=bg.resize((154,243))
        main_bg.alpha_composite(bg,((25+idx*160,465)))
        
async def render_characters(main_bg:Image.Image,characters:list[Character]):
    bg=await AM.get_local_asset("pfpbg",(841,739))
    if not bg:
        bg=Image.new("RGBA",(783,775))
    t=[]
    for i , c in enumerate(characters):
        l="t"
        if i>2:
            i-=3
            l="b"
        t.append(render_char(bg,c,i,l))
    await asyncio.gather(*t)
    main_bg.alpha_composite(bg.resize((783,775)),(23,284))
    
async def render_top(main_bg:Image.Image,p:Player):
    bg=await AM.get_local_asset("ptop",(202,214))
    chat=await AM.get_local_asset("chat",(566,214))
    if not bg or not chat:
        bg=Image.new("RGBA",size=(202,214))
        chat=Image.new("RGBA",(537,214))
    
    ch,chb,cr,_=await asyncio.gather(
        AM.get_asset_from_url(p.icon,(106,106)),
        AM.get_local_asset("charicon",(150,167)),
        AM.get_local_asset("circle",(36,36)),
        asyncio.to_thread(paste_text_center,chat,f"{p.signature}",f24)
    )
    t=[]
    if ch:
        t.append(asyncio.to_thread(align_center_paste,chb,ch,5))
    if chb:
        chbd=ImageDraw.Draw(chb)
        t.append(asyncio.to_thread(align_center_paste_text,chbd,f"{p.uid}",f13,112,fill=(0,0,0,255)))
        t.append(asyncio.to_thread(align_center_paste_text,chbd,f"{p.nickname}",f16,132,fill=(0,0,0,255)))
    
    await asyncio.gather(*t)
    crd=ImageDraw.Draw(cr)
    align_center_paste_text(crd,f"{p.level}",f16,10,fill=(0,0,0,255))
    chb.alpha_composite(cr,(111,76))
    paste_center(bg,chb)
    
    main_bg.alpha_composite(bg,(23,39))
    main_bg.alpha_composite(chat,(240,39))

async def build_profile1(pfp:Profile)->Image.Image:
    bg=await AM.get_local_asset("pfpmain",(828,1078))
    if not bg:
        bg=Image.new("RGBA",(828,1078))
    
    t=[]
    t.append(render_characters(bg,pfp.characters))
    t.append(render_top(bg,pfp.player))
    await asyncio.gather(*t)
    return bg