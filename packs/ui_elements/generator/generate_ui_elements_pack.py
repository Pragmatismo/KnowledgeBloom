#!/usr/bin/env python3
"""Generate a Knowledge in Bloom UI Elements seed pack using Pillow."""

from __future__ import annotations
import json, shutil, sys, zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PACK_ID = "ui_elements"
ROOT = Path.cwd() / PACK_ID
IMG_DIR = ROOT / "assets" / "images"
ZIP_PATH = Path.cwd() / f"{PACK_ID}_pack.zip"
CANVAS = (960, 720)

BG = (246, 247, 249)
WHITE = (255, 255, 255)
TEXT = (32, 36, 42)
MUTED = (105, 112, 122)
BORDER = (185, 191, 199)
ACCENT = (74, 122, 207)
ACCENT_LIGHT = (222, 232, 249)
GREEN = (72, 157, 96)
RED = (195, 74, 74)

def font(size, bold=False):
    names = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()

F18, F22, F28, F36 = font(18), font(22), font(28), font(36, True)

def box(d, xy, radius=14, fill=WHITE, outline=BORDER, width=3):
    d.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def center(d, xy, text, f=F28, fill=TEXT):
    x1,y1,x2,y2 = xy
    b = d.textbbox((0,0), text, font=f)
    d.text((x1+(x2-x1-(b[2]-b[0]))/2,
            y1+(y2-y1-(b[3]-b[1]))/2-b[1]), text, font=f, fill=fill)

def canvas():
    im = Image.new("RGB", CANVAS, BG)
    d = ImageDraw.Draw(im)
    box(d, (60,55,900,665), radius=28, fill=WHITE, outline=(220,224,230), width=3)
    return im,d

def chevron(d, x, y, direction="down"):
    pts = {
        "down":[(x-14,y-7),(x,y+7),(x+14,y-7)],
        "up":[(x-14,y+7),(x,y-7),(x+14,y+7)],
        "right":[(x-7,y-14),(x+7,y),(x-7,y+14)]
    }[direction]
    d.line(pts, fill=MUTED, width=4, joint="curve")

def button(d):
    box(d,(310,285,650,435),26,ACCENT,(45,92,170),4)
    center(d,(310,285,650,435),"Submit",F36,WHITE)

def checkbox(d):
    box(d,(280,300,360,380),10,ACCENT,(45,92,170),4)
    d.line([(298,340),(320,360),(345,315)],fill=WHITE,width=8,joint="curve")
    d.text((395,310),"Remember this choice",font=F28,fill=TEXT)

def radio(d):
    d.ellipse((285,300,365,380),fill=WHITE,outline=ACCENT,width=6)
    d.ellipse((307,322,343,358),fill=ACCENT)
    d.text((395,310),"Option A",font=F28,fill=TEXT)

def toggle(d):
    d.rounded_rectangle((320,295,640,425),radius=65,fill=GREEN,outline=(48,124,70),width=4)
    d.ellipse((515,310,625,410),fill=WHITE,outline=(220,224,230),width=3)

def text_field(d):
    d.text((250,240),"Email address",font=F22,fill=MUTED)
    box(d,(245,285,715,400),14,WHITE,BORDER,4)
    d.text((275,317),"name@example.com",font=F28,fill=MUTED)

def password(d):
    d.text((250,240),"Password",font=F22,fill=MUTED)
    box(d,(245,285,715,400),14,WHITE,BORDER,4)
    d.text((275,315),"••••••••",font=F36,fill=TEXT)

def textarea(d):
    d.text((240,190),"Message",font=F22,fill=MUTED)
    box(d,(235,235,725,485),14,WHITE,BORDER,4)
    for i,t in enumerate(["Write a longer message here.","This field can contain","several lines of text."]):
        d.text((270,275+i*55),t,font=F28,fill=MUTED)

def dropdown(d):
    d.text((245,230),"Choose a country",font=F22,fill=MUTED)
    box(d,(240,275,720,405),14,WHITE,BORDER,4)
    d.text((275,314),"United Kingdom",font=F28,fill=TEXT)
    chevron(d,675,340)

