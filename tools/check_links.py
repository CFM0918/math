from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
IGNORED_PREFIXES = (
    "#",
    "mailto:",
    "tel:",
    "javascript:",
    "data:",
    "http://",
    "https://",
)


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.pending: list[str] = []
        self.title_parts: list[str] = []
        self.visible_parts: list[str] = []
        self._in_title = False
        self._hidden_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        for key in ("href", "src"):
            value = values.get(key)
            if value is not None:
                self.links.append(value)
        pending = values.get("data-missing")
        if pending:
            self.pending.append(pending)
        if tag == "title":
            self._in_title = True
        if tag in {"script", "style", "template"}:
            self._hidden_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag in {"script", "style", "template"} and self._hidden_depth:
            self._hidden_depth -= 1

    def handle_data(self, data: str) -> None:
        text = " ".join(data.split())
        if not text:
            return
        if self._in_title:
            self.title_parts.append(text)
        if not self._hidden_depth:
            self.visible_parts.append(text)


def resolve_local(page: Path, raw: str) -> Path | None:
    if not raw or raw.startswith(IGNORED_PREFIXES):
        return None
    path = unquote(urlparse(raw).path)
    if not path:
        return None
    if path.startswith("/math/"):
        target = ROOT / path[len("/math/") :]
    elif path == "/math":
        target = ROOT
    elif path.startswith("/"):
        return None
    else:
        target = (page.parent / path).resolve()
    if raw.endswith("/") or target.is_dir():
        target /= "index.html"
    return target


def has_exact_case(target: Path) -> bool:
    """Emulate GitHub Pages' case-sensitive paths while running on Windows."""
    try:
        relative = target.resolve().relative_to(ROOT.resolve())
    except ValueError:
        return False
    current = ROOT.resolve()
    for part in relative.parts:
        try:
            names = {child.name for child in current.iterdir()}
        except OSError:
            return False
        if part not in names:
            return False
        current /= part
    return True


errors: list[str] = []
pending_materials: list[str] = []
linked_course_pages: set[Path] = set()
checked = 0

for html in sorted(ROOT.rglob("*.html")):
    relative = html.relative_to(ROOT)
    try:
        source = html.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"{relative}：無法以 UTF-8 讀取（{exc}）")
        continue

    if "\ufffd" in source:
        errors.append(f"{relative}：包含無法辨識的字元（�）")

    parser = PageParser()
    try:
        parser.feed(source)
    except Exception as exc:
        errors.append(f"{relative}：HTML 無法解析（{exc}）")
        continue

    if not "".join(parser.title_parts).strip():
        errors.append(f"{relative}：缺少頁面標題")
    if len(" ".join(parser.visible_parts)) < 80:
        errors.append(f"{relative}：可見內容過少，可能是空白頁")

    for raw in parser.links:
        target = resolve_local(html, raw)
        if target is None:
            continue
        checked += 1
        if not target.exists():
            errors.append(f"{relative} -> {raw}")
        elif not has_exact_case(target):
            errors.append(f"{relative} -> {raw}（大小寫與實際檔名不一致）")
        elif relative.name == "index.html" and "courses" in target.parts:
            linked_course_pages.add(target.resolve())

    for raw in parser.pending:
        target = resolve_local(html, raw)
        if target is None:
            errors.append(f"{relative}：data-missing 不是有效的本機路徑（{raw}）")
        elif target.exists():
            errors.append(f"{relative}：已存在的教材仍被標成待補（{raw}）")
        else:
            pending_materials.append(f"{relative} -> {raw}")

course_pages = {
    page.resolve()
    for page in ROOT.glob("grades/grade*/semester*/courses/*/*.html")
    if page.name in {"interactive.html", "slides.html"}
}
for orphan in sorted(course_pages - linked_course_pages):
    errors.append(f"{orphan.relative_to(ROOT)}：教材存在，但學期首頁沒有連結")

print(f"已檢查 {checked} 個本機連結與 {len(course_pages)} 個教材頁面。")
if pending_materials:
    print(f"\n明確標示待補教材：{len(pending_materials)} 項")
    for item in pending_materials:
        print(" -", item)

if errors:
    print("\n發現需要修正的項目：")
    for item in errors:
        print(" -", item)
    raise SystemExit(1)

print("\n檢查通過：沒有空白頁、失效本機連結或未列入導覽的教材。")
