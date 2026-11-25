#!/usr/bin/env python3
"""Build the editable team 1 presentation using only Python's standard library."""

from html import escape
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

OUT = Path(__file__).with_name("presentation_team1.pptx")
EMU = 914400
W, H = 12192000, 6858000

BG = "0C1220"
PANEL = "141E31"
PANEL2 = "1B2941"
INK = "F1F5FB"
MUTED = "A9B7CB"
CYAN = "62D5E8"
LIME = "B8E986"
ORANGE = "FFC778"
LINE = "34445E"
FONT = "Aptos"


def emu(inches):
    return round(inches * EMU)


class Slide:
    def __init__(self):
        self.parts = []
        self.shape_id = 2

    def rect(self, x, y, w, h, fill=PANEL, line=LINE, radius=True):
        sid = self.shape_id
        self.shape_id += 1
        geom = "roundRect" if radius else "rect"
        stroke = "<a:noFill/>" if line is None else f'<a:solidFill><a:srgbClr val="{line}"/></a:solidFill>'
        self.parts.append(
            f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="Shape {sid}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>'
            f'<a:prstGeom prst="{geom}"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>'
            f'<a:ln w="12700">{stroke}</a:ln></p:spPr></p:sp>'
        )

    def text(self, x, y, w, h, text, size=18, color=INK, bold=False, align="l", valign="t", margin=0.02):
        sid = self.shape_id
        self.shape_id += 1
        paras = []
        for line in str(text).split("\n"):
            paras.append(
                f'<a:p><a:pPr algn="{align}"><a:lnSpc><a:spcPct val="106000"/></a:lnSpc>'
                f'<a:spcAft><a:spcPts val="450"/></a:spcAft></a:pPr>'
                f'<a:r><a:rPr lang="ru-RU" sz="{round(size * 100)}" b="{1 if bold else 0}" dirty="0">'
                f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
                f'<a:latin typeface="{FONT}"/><a:ea typeface="{FONT}"/><a:cs typeface="{FONT}"/>'
                f'</a:rPr><a:t xml:space="preserve">{escape(line)}</a:t></a:r>'
                f'<a:endParaRPr lang="ru-RU" sz="{round(size * 100)}"/></a:p>'
            )
        self.parts.append(
            f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="Text {sid}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr>'
            f'<p:txBody><a:bodyPr wrap="square" lIns="{emu(margin)}" rIns="{emu(margin)}" '
            f'tIns="{emu(margin)}" bIns="{emu(margin)}" anchor="{valign}"><a:noAutofit/></a:bodyPr>'
            f'<a:lstStyle/>{"".join(paras)}</p:txBody></p:sp>'
        )

    def rule(self, x, y, w, color=LINE, thickness=0.018):
        self.rect(x, y, w, thickness, fill=color, line=None, radius=False)

    def bullet(self, x, y, w, text, size=19, color=INK):
        self.text(x, y, 0.25, 0.38, "•", size=size + 1, color=CYAN, bold=True)
        self.text(x + 0.28, y, w - 0.28, 0.55, text, size=size, color=color)


def slide_xml(slide):
    tree = (
        '<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
        '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
        '<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
        + "".join(slide.parts)
        + "</p:spTree>"
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
        f'<p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="{BG}"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>'
        f'{tree}</p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'
    )


def add_header(s, kicker, title, page):
    s.text(0.75, 0.42, 11.9, 0.32, kicker.upper(), size=10.5, color=CYAN, bold=True)
    s.text(0.75, 0.82, 12.0, 0.72, title, size=29, color=INK, bold=True)
    s.rule(0.75, 1.58, 11.85, color=LINE, thickness=0.012)
    s.text(0.75, 7.13, 7.0, 0.18, "КОМАНДА 1 · 2-3 ДЕРЕВО", size=8.5, color=MUTED)
    s.text(11.5, 7.13, 0.65, 0.18, f"{page:02d} / 07", size=8.5, color=MUTED, align="r")