def listbox(d):
    box(d,(300,175,660,525),12,WHITE,BORDER,4)
    for i,t in enumerate(["Apple","Banana","Cherry","Orange","Pear"]):
        y=205+i*62
        if i==2:d.rectangle((315,y-8,645,y+42),fill=ACCENT_LIGHT)
        d.text((340,y),t,font=F28,fill=TEXT)

def slider(d):
    d.rounded_rectangle((220,335,740,365),radius=15,fill=(215,220,228))
    d.rounded_rectangle((220,335,500,365),radius=15,fill=ACCENT)
    d.ellipse((470,305,530,395),fill=WHITE,outline=ACCENT,width=6)

def progress(d):
    d.text((250,255),"Uploading…",font=F28,fill=TEXT)
    d.rounded_rectangle((245,330,715,390),radius=30,fill=(220,224,230))
    d.rounded_rectangle((245,330,555,390),radius=30,fill=ACCENT)
    d.text((610,338),"66%",font=F22,fill=MUTED)

def scrollbar(d):
    box(d,(300,150,660,550),16,(249,250,252),BORDER,3)
    for y in range(190,510,45):d.line((335,y,590,y),fill=(210,214,220),width=4)
    d.rounded_rectangle((620,170,645,530),radius=12,fill=(226,229,234))
    d.rounded_rectangle((618,245,647,365),radius=14,fill=MUTED)

def tabs(d):
    labels=["Overview","Settings","History"]
    x=220
    for i,t in enumerate(labels):
        if i==0:
            box(d,(x,245,x+175,335),18,WHITE,ACCENT,4)
            center(d,(x,245,x+175,330),t,F28,ACCENT)
        else:center(d,(x,245,x+175,330),t,F28,MUTED)
        x+=175
    d.line((220,335,745,335),fill=ACCENT,width=4)
    d.text((250,390),"Selected tab content",font=F28,fill=TEXT)

def tooltip(d):
    box(d,(250,310,440,410),18,ACCENT,(45,92,170),3)
    center(d,(250,310,440,410),"Hover here",F28,WHITE)
    box(d,(470,205,725,320),14,(40,45,55),(40,45,55),1)
    d.polygon([(500,320),(525,350),(545,320)],fill=(40,45,55))
    center(d,(470,205,725,320),"Helpful information",F22,WHITE)

def breadcrumb(d):
    labels=["Home","Library","Animals","Cats"]; x=160
    for i,t in enumerate(labels):
        d.text((x,330),t,font=F28,fill=ACCENT if i<3 else TEXT)
        b=d.textbbox((x,330),t,font=F28); x=b[2]+24
        if i<3: chevron(d,x,350,"right"); x+=28

def search(d):
    box(d,(220,290,740,420),28,WHITE,BORDER,4)
    d.ellipse((265,320,310,365),outline=MUTED,width=5)
    d.line((302,357,330,385),fill=MUTED,width=5)
    d.text((350,325),"Search…",font=F28,fill=MUTED)

def datepicker(d):
    box(d,(245,285,715,410),14,WHITE,BORDER,4)
    d.text((280,322),"20 July 2026",font=F28,fill=TEXT)
    d.rectangle((620,315,670,365),outline=ACCENT,width=4)
    d.line((620,330,670,330),fill=ACCENT,width=4)

def colorpicker(d):
    box(d,(250,240,710,470),18,WHITE,BORDER,4)
    colors=[RED,(218,150,45),GREEN,ACCENT,(135,87,190),(245,116,173)]
    for i,c in enumerate(colors):
        x=285+i*70; d.ellipse((x,285,x+60,345),fill=c,outline=TEXT,width=2)
    d.text((290,395),"#4A7ACF",font=F28,fill=TEXT)
    d.rectangle((510,385,650,435),fill=ACCENT,outline=TEXT,width=3)

def spinner(d):
    box(d,(320,275,640,425),14,WHITE,BORDER,4)
    d.text((355,315),"5",font=F36,fill=TEXT)
    d.line((530,275,530,425),fill=BORDER,width=3)
    chevron(d,585,322,"up"); chevron(d,585,380,"down")

