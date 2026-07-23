from typing import Optional , Literal , Tuple
from pathlib import Path
from PIL import Image , ImageFont 
from io import BytesIO
import os 
from collections import OrderedDict
import aiohttp
import asyncio 


base_path = Path(__file__).parent.parent / "assets"
cache_path = Path(__file__).parent.parent / "cache"
font_path=base_path/"fonts"

def _resolve_local_asset_path(asset_name: str) -> Path:
    candidate_dirs = [
        base_path / "relics",
        base_path / "character1" / "relics",
        base_path / "profile1",
        base_path / "character1" / "common",
        base_path / "character1" / "main",
        base_path / "character1" / "stats",
    ]

    for directory in candidate_dirs:
        candidate = directory / f"{asset_name}.png"
        if candidate.exists():
            return candidate

    return base_path / "relics" / f"{asset_name}.png"


local_asset_map={
    "relic_bg": _resolve_local_asset_path("relic_bg"),
    "lvl_max": _resolve_local_asset_path("lvl_max"),
    "up_arrow": _resolve_local_asset_path("up_arrow"),
    "score":_resolve_local_asset_path("score"),
    "star":_resolve_local_asset_path("star"),
    "stat_bg":_resolve_local_asset_path("stat_bg"),
    "SE":_resolve_local_asset_path("SE"),
    "combo":_resolve_local_asset_path("combo"),
    "char4":_resolve_local_asset_path("char4"),
    "char5":_resolve_local_asset_path("char5"),
    "pfpbg":_resolve_local_asset_path("pfpbg"),
    "charicon":_resolve_local_asset_path("charicon"),
    "ptop":_resolve_local_asset_path("ptop"),
    "chat":_resolve_local_asset_path("chat"),
    "pfpmain":_resolve_local_asset_path("pfpmain"),
    "circle":_resolve_local_asset_path("circle"),
}

local_literal=Literal[
    "relic_bg","lvl_max","up_arrow","score","star","stat_bg","SE","combo",
    "char4","char5","pfpbg","charicon","ptop","chat","pfpmain","circle"
]

class Fonts:
    FONT_FILES = {
        "bold": font_path / "DIN-Bold.ttf",
        "medium": font_path / "DIN-Medium.ttf",
        "regular": font_path / "DIN-Regular.ttf",
        "light": font_path / "DIN-Light.ttf",
    }
    def __init__(self) -> None:
        self.bold = self.FONT_FILES["bold"]
        self.medium = self.FONT_FILES["medium"]
        self.regular = self.FONT_FILES["regular"]
        self.light = self.FONT_FILES["light"]
        
    @staticmethod
    def get(
        font_type: Literal["bold", "medium", "regular", "light"],
        size: int
        ) -> ImageFont.FreeTypeFont:
        font_file = Fonts.FONT_FILES.get(font_type.lower())
        if font_file is None:
            raise ValueError(
                f"Unknown font type {font_type!r}. Use one of: {', '.join(Fonts.FONT_FILES)}"
            )
        if not font_file.exists():
            raise FileNotFoundError(f"Font file not found: {font_file}")
        return ImageFont.truetype(str(font_file), size)

class AssetCache:
    def __init__(self, limit: int = 100):
        self.base_path = base_path
        self.cache_path = cache_path
        self.cache: OrderedDict[str, Path] = OrderedDict()
        self.local_cache = {key: Path(path) for key, path in local_asset_map.items()}
        self.limit = limit
        try:
            self.cache_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise RuntimeError(f"Failed to create cache directory at {self.cache_path}: {e}")
        try:
            for f in self.cache_path.iterdir():
                if f.is_file() and f.suffix in {'.png', '.jpg', '.jpeg'}:
                    key = f.stem  
                    self.cache[key] = f
        except OSError as e:
            raise RuntimeError(f"Failed to read cache directory: {e}")

    def store(self, key: str, img: Image.Image) -> None:
        if not isinstance(img, Image.Image):
            raise TypeError(f"Expected PIL Image, got {type(img)}")
        try:
            cache_file = self.cache_path / f"{key}.png"
            img.save(cache_file)
            if key in self.cache:
                self.cache.move_to_end(key)
            else:
                self.cache[key] = cache_file
            while len(self.cache) > self.limit:
                oldest_key, oldest_path = self.cache.popitem(last=False)
                try:
                    oldest_path.unlink()
                except OSError as e:
                    print(f"Warning: Failed to delete evicted cache file {oldest_path}: {e}")
        except IOError as e:
            raise RuntimeError(f"Failed to save cache file for key '{key}': {e}")
        
    def get(self, key: str) -> Image.Image | None:
        if key not in self.cache:
            return None
        cache_file = self.cache[key]
        if not cache_file.exists():
            del self.cache[key]
            return None
        try:
            img = Image.open(cache_file)
            img.load()  
            self.cache.move_to_end(key)
            return img.convert("RGBA").copy()
        except Exception as e:
            print(f"Warning: Failed to load cache file {cache_file}: {e}")
            try:
                cache_file.unlink()
            except OSError:
                pass
            del self.cache[key]
            return None
        
    def get_local(self, key: local_literal) -> Image.Image | None:
        if key not in self.local_cache:
            print(f"Warning: Local asset key {key} not found in local cache.")
            return None
        local_file = self.local_cache[key]
        if not local_file.exists():
            print(f"Warning: Local asset file {local_file} does not exist.")
            return None
        try:
            img = Image.open(local_file)
            img.load()  
            return img.convert("RGBA").copy()
        except Exception as e:
            print(f"Warning: Failed to load local asset file {local_file}: {e}")
            return None
        
class AssetManager:
        def __init__(
            self,
            asset_cache:AssetCache
            ) -> None:
            self.cache=asset_cache

        async def close(self):
            return None

        async def get_asset_from_url(self,url:str,size:Tuple[int,int])->Image.Image|None:
            name=url.split("/")[-1].split(".")[0]
            key=f"{name}_{size[0]}x{size[1]}"
            img = await asyncio.to_thread(self.cache.get, key)
            if img:
                return img
            else:
                timeout = aiohttp.ClientTimeout(total=10)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.read()
                            img = Image.open(BytesIO(data)).convert("RGBA")
                            img = img.resize(size)
                            await asyncio.to_thread(self.cache.store,key,img)
                            return img
                        return None
                    
        def clear_cache(self):
            self.cache.cache.clear()
            for f in self.cache.cache_path.iterdir():
                if f.is_file() and f.suffix in {'.png', '.jpg', '.jpeg'}:
                    try:
                        f.unlink()
                    except OSError as e:
                        print(f"Warning: Failed to delete cache file {f}: {e}")
        
        async def get_local_asset(self,key:local_literal,size:Tuple[int,int])->Image.Image|None:
            img=await asyncio.to_thread(self.cache.get_local,key)
            if img:
                img=img.resize(size)
                return img
            else:
                return None
            
            
asset_cache=AssetCache(limit=500)
asset_manager=AssetManager(asset_cache)