def build_slides():
    slides = []

    # 1 — cover
    s = Slide()
    s.text(0.9, 0.78, 11.3, 0.35, "СЕМИНАР · ТЕСТИРОВАНИЕ ДЕРЕВЬЕВ", size=12, color=CYAN, bold=True)
    s.text(0.85, 1.55, 11.8, 1.25, "2-3 дерево", size=50, color=INK, bold=True)
    s.text(0.9, 2.82, 11.2, 0.65, "Команда 1 · сравнение с B+ деревом порядка t = 3 команды 4", size=21, color=MUTED)
    stats = [(0.85, "10 000", "операций на набор"), (4.82, "3", "набора из семинара 11"), (8.79, "O(log n)", "высота и операции")]
    for x, value, label in stats:
        s.rect(x, 4.25, 3.65, 1.42, PANEL, LINE)
        s.text(x + 0.2, 4.48, 3.25, 0.55, value, size=27, color=LIME, bold=True)
        s.text(x + 0.2, 5.1, 3.25, 0.35, label, size=13, color=MUTED)
    s.text(0.9, 7.13, 8.0, 0.18, "КОМАНДА 1 · ТЕСТИРОВАНИЕ 2-3 И B-ДЕРЕВЬЕВ", size=8.5, color=MUTED)
    s.text(11.5, 7.13, 0.65, 0.18, "01 / 07", size=8.5, color=MUTED, align="r")
    slides.append(s)

    # 2 — structure
    s = Slide()
    add_header(s, "Структура", "Узел хранит 1–2 ключа", 2)
    bullets = [
        "У внутреннего узла от 2 до 3 детей.",
        "Все листья расположены на одной глубине.",
        "При переполнении средний ключ поднимается к родителю.",
        "При удалении узел занимает ключ у соседа или сливается с ним.",
    ]
    for i, line in enumerate(bullets):
        s.bullet(0.9, 1.95 + i * 0.72, 5.5, line, size=16.5)
    # Tree illustration: root with two separators and three leaves.
    s.rect(8.3, 2.05, 2.35, 0.68, PANEL2, CYAN)
    s.text(8.42, 2.18, 2.1, 0.35, "20  |  40", size=18, color=CYAN, bold=True, align="ctr", valign="ctr")
    s.rect(9.45, 2.74, 0.025, 0.45, LINE, None, False)
    s.rule(7.12, 3.18, 4.7, LINE, 0.025)
    for cx in [7.12, 9.45, 11.8]:
        s.rect(cx, 3.18, 0.025, 0.38, LINE, None, False)
    for x, text in [(6.45, "4 · 9"), (8.75, "24 · 31"), (11.12, "42 · 57")]:
        s.rect(x, 3.57, 1.55, 0.62, "1B2B28", "7DA860")
        s.text(x + 0.1, 3.72, 1.35, 0.28, text, size=14, color=LIME, bold=True, align="ctr", valign="ctr")
    s.text(6.55, 4.35, 6.4, 0.35, "< 20     ·     между 20 и 40     ·     > 40", size=12, color=MUTED, align="ctr")
    s.rect(0.85, 5.55, 11.55, 0.88, "30291E", ORANGE)
    s.text(1.08, 5.72, 11.1, 0.56, "Уточнение: формула 2t−1 при t=2 даёт 3 ключа (2-3-4 дерево). Здесь реализовано классическое 2-3 дерево: максимум 2 ключа.", size=13, color="FFE1B6")
    slides.append(s)

    # 3 — workloads
    s = Slide()
    add_header(s, "Наборы и методика", "Три набора, по 10 000 значений", 3)
    cards = [
        (0.85, "RANDOM", "rand() % 100000", "Повторы возможны"),
        (4.82, "SORTED", "1 … 10 000", "Строго возрастающий порядок"),
        (8.79, "HOTSPOT", "5 000 × 42, затем 5 000 случайных", "Много повторов ключа 42"),
    ]
    for x, title, value, sub in cards:
        s.rect(x, 2.0, 3.65, 1.82, PANEL, LINE)
        s.text(x + 0.2, 2.22, 3.25, 0.32, title, size=12, color=CYAN, bold=True)
        s.text(x + 0.2, 2.72, 3.25, 0.58, value, size=18 if title != "HOTSPOT" else 15, color=INK, bold=True)
        s.text(x + 0.2, 3.4, 3.25, 0.28, sub, size=11.5, color=MUTED)
    s.rect(0.85, 4.32, 5.55, 1.35, PANEL2, LINE)
    s.text(1.08, 4.55, 5.1, 0.85, "Генератор: srand(1).\nПовторные вставки не создают дубликаты.", size=15, color=INK)
    s.rect(6.72, 4.32, 5.72, 1.35, PANEL2, LINE)
    s.text(6.96, 4.55, 5.24, 0.85, "Время — медиана 7 запусков с -O2.\nПоиск и удаление по исходным значениям.", size=15, color=INK)
    s.text(0.92, 6.24, 11.3, 0.42, "Время указано как медиана семи запусков; тайминги зависят от компьютера.", size=12, color=MUTED)
    slides.append(s)

    # 4 — result table
    s = Slide()
    add_header(s, "Измеренные результаты · команда 1", "Высота осталась небольшой", 4)
    headers = ["Набор", "Уникальные", "Высота", "Расщепления", "Слияния", "Перераспр.", "Вставка, мс", "Поиск, мс", "Удаление, мс"]
    rows = [
        ["Random", "9 511", "11", "7 080", "7 080", "3 052", "0.957", "0.683", "1.006"],
        ["Sorted", "10 000", "13", "9 982", "9 982", "5", "0.784", "0.420", "0.458"],
        ["Hotspot", "4 879", "10", "3 610", "3 610", "1 557", "0.445", "0.328", "0.563"],
    ]
    widths = [1.1, 1.05, 0.72, 1.17, 1.0, 1.12, 1.1, 0.95, 1.15]
    total = sum(widths)
    scale = 11.95 / total
    widths = [v * scale for v in widths]
    x0, y0, rh = 0.68, 2.15, 0.68
    x = x0
    for j, title in enumerate(headers):
        s.rect(x, y0, widths[j], rh, PANEL2, LINE, False)
        s.text(x + 0.03, y0 + 0.12, widths[j] - 0.06, 0.44, title, size=9.2, color=CYAN, bold=True, align="ctr", valign="ctr", margin=0)
        x += widths[j]
    for i, row in enumerate(rows):
        x = x0
        y = y0 + (i + 1) * rh
        for j, value in enumerate(row):
            s.rect(x, y, widths[j], rh, PANEL if i % 2 == 0 else "10192A", LINE, False)
            s.text(x + 0.03, y + 0.12, widths[j] - 0.06, 0.44, value, size=11, color=INK, bold=(j == 0), align="ctr", valign="ctr", margin=0)
            x += widths[j]
    s.rect(0.8, 5.45, 11.72, 0.86, PANEL, LINE)
    s.text(1.04, 5.62, 11.2, 0.52, "Узлов после вставки: Random 7 091  ·  Sorted 9 995  ·  Hotspot 3 620\nСамопроверка пройдена: 30 000 случайных операций, сравнение с std::set.", size=12.5, color=MUTED)
    slides.append(s)

    # 5 — observations
    s = Slide()
    add_header(s, "Наблюдения", "Порядок входа меняет работу узлов", 5)
    obs = [
        (0.85, 2.0, "13 уровней", "Sorted не превратил дерево в цепочку: баланс сохраняется на возрастающем входе."),
        (6.72, 2.0, "9 982", "Расщепления на Sorted — максимум: правый край постоянно принимает новые ключи."),
        (0.85, 4.0, "4 879", "Уникальных ключей в Hotspot: повторы 42 и случайные совпадения не добавляют узлы."),
        (6.72, 4.0, "O(log n)", "Вставка, поиск и удаление. Полный обход — O(n), память — O(n)."),
    ]
    for x, y, value, explanation in obs:
        s.rect(x, y, 5.55, 1.55, PANEL, LINE)
        s.text(x + 0.22, y + 0.2, 5.08, 0.47, value, size=24, color=LIME, bold=True)
        s.text(x + 0.22, y + 0.78, 5.08, 0.58, explanation, size=12.5, color=INK)
    s.text(0.9, 6.05, 11.4, 0.55, "Заимствование у соседа даёт перераспределение; если сосед не может отдать ключ, происходит слияние.", size=13, color=MUTED)
    slides.append(s)

    # 6 — paired comparison
    s = Slide()
    add_header(s, "Пара защиты · команда 4", "2-3 дерево и B+ дерево", 6)
    rows = [
        ("Свойство", "2-3 дерево · команда 1", "B+ · команда 4, t=3"),
        ("Ключи данных", "Во внутренних узлах и листьях", "Только в листьях; внутри — разделители"),
        ("Максимум детей", "3", "6 по шаблону задания"),
        ("Поиск", "Может завершиться внутри", "Всегда доходит до листа"),
        ("Диапазоны", "Обход дерева", "Связанные листья удобны для сканирования"),
        ("Высота на тестах", "11–13 уровней", "Обычно ниже за счёт большего ветвления"),
    ]
    cols = [2.25, 4.55, 4.85]
    x0, y0, row_h = 0.85, 1.92, 0.68
    for i, row in enumerate(rows):
        x = x0
        for j, value in enumerate(row):
            fill = PANEL2 if i == 0 else (PANEL if i % 2 else "10192A")
            col = CYAN if i == 0 else INK
            s.rect(x, y0 + i * row_h, cols[j], row_h, fill, LINE, False)
            s.text(x + 0.1, y0 + i * row_h + 0.1, cols[j] - 0.2, 0.48, value, size=12 if j else 11.5, color=col, bold=(i == 0 or j == 0), valign="ctr")
            x += cols[j]
    s.rect(0.85, 6.27, 11.65, 0.55, "30291E", ORANGE)
    s.text(1.04, 6.36, 11.27, 0.35, "Связанные листья B+ дерева упрощают последовательный проход по диапазону после поиска первого ключа.", size=11.2, color="FFE1B6", valign="ctr")
    slides.append(s)

    # 7 — conclusion
    s = Slide()
    add_header(s, "Итог", "Выбираем по типу запросов", 7)
    s.rect(0.85, 2.0, 5.55, 2.35, PANEL, LINE)
    s.text(1.12, 2.24, 5.05, 0.42, "2-3 ДЕРЕВО", size=16, color=CYAN, bold=True)
    for i, line in enumerate(["Простая сбалансированная структура.", "Точечный поиск и обновление — O(log n).", "Удобно объяснять разделение и слияние узлов."]):
        s.bullet(1.12, 2.9 + i * 0.46, 4.95, line, size=12.5)
    s.rect(6.72, 2.0, 5.72, 2.35, PANEL, LINE)
    s.text(6.99, 2.24, 5.18, 0.42, "B+ ДЕРЕВО", size=16, color=LIME, bold=True)
    for i, line in enumerate(["Большее ветвление уменьшает высоту.", "Связанные листья ускоряют диапазонное чтение.", "Подходит для индексов и последовательного сканирования."]):
        s.bullet(6.99, 2.9 + i * 0.46, 5.1, line, size=12.5)
    s.rect(0.85, 4.88, 11.59, 0.95, PANEL2, LINE)
    s.text(1.12, 5.08, 11.05, 0.55, "Обе структуры сбалансированы: операции имеют логарифмическую оценку. Нагрузка на диапазонные запросы склоняет выбор к B+.", size=16, color=INK, bold=True, valign="ctr")
    s.text(0.9, 6.3, 11.5, 0.42, "Код: team1_23_tree.cpp  ·  Отчёт: report_team1.md", size=11, color=MUTED)
    s.text(0.9, 7.13, 8.0, 0.18, "СПАСИБО", size=8.5, color=MUTED)
    s.text(11.5, 7.13, 0.65, 0.18, "07 / 07", size=8.5, color=MUTED, align="r")
    slides.append(s)

    return slides