def menubar(d):
    box(d,(160,240,800,470),14,(248,249,251),BORDER,4)
    d.rectangle((160,240,800,310),fill=(226,229,235))
    for i,t in enumerate(["File","Edit","View","Help"]):
        d.text((200+i*120,260),t,font=F22,fill=TEXT)
    d.text((210,355),"Document content",font=F28,fill=MUTED)

def contextmenu(d):
    box(d,(335,165,625,535),14,WHITE,BORDER,4)
    for i,t in enumerate(["Cut","Copy","Paste","Rename","Delete"]):
        y=205+i*62
        if i==1:d.rectangle((350,y-8,610,y+38),fill=ACCENT_LIGHT)
        d.text((380,y),t,font=F28,fill=RED if t=="Delete" else TEXT)

def modal(d):
    d.rectangle((100,90,860,630),fill=(220,223,228))
    box(d,(215,180,745,525),24,WHITE,BORDER,4)
    d.text((260,220),"Delete this item?",font=F36,fill=TEXT)
    d.text((260,305),"This action cannot be undone.",font=F28,fill=MUTED)
    box(d,(285,410,465,475),16,WHITE,BORDER,3); center(d,(285,410,465,475),"Cancel",F22,TEXT)
    box(d,(495,410,675,475),16,RED,(155,50,50),3); center(d,(495,410,675,475),"Delete",F22,WHITE)

def notification(d):
    box(d,(235,250,725,455),22,WHITE,BORDER,4)
    d.ellipse((270,300,340,370),fill=GREEN)
    d.line([(285,335),(302,352),(326,315)],fill=WHITE,width=7,joint="curve")
    d.text((375,285),"Upload complete",font=F28,fill=TEXT)
    d.text((375,340),"Your file is ready.",font=F22,fill=MUTED)

def pagination(d):
    x=230
    for t in ["‹","1","2","3","4","›"]:
        active=t=="2"; box(d,(x,305,x+78,395),14,ACCENT if active else WHITE,ACCENT if active else BORDER,3)
        center(d,(x,305,x+78,395),t,F28,WHITE if active else TEXT); x+=90

def accordion(d):
    y=190
    for label,opened in [("Account settings",False),("Privacy options",True),("Notifications",False)]:
        box(d,(220,y,740,y+82),12,(249,250,252),BORDER,3)
        d.text((255,y+24),label,font=F28,fill=TEXT); chevron(d,695,y+41,"up" if opened else "down")
        y+=90
        if opened:
            box(d,(220,y-8,740,y+100),12,WHITE,BORDER,3)
            d.text((255,y+22),"Expanded section content appears here.",font=F22,fill=MUTED); y+=118

def treeview(d):
    box(d,(265,145,695,555),14,WHITE,BORDER,4)
    rows=[(0,"▼ Documents"),(1,"▶ Reports"),(1,"▼ Projects"),(2,"• Garden App"),(2,"• Learning Packs"),(0,"▶ Pictures")]
    for i,(depth,t) in enumerate(rows):
        d.text((300+depth*38,185+i*58),t,font=F28,fill=TEXT)

def filepicker(d):
    d.text((235,240),"Choose a file",font=F22,fill=MUTED)
    box(d,(230,285,730,410),14,WHITE,BORDER,4)
    d.text((260,325),"No file selected",font=F28,fill=MUTED)
    box(d,(545,300,705,395),14,(236,238,242),BORDER,3)
    center(d,(545,300,705,395),"Browse…",F22,TEXT)

