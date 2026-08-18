from . import palette

VIEW_W = 1200
VIEW_H = 330
CX = 600.0
CY = 165.0
CENTRE_R = 30
PULSE_R = 38


def _ring_path(idx: int, rx: int, ry: int) -> str:
    x0 = CX - rx
    return f'M {x0:.1f} {CY:.1f} a {rx} {ry} 0 1 0 {2 * rx} 0 a {rx} {ry} 0 1 0 {-2 * rx} 0'


RING_STROKE_OPACITIES = [".30", ".45", ".65"]


def render(theme: str, rings: list[dict], centre_label: str = "TVP") -> str:
    """Render the stack orbit diagram.

    rings: list of {"items": [labels], "rx": int, "ry": int, "duration": float}
    """
    fg, bg = palette(theme)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW_W} {VIEW_H}" '
        f'width="{VIEW_W}" height="{VIEW_H}" role="img" aria-label="Tools in orbit">\n'
    ]

    parts.append('  <g>\n    \n')
    ring_parts = []
    for idx, ring in enumerate(rings):
        rx, ry = ring["rx"], ring["ry"]
        opacity = RING_STROKE_OPACITIES[idx]
        ring_parts.append(
            f'<path id="o{idx}" d="{_ring_path(idx, rx, ry)}" fill="none" '
            f'stroke="{fg}" stroke-opacity="{opacity}" stroke-width="1"/>'
        )
    parts.append("    ".join(ring_parts) + "\n")
    parts.append('  </g>\n')

    parts.append(
        f'  <circle cx="{CX:.1f}" cy="{CY:.1f}" r="{CENTRE_R}" fill="{bg}"/>\n'
        f'  <circle cx="{CX:.1f}" cy="{CY:.1f}" r="{CENTRE_R}" fill="none" '
        f'stroke="{fg}" stroke-width="1.6" stroke-opacity=".85">\n'
        '    <animate attributeName="stroke-opacity" values=".85;.4;.85" dur="5.5s" repeatCount="indefinite"/>\n'
        '  </circle>\n'
        f'  <circle cx="{CX:.1f}" cy="{CY:.1f}" r="{PULSE_R}" fill="none" '
        f'stroke="{fg}" stroke-width="0.7" stroke-opacity=".25">\n'
        f'    <animate attributeName="r" values="{PULSE_R};{PULSE_R + 8};{PULSE_R}" dur="5.5s" repeatCount="indefinite"/>\n'
        '    <animate attributeName="stroke-opacity" values=".25;.04;.25" dur="5.5s" repeatCount="indefinite"/>\n'
        '  </circle>\n'
        f'  <text x="{CX:.1f}" y="{CY + 4:.1f}" text-anchor="middle" '
        'style="font:600 12px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;letter-spacing:2px" '
        f'fill="{fg}" fill-opacity=".55">{centre_label}</text>\n'
        '\n'
    )

    for idx, ring in enumerate(rings):
        items = ring["items"]
        dur = ring["duration"]
        step = dur / len(items)
        for j, label in enumerate(items):
            begin = -j * step
            begin_str = f"{begin:.2f}s" if j > 0 else "0.00s"
            parts.append(
                '  <g>\n'
                f'    <circle r="3" fill="{fg}" fill-opacity=".9"/>\n'
                f'    <circle r="7" fill="none" stroke="{fg}" stroke-opacity=".25" stroke-width="1"/>\n'
                f'    <text x="12" y="4" style="font:400 12px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;letter-spacing:1.4px" '
                f'fill="{fg}" fill-opacity=".8">{label}</text>\n'
                f'    <animateMotion dur="{dur:g}s" begin="{begin_str}" repeatCount="indefinite" rotate="0"><mpath href="#o{idx}"/></animateMotion>\n'
                '  </g>\n'
            )

    parts.append('</svg>\n')
    return "".join(parts)