def empty_tree():
    return (
        '<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
        '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree>'
    )


def package_parts(slides):
    parts = {}
    slide_overrides = "".join(f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>' for i in range(1, len(slides) + 1))
    parts["[Content_Types].xml"] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>'
        '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>'
        '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>'
        '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>'
        + slide_overrides
        + '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
        '</Types>'
    )
    parts["_rels/.rels"] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
        '</Relationships>'
    )
    slide_ids = "".join(f'<p:sldId id="{255+i}" r:id="rId{i+1}"/>' for i in range(1, len(slides) + 1))
    parts["ppt/presentation.xml"] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
        '<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>'
        f'<p:sldIdLst>{slide_ids}</p:sldIdLst><p:sldSz cx="{W}" cy="{H}" type="wide"/>'
        '<p:notesSz cx="6858000" cy="9144000"/><p:defaultTextStyle/></p:presentation>'
    )
    pres_rels = '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>'
    for i in range(1, len(slides) + 1):
        pres_rels += f'<Relationship Id="rId{i+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>'
    parts["ppt/_rels/presentation.xml.rels"] = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{pres_rels}</Relationships>'

    parts["ppt/slideMasters/slideMaster1.xml"] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
        f'<p:cSld name="Master">{empty_tree()}</p:cSld>'
        '<p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>'
        '<p:sldLayoutIdLst><p:sldLayoutId id="1" r:id="rId1"/></p:sldLayoutIdLst>'
        '<p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>'
    )
    parts["ppt/slideMasters/_rels/slideMaster1.xml.rels"] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>'
        '</Relationships>'
    )
    parts["ppt/slideLayouts/slideLayout1.xml"] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1">'
        f'<p:cSld name="Blank">{empty_tree()}</p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>'
    )
    parts["ppt/slideLayouts/_rels/slideLayout1.xml.rels"] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>'
        '</Relationships>'
    )
    parts["ppt/theme/theme1.xml"] = theme_xml()

    for i, slide in enumerate(slides, 1):
        parts[f"ppt/slides/slide{i}.xml"] = slide_xml(slide)
        parts[f"ppt/slides/_rels/slide{i}.xml.rels"] = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
            '</Relationships>'
        )

    parts["docProps/core.xml"] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
        'xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        '<dc:title>Команда 1 — 2-3 дерево</dc:title><dc:subject>Тестирование 2-3 и B+ деревьев</dc:subject>'
        '<dc:creator>Команда 1</dc:creator></cp:coreProperties>'
    )
    parts["docProps/app.xml"] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
        'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
        '<Application>Microsoft PowerPoint</Application><PresentationFormat>On-screen Show (16:9)</PresentationFormat>'
        f'<Slides>{len(slides)}</Slides></Properties>'
    )
    return parts