ELEMENTS = [
("button","Button",["a button","push button"],"Input Control",["Checkbox","Dropdown menu","Tab"],"A button performs an action when selected.",button),
("checkbox","Checkbox",["check box","tick box","tickbox"],"Selection Control",["Radio button","Toggle switch","Button"],"A checkbox independently switches an option on or off.",checkbox),
("radio_button","Radio button",["option button"],"Selection Control",["Checkbox","Toggle switch","Slider"],"Radio buttons usually select one option from a group.",radio),
("toggle_switch","Toggle switch",["switch","toggle"],"Selection Control",["Checkbox","Slider","Button"],"A toggle switch changes between two states.",toggle),
("text_field","Text field",["text box","input field","text input"],"Text Input",["Text area","Search box","Dropdown menu"],"A text field accepts one short line of text.",text_field),
("password_field","Password field",["password box","password input"],"Text Input",["Text field","Search box","Text area"],"A password field hides typed characters.",password),
("text_area","Text area",["multiline text field","multiline text box"],"Text Input",["Text field","List box","Modal dialog"],"A text area accepts several lines of text.",textarea),
("dropdown_menu","Dropdown menu",["drop-down menu","select menu","dropdown","combo box"],"Selection Control",["List box","Context menu","Accordion"],"A dropdown reveals a list of choices.",dropdown),
("list_box","List box",["selection list"],"Selection Control",["Dropdown menu","Tree view","Context menu"],"A list box displays selectable options.",listbox),
("slider","Slider",["range slider","range control"],"Input Control",["Progress bar","Scrollbar","Spinner"],"A slider selects a value along a range.",slider),
("progress_bar","Progress bar",["loading bar","progress indicator"],"Feedback",["Slider","Scrollbar","Notification"],"A progress bar shows task completion.",progress),
("scrollbar","Scrollbar",["scroll bar"],"Navigation",["Slider","Progress bar","Pagination"],"A scrollbar moves through longer content.",scrollbar),
("tab","Tab",["interface tab","navigation tab"],"Navigation",["Button","Breadcrumb","Accordion"],"A tab switches between related panels.",tabs),
("tooltip","Tooltip",["tool tip","hover tip"],"Feedback",["Notification","Modal dialog","Context menu"],"A tooltip briefly explains an element.",tooltip),
("breadcrumb","Breadcrumb",["breadcrumb trail","breadcrumbs"],"Navigation",["Pagination","Tab","Menu bar"],"A breadcrumb shows location in a hierarchy.",breadcrumb),
("search_box","Search box",["search field","search input"],"Text Input",["Text field","Password field","File picker"],"A search box accepts a search query.",search),
("date_picker","Date picker",["calendar picker","date selector"],"Input Control",["Colour picker","Dropdown menu","Spinner"],"A date picker selects a calendar date.",datepicker),
("colour_picker","Colour picker",["color picker","colour selector","color selector"],"Input Control",["Date picker","Slider","Dropdown menu"],"A colour picker selects a colour.",colorpicker),
("spinner","Spinner",["number spinner","numeric stepper","stepper"],"Input Control",["Slider","Dropdown menu","Scrollbar"],"A spinner adjusts a value with up and down controls.",spinner),
("menu_bar","Menu bar",["application menu","main menu"],"Navigation",["Toolbar","Context menu","Breadcrumb"],"A menu bar groups application commands.",menubar),
("context_menu","Context menu",["right-click menu","popup menu"],"Navigation",["Dropdown menu","Menu bar","List box"],"A context menu shows actions relevant to the current object.",contextmenu),
("modal_dialog","Modal dialog",["modal","dialog box","dialog"],"Container",["Notification","Tooltip","Accordion"],"A modal dialog requires attention before returning to the main interface.",modal),
("notification","Notification",["toast notification","toast","alert message"],"Feedback",["Tooltip","Modal dialog","Progress bar"],"A notification reports an event or status change.",notification),
("pagination","Pagination",["page navigation","pager"],"Navigation",["Breadcrumb","Scrollbar","Tab"],"Pagination divides content into numbered pages.",pagination),
("accordion","Accordion",["collapsible panel","expander"],"Container",["Tab","Dropdown menu","Tree view"],"An accordion expands and collapses sections.",accordion),
("tree_view","Tree view",["tree","hierarchical list"],"Navigation",["List box","Accordion","Breadcrumb"],"A tree view displays nested items.",treeview),
("file_picker","File picker",["file chooser","file selector","file browser"],"Input Control",["Search box","Text field","Date picker"],"A file picker lets the user choose a file.",filepicker),
]

