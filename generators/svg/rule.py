from . import palette


def render(theme: str) -> str:
    fg, _ = palette(theme)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 14" width="1200" height="14" role="img" aria-label="divider">\n'
        f'  <line x1="0" y1="7" x2="1200" y2="7" stroke="{fg}" stroke-opacity=".14" stroke-width="1"/>\n'
        f'  <circle cx="600" cy="7" r="2" fill="{fg}" fill-opacity=".28"/>\n'
        f'  <line x1="560" y1="7" x2="592" y2="7" stroke="{fg}" stroke-opacity=".28" stroke-width="1"/>\n'
        f'  <line x1="608" y1="7" x2="640" y2="7" stroke="{fg}" stroke-opacity=".28" stroke-width="1"/>\n'
        '</svg>\n'
    )