def theme_xml():
    accents = [CYAN, LIME, ORANGE, "8297B2", "A98BEA", "F17E8A"]
    accent_xml = "".join(f'<a:accent{i+1}><a:srgbClr val="{c}"/></a:accent{i+1}>' for i, c in enumerate(accents))
    fills = ''.join(f'<a:solidFill><a:schemeClr val="accent{i}"/></a:solidFill>' for i in (1, 2, 3))
    lines = ''.join(f'<a:ln w="6350"><a:solidFill><a:schemeClr val="accent{i}"/></a:solidFill><a:prstDash val="solid"/></a:ln>' for i in (1, 2, 3))
    effects = '<a:effectStyle><a:effectLst/></a:effectStyle>' * 3
    bg_fills = '<a:solidFill><a:schemeClr val="lt1"/></a:solidFill><a:solidFill><a:schemeClr val="lt2"/></a:solidFill><a:solidFill><a:schemeClr val="dk1"/></a:solidFill>'
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Team 1">'
        '<a:themeElements><a:clrScheme name="Team 1">'
        '<a:dk1><a:srgbClr val="0C1220"/></a:dk1><a:lt1><a:srgbClr val="F1F5FB"/></a:lt1>'
        '<a:dk2><a:srgbClr val="141E31"/></a:dk2><a:lt2><a:srgbClr val="A9B7CB"/></a:lt2>'
        f'{accent_xml}<a:hlink><a:srgbClr val="62D5E8"/></a:hlink><a:folHlink><a:srgbClr val="A98BEA"/></a:folHlink>'
        '</a:clrScheme><a:fontScheme name="Team 1">'
        f'<a:majorFont><a:latin typeface="{FONT}"/><a:ea typeface="{FONT}"/><a:cs typeface="{FONT}"/></a:majorFont>'
        f'<a:minorFont><a:latin typeface="{FONT}"/><a:ea typeface="{FONT}"/><a:cs typeface="{FONT}"/></a:minorFont>'
        '</a:fontScheme><a:fmtScheme name="Team 1">'
        f'<a:fillStyleLst>{fills}</a:fillStyleLst><a:lnStyleLst>{lines}</a:lnStyleLst>'
        f'<a:effectStyleLst>{effects}</a:effectStyleLst><a:bgFillStyleLst>{bg_fills}</a:bgFillStyleLst>'
        '</a:fmtScheme></a:themeElements><a:objectDefaults/><a:extraClrSchemeLst/></a:theme>'
    )


def main():
    slides = build_slides()
    parts = package_parts(slides)
    with ZipFile(OUT, "w", ZIP_DEFLATED) as archive:
        for name, content in parts.items():
            archive.writestr(name, content.encode("utf-8"))
    print(f"Created {OUT} ({len(slides)} slides)")


if __name__ == "__main__":
    main()
