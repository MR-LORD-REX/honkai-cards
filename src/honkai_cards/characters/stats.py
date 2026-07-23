from PIL import Image , ImageFont, ImageDraw , ImageFilter
import asyncio

from ..models.build_card import StatBundle,BuildCardResponse , Teammate , BenchmarkDisplay ,Benchmark
from ..utils.asset_manager import asset_manager as AM , Fonts
from ..utils.image import paste,paste_text,align_center_paste,align_center_paste_text,paste_border

f20=Fonts.get("bold",20)
f30=Fonts.get("bold",30)
f36=Fonts.get("bold",36)
f48=Fonts.get("bold",48)


async def build_stars(rarity:int)->Image.Image:
    star=await AM.get_local_asset("star",(36,36))
    if star is None:
        star = Image.new("RGBA",(36,36),(0,0,0,0))
    new=Image.new("RGBA",(36*rarity + ((rarity-1) * 7),36),(0,0,0,0))
    for i in range(rarity):
        new.alpha_composite(star,(i*36 + (i*7),0))
    return new

async def render_teamate(tm:Teammate)->Image.Image:
    new=Image.new("RGBA",(128,280))
    t=[]
    rect=await AM.get_local_asset("SE",(90,35))
    if not rect:
        raise RuntimeError("no rect found")
    
    r1,r2=rect.copy(),rect.copy()
    rd1,rd2=ImageDraw.Draw(r1),ImageDraw.Draw(r2)
    ch,lc,_,_=await asyncio.gather(
        AM.get_asset_from_url(tm.icon,(128,128)),
        AM.get_asset_from_url(tm.lightConeIcon,(124,124)),
        asyncio.to_thread(align_center_paste_text,rd1,f"E{tm.eidolon}",f20,10),
        asyncio.to_thread(align_center_paste_text,rd2,f"S{tm.superimposition}",f20,10)
    )

    if ch:
        t.append(asyncio.to_thread(align_center_paste,new,ch,0))
    if lc:
        t.append(asyncio.to_thread(align_center_paste,new,lc,143))
    await asyncio.gather(*t)
    t.clear()
    t.append(asyncio.to_thread(align_center_paste,new,r1,117))
    t.append(asyncio.to_thread(align_center_paste,new,r2,245))
    
    await asyncio.gather(*t)
    
    return new

async def render_team(bg:Image.Image,teamates:list[Teammate],rank:Benchmark,t_name:str):
    new=Image.new("RGBA",(478,445))
    draw=ImageDraw.Draw(new)
    t=[]
    tms=[render_teamate(t) for t in teamates]
    tms=await asyncio.gather(*tms)
    for i,icon in enumerate(tms):
        t.append(asyncio.to_thread(paste,new,icon,(24+i*151,135)))
    perc="0.0% - F"
    if rank.percent:
        perc=f"{rank.percent*100:.2f}% : {rank.rank}"
    name=f"{t_name} Benchmark"
    t.append(asyncio.to_thread(align_center_paste_text,draw,perc,f36,0,(212,175,55,255)))
    t.append(asyncio.to_thread(align_center_paste_text,draw,name,f36,53,(212,175,55,255)))
    await asyncio.gather(*t)
    bg.alpha_composite(new,(0,850))
    return

