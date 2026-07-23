from PIL import Image , ImageDraw , ImageFont

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

def align_center_paste(
    bg:Image.Image,
    overlay:Image.Image,
    y:int,
):
    x=(bg.width-overlay.width)//2
    bg.alpha_composite(overlay,(x,y))
    
def align_center_paste_text(
    draw:ImageDraw.ImageDraw,
    text:str,
    font:ImageFont.FreeTypeFont,
    y:int,
    fill:tuple[int,int,int,int]=(255,255,255,255),
):
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (draw.im.size[0] - text_width) // 2
    draw.text((x,y),text,font=font,fill=fill)

def paste_center(
    bg:Image.Image,
    overlay:Image.Image,
):
    x=(bg.width-overlay.width)//2
    y=(bg.height-overlay.height)//2
    bg.alpha_composite(overlay,(x,y))
    
def crop_from_center(
    img:Image.Image,
    size:tuple[int,int],
    x_offset:int=0,
    y_offset:int=0,
)->Image.Image:
    w,h=size
    cx=img.width//2+x_offset
    cy=img.height//2+y_offset

    left=max(0,cx-w//2)
    top=max(0,cy-h//2)
    right=min(img.width,left+w)
    bottom=min(img.height,top+h)

    if right-left<w:
        left=max(0,right-w)
    if bottom-top<h:
        top=max(0,bottom-h)

    return img.crop((left,top,right,bottom))

def paste_border(
    img:Image.Image,
    width:int,
    color:tuple[int,int,int,int]=(255,255,255,100),
    radius:int=0,
):
    draw=ImageDraw.Draw(img)

    if radius>0:
        draw.rounded_rectangle(
            (
                width//2,
                width//2,
                img.width-width//2-1,
                img.height-width//2-1,
            ),
            radius=radius,
            outline=color,
            width=width,
        )
    else:
        draw.rectangle(
            (
                width//2,
                width//2,
                img.width-width//2-1,
                img.height-width//2-1,
            ),
            outline=color,
            width=width,
        )
        
        
from PIL import Image, ImageDraw, ImageFont


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.splitlines() or [""]:
        words = paragraph.split(" ")
        current = ""

        for word in words:
            candidate = f"{current} {word}".strip()
            width = draw.textlength(candidate, font=font)

            if width <= max_width or not current:
                current = candidate
            else:
                lines.append(current)
                current = word
            while draw.textlength(current, font=font) > max_width and len(current) > 1:
                lo, hi = 1, len(current)
                while lo < hi:
                    mid = (lo + hi + 1) // 2
                    if draw.textlength(current[:mid], font=font) <= max_width:
                        lo = mid
                    else:
                        hi = mid - 1
                lines.append(current[:lo])
                current = current[lo:]
        lines.append(current)
    return lines

def paste_text_center(
    img: Image.Image,
    text: str,
    font: ImageFont.FreeTypeFont,
    y: int | None = None,
    fill=(255, 255, 255, 255),
    max_width: int | None = None,
    line_spacing: int = 6,
) -> int | float:
    """
    Draws text onto img, horizontally centered. If y is given, the text block
    starts at that vertical position. If y is omitted, the whole wrapped block
    is centered vertically in img as well.
    Automatically wraps long text onto multiple lines to fit within max_width
    (defaults to img.width if not given).

    Returns the y-coordinate immediately below the last line drawn (useful for
    stacking further content beneath the text block).
    """
    draw = ImageDraw.Draw(img)
    width_limit = max_width or img.width

    lines = _wrap_text(draw, text, font, width_limit)

    # measure line heights up front so we can center the whole block if needed
    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_heights.append(bbox[3] - bbox[1])

    total_height = sum(line_heights) + line_spacing * (len(lines) - 1)

    cursor_y = y if y is not None else (img.height - total_height) // 2

    for line, line_h in zip(lines, line_heights):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        x = (img.width - line_w) // 2
        draw.text((x, cursor_y), line, font=font, fill=fill)
        cursor_y += line_h + line_spacing

    return cursor_y