def generate():
    if ROOT.exists(): shutil.rmtree(ROOT)
    IMG_DIR.mkdir(parents=True)

    items=[]
    for item_id,answer,accepted,category,distractors,explanation,painter in ELEMENTS:
        im,d=canvas(); painter(d)
        image_rel=f"assets/images/{item_id}.png"
        im.save(ROOT/image_rel,optimize=True)
        items.append({
            "item_id":item_id,
            "question":{
                "text":"What is this UI element called?",
                "image":image_rel,
                "category":category,
                "credit":{
                    "creator":"Generated by generate_ui_elements_pack.py",
                    "source":"Original simplified interface illustration",
                    "license":"CC0 1.0"
                }
            },
            "answer":{
                "text":answer,
                "accepted_answers":accepted,
                "comparison":{"ignore_case":True,"ignore_accents":True,"ignore_punctuation":True}
            },
            "distractors":distractors,
            "explanation":{"text":explanation},
            "tags":["user interface","ui element",category.lower()]
        })

    pack={
        "schema_version":"1.0",
        "pack_id":PACK_ID,
        "title":"UI Elements",
        "subtitle":"Recognise common interface controls",
        "description":"A visual identification pack covering common interface components.",
        "author":"Knowledge in Bloom",
        "version":"1.0.0",
        "language":"en-GB",
        "icon":"icon.png",
        "item_files":["items.json"],
        "item_order":"defined",
        "default_round_size":10,
        "capabilities":{"multiple_choice":True,"typed_answer":True,"categorize":True,"media_only":True},
        "reversible":False,
        "tags":["user interface","ui","computing","digital literacy","design","beginner"],
        "suggested_follow_up_packs":["web_design","html_elements"],
        "license":{"name":"CC0 1.0","url":"https://creativecommons.org/publicdomain/zero/1.0/"},
        "credits":[{"name":"Knowledge in Bloom UI pack generator","role":"Question data and illustrations","license":"CC0 1.0"}]
    }

    (ROOT/"pack.json").write_text(json.dumps(pack,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (ROOT/"items.json").write_text(json.dumps(items,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

    src=Path.cwd()/"icon.png"
    if src.exists(): shutil.copy2(src,ROOT/"icon.png")

    warnings=[]
    ids=[x["item_id"] for x in items]
    if len(ids)!=len(set(ids)): warnings.append("Duplicate item IDs")
    for item in items:
        if not (ROOT/item["question"]["image"]).exists(): warnings.append(f"Missing image: {item['item_id']}")
    if not (ROOT/"icon.png").exists(): warnings.append("icon.png not found; copy your existing icon into the generated folder.")

    report=[
        "Knowledge in Bloom pack validation",
        "==================================",
        f"Pack ID: {PACK_ID}",
        f"Items: {len(items)}",
        f"Images: {len(list(IMG_DIR.glob('*.png')))}",
        f"Unique item IDs: {len(set(ids))}",
        "",
        "Result: PASS" if not warnings else "Result: PASS WITH WARNINGS",
        *[f"- {w}" for w in warnings]
    ]
    (ROOT/"validation_report.txt").write_text("\n".join(report)+"\n",encoding="utf-8")

    readme=f"""# UI Elements pack

Generated with Pillow by generate_ui_elements_pack.py.

Items: {len(items)}

Place your existing icon.png beside the generator before running, or copy it into
the generated ui_elements folder afterwards.

Run:
    python3 generate_ui_elements_pack.py

Install Pillow if required:
    python3 -m pip install Pillow
"""
    (ROOT/"README.md").write_text(readme,encoding="utf-8")

    if ZIP_PATH.exists(): ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH,"w",zipfile.ZIP_DEFLATED) as z:
        for p in sorted(ROOT.rglob("*")):
            if p.is_file(): z.write(p,p.relative_to(ROOT.parent))

    print(f"Created {ROOT}")
    print(f"Created {ZIP_PATH}")
    print(f"Generated {len(items)} UI element questions.")
    if warnings:
        print("\nWarnings:")
        for w in warnings: print(f"- {w}")

if __name__=="__main__":
    try:
        generate()
    except ModuleNotFoundError:
        print("Pillow is required. Install it with: python3 -m pip install Pillow",file=sys.stderr)
        raise SystemExit(1)