async def render_stats(main_bg:Image.Image,res:BuildCardResponse,bench:BenchmarkDisplay|None=None):
    draw=ImageDraw.Draw(main_bg)
    combo=await AM.get_local_asset("combo",(43,43))
    icons=[]
    for stat in (
    res.baseStats.hp,
    res.baseStats.atk,
    res.baseStats.def_,
    res.baseStats.spd,
    res.baseStats.critRate,
    res.baseStats.critDmg,
    res.baseStats.ehr,
    res.baseStats.res,
    res.baseStats.be,
    res.baseStats.err,
    res.baseStats.ohb,
    res.baseStats.elation,
    res.baseStats.dmgBoost,
    ):
        if stat is None:
            continue
        icons.append(AM.get_asset_from_url(stat.icon,(43,43)))
    icons=await asyncio.gather(*icons)
    t=[]
    last=0
    for i,(icon,st) in enumerate(zip(
    icons,
    (res.baseStats.hp,
    res.baseStats.atk,
    res.baseStats.def_,
    res.baseStats.spd,
    res.baseStats.critRate,
    res.baseStats.critDmg,
    res.baseStats.ehr,
    res.baseStats.res,
    res.baseStats.be,
    res.baseStats.err,
    res.baseStats.ohb,
    res.baseStats.elation,
    res.baseStats.dmgBoost,
    ))):
        t.append(asyncio.to_thread(paste,main_bg,icon,(15,237+i*43)))
        t.append(asyncio.to_thread(paste_text,draw,f"{st.name}",(67,242+i*43),f30))
        value=f"{st.value:.1f}" if not st.isPercent else f"{st.value*100:.1f}%"
        t.append(asyncio.to_thread(paste_text,draw,value,(370,242+i*43),f30))
        last=i
    last+=1
    if bench:
        if combo:
            t.append(asyncio.to_thread(paste,main_bg,combo,(15,237+last*43)))
        t.append(asyncio.to_thread(paste_text,draw,f"{bench.name}",(67,242+last*43),f30))
        value=bench.value if bench.value else 0.0
        if bench.type=="dmg":
            value=f"{round(value/1000,2)}K"
        elif bench.type=="percent":
            value=f"{value*100:.1f}%"
        else:
            value=f"{round(value,2)}"
        t.append(asyncio.to_thread(paste_text,draw,value,(300,242+last*43),f30))

    await asyncio.gather(*t)
    
async def render_header(main_bg:Image.Image,res:BuildCardResponse):
    draw=ImageDraw.Draw(main_bg)
    t=[]
    ele,stars,path=await asyncio.gather(
        AM.get_asset_from_url(res.character.element.icon,(65,65)),
        build_stars(res.character.rarity),
        AM.get_asset_from_url(res.character.path.icon,(65,65))
    )
    if ele:
        t.append(asyncio.to_thread(paste,main_bg,ele,(30,10)))
    if path:
        t.append(asyncio.to_thread(paste,main_bg,path,(386,10)))
    t.append(asyncio.to_thread(align_center_paste,main_bg,stars,23))
    t.append(asyncio.to_thread(align_center_paste_text,draw,res.character.name,f48,85))
    txt=f"Lv{res.character.level} E{res.character.eidolon}"
    t.append(asyncio.to_thread(align_center_paste_text,draw,txt,f30,150))
    await asyncio.gather(*t)
    
async def render_bench_stats(main_bg:Image.Image,stats:StatBundle):
    bg=Image.new("RGBA",(478,505),(0,0,0,0))
    draw=ImageDraw.Draw(bg)
    text="Combat Stats"
    align_center_paste_text(draw,text,f36,fill=(212,175,55,255),y=0)
    e_stats=[
        s for s in (
            stats.hp,
            stats.atk,
            stats.def_,
            stats.spd,
            stats.critRate,
            stats.critDmg,
            *(x for x in (
                stats.elation,
                stats.dmgBoost,
                stats.hpPercent,
                stats.atkPercent,
                stats.defPercent,
                stats.ehr,
                stats.res,
                stats.be,
                stats.err,
                stats.ohb,
            ) if x and x.isDelta),
        ) if s
    ]
    

    icons = await asyncio.gather(
        *[AM.get_asset_from_url(st.icon, (43, 43)) for st in e_stats]
    )
    t=[]
    for i, (icon,st) in enumerate(zip(icons,e_stats)):
        t.append(asyncio.to_thread(paste,bg,icon,(15,20+i*43)))
        name=f"{st.name} ≥" if st.isDelta else st.name
        t.append(asyncio.to_thread(paste_text,draw,name,(58,25+i*43),f30))
        value=f"{st.value:.1f}" if not st.isPercent else f"{st.value*100:.1f}%"
        t.append(asyncio.to_thread(paste_text,draw,value,(364,25+i*43),f30))

    await asyncio.gather(*t)
    await asyncio.to_thread(paste,main_bg,bg,(0,1355))
        
async def build_stats_panel(res:BuildCardResponse)->Image.Image:
    bg=Image.new("RGBA",(478,1743),(0,0,0,124))
    bg.filter(ImageFilter.GaussianBlur(40))
    paste_border(bg,4,radius=5)
    if not bg:
        raise RuntimeError("stat bg not found")
    t=[]
    t.append(render_stats(bg,res,res.benchmarkDisplay))
    t.append(render_header(bg,res))
    if res.hasBenchmark:
        t.append(render_team(bg,res.teammates,res.benchmark,res.configType))
        t.append(render_bench_stats(bg,res.benchmarkStats))
    
    await asyncio.gather(*t)
    return bg