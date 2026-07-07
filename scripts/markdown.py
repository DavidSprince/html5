import re
from markupsafe import Markup, escape


def _inline(text: str) -> str:
    """Render **bold** spans; escape everything else first."""
    parts = re.split(r'(\*\*[^*]+\*\*)', text)
    out = []
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            out.append(f"<strong>{escape(part[2:-2])}</strong>")
        else:
            out.append(str(escape(part)))
    return ''.join(out)


def render_markdown(text: str) -> Markup:
    """Render the limited markdown subset used in generated content:
    **bold** spans and simple '- ' bullet lists, paragraphs separated by
    blank lines. Mirrors src/lib/markdown.jsx from the React app."""
    if not text:
        return Markup("")
    blocks = re.split(r'\n\n+', text.strip())
    html_parts = []
    for block in blocks:
        lines = [l for l in block.split('\n') if l.strip()]
        is_list = len(lines) > 0 and all(l.strip().startswith('- ') for l in lines)
        if is_list:
            items = ''.join(f"<li>{_inline(l.strip()[2:])}</li>" for l in lines)
            html_parts.append(f'<ul class="space-y-2 my-4">{items}</ul>')
        else:
            html_parts.append(f'<p class="mb-4 leading-relaxed">{_inline(block)}</p>')
    return Markup(''.join(html_parts))
