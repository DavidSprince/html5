"""Icon helper — loads lucide-static SVGs and exposes them as inline markup
so the generated HTML has zero external icon requests (matches the React
app's use of lucide-react, one-to-one on icon names)."""
import re
from pathlib import Path
from markupsafe import Markup

ICONS_DIR = Path(__file__).parent.parent.parent / "lucide-static-icons" / "icons"

_cache = {}


def _to_kebab(name: str) -> str:
    # PascalCase -> kebab-case (e.g. "HeartPulse" -> "heart-pulse", "Grid3x3" -> "grid-3x3")
    s = re.sub(r'(?<!^)(?=[A-Z])', '-', name)
    return s.lower().replace('--', '-')

# Manual overrides for names that don't map cleanly via the regex above
OVERRIDES = {
    "Grid3x3": "grid-3x3",
    "SquarePlay": "square-play",
    "CheckCircle2": "check-circle-2",
    "ListChecks": "list-checks",
    "HelpCircle": "help-circle",
    "ExternalLink": "external-link",
    "ChevronRight": "chevron-right",
    "TrendingUp": "trending-up",
    "GraduationCap": "graduation-cap",
    "FileSpreadsheet": "file-spreadsheet",
    "LayoutTemplate": "layout-template",
    "LineChart": "line-chart",
    "MessageSquare": "message-square",
    "PenTool": "pen-tool",
    "HeartPulse": "heart-pulse",
    "Wand2": "wand-2",
    "IdCard": "id-card",
    "BookOpen": "book-open",
}


def icon_svg(name: str, css_class: str = "", stroke_width: str = None) -> str:
    """Return inline SVG markup for a lucide icon name (PascalCase)."""
    key = OVERRIDES.get(name, _to_kebab(name))
    if key not in _cache:
        path = ICONS_DIR / f"{key}.svg"
        if not path.exists():
            path = ICONS_DIR / "sparkles.svg"  # fallback
        _cache[key] = path.read_text()
    svg = _cache[key]
    # strip the license comment line
    svg = re.sub(r'<!--.*?-->\s*', '', svg, count=1, flags=re.S)
    # inject/replace class attribute
    if css_class:
        if 'class="' in svg:
            svg = re.sub(r'class="[^"]*"', f'class="{css_class}"', svg, count=1)
        else:
            svg = svg.replace('<svg', f'<svg class="{css_class}"', 1)
    if stroke_width:
        svg = re.sub(r'stroke-width="[^"]*"', f'stroke-width="{stroke_width}"', svg, count=1)
    return Markup(svg)
