from . import palette

VIEW_W = 1200
VIEW_H = 300

# Star field: (cx, cy, r, opacity, animation_duration). Frozen for byte-stable output.
STARS = [
    (396, 58, 1.2, 0.21, 5.7),
    (444, 33, 1.1, 0.20, 5.2),
    (101, 42, 1.0, 0.53, 3.6),
    (480, 276, 0.6, 0.54, 4.4),
    (187, 49, 0.9, 0.52, 3.9),
    (93, 34, 0.8, 0.47, 5.1),
    (629, 249, 1.3, 0.30, 7.9),
    (898, 58, 1.0, 0.20, 6.3),
    (994, 267, 1.0, 0.46, 3.3),
    (1172, 235, 0.9, 0.34, 6.3),
    (215, 49, 0.7, 0.50, 3.6),
    (1031, 39, 1.0, 0.41, 7.4),
    (970, 246, 0.9, 0.35, 4.8),
    (1046, 271, 0.7, 0.25, 4.2),
    (703, 87, 0.6, 0.36, 4.8),
    (677, 270, 1.2, 0.40, 6.1),
    (804, 32, 1.4, 0.51, 7.4),
    (483, 45, 1.2, 0.21, 3.3),
    (262, 61, 0.9, 0.20, 3.0),
    (195, 45, 0.9, 0.19, 7.4),
    (732, 57, 0.8, 0.33, 4.8),
    (162, 242, 1.5, 0.38, 5.4),
    (120, 45, 0.9, 0.29, 7.1),
    (207, 24, 1.5, 0.40, 3.7),
    (650, 25, 1.1, 0.59, 7.3),
    (828, 87, 0.9, 0.25, 6.9),
    (402, 77, 1.3, 0.59, 7.3),
]

# Orbital planet on the right side.
PLANET_CX = 935.0
PLANET_CY = 150.0
PLANET_ROT = -7.0
PLANET_CORE_R = 44.0
PLANET_PULSE_R = 53.0

# Six concentric ellipses. rx, ry, stroke_opacity, stroke_width, dur (seconds for the dash offset animation).
PLANET_RINGS = [
    (252, 38, "0.34", 1.0, 26),
    (218, 33, "0.46", 1.1, 21),
    (184, 28, "0.6", 1.2, 17),
    (150, 23, "0.74", 1.2, 13),
    (118, 18, "0.88", 1.4, 10),
    (88, 13, "1.0", 1.5, 7),
]

# Subtitle rotation.
SUBTITLE_TOTAL_DUR = 13.60
SUBTITLE_FADE = 0.0331  # fraction of total per fade in/out


def _star(cx: int, cy: int, r: float, base_op: float, dur: float, fg: str) -> str:
    low = round(base_op * 0.25, 2)
    return (
        f'    <circle cx="{cx}" cy="{cy}" r="{r}" fill="{fg}" opacity="{base_op:.2f}">'
        f'<animate attributeName="opacity" values="{base_op:.2f};{low:.2f};{base_op:.2f}" '
        f'dur="{dur}s" repeatCount="indefinite"/></circle>\n'
    )


def _planet_ellipses(fg: str) -> str:
    parts = []
    for rx, ry, op, sw, dur in PLANET_RINGS:
        # Approximate ellipse perimeter used to derive the dash pattern.
        perim = 3.14159 * (3 * (rx + ry) - ((3 * rx + ry) * (rx + 3 * ry)) ** 0.5)
        # Empirical dash proportions from the reference SVG: [dash, gap, dash/tick, long gap]
        # captured as fractions of the perimeter.
        d1 = perim * 0.100
        d2 = perim * 0.050
        d3 = perim * 0.030
        d4 = perim - (d1 + d2 + d3)
        parts.append(
            f'    <ellipse cx="{PLANET_CX}" cy="{PLANET_CY}" rx="{rx}" ry="{ry}" '
            f'fill="none" stroke="{fg}" stroke-opacity="{op}" stroke-width="{sw}" '
            f'stroke-dasharray="{d1:.1f} {d2:.1f} {d3:.1f} {d4:.1f}" stroke-linecap="round">'
            f'<animate attributeName="stroke-dashoffset" from="0" to="{perim:.1f}" '
            f'dur="{dur}s" repeatCount="indefinite"/></ellipse>\n'
        )
    return "".join(parts)


def _planet_bottom_arcs(fg: str) -> str:
    parts = []
    for rx, ry, op, sw, _dur in PLANET_RINGS:
        parts.append(
            f'    <path d="M {PLANET_CX - rx:.1f} {PLANET_CY:.1f} '
            f'A {rx} {ry} 0 0 0 {PLANET_CX + rx:.1f} {PLANET_CY:.1f}" '
            f'fill="none" stroke="{fg}" stroke-opacity="{op}" stroke-width="{sw}"/>\n'
        )
    return "".join(parts)


def _planet_core_horizon(fg: str) -> str:
    # Small arc across the top of the core (the horizon line).
    r = 66.0
    return (
        f'    <path d="M {PLANET_CX - r:.1f} {PLANET_CY:.1f} '
        f'A {r} {r} 0 0 1 {PLANET_CX + r:.1f} {PLANET_CY:.1f}" '
        f'fill="none" stroke="{fg}" stroke-opacity=".5" stroke-width="1.1"/>\n'
    )


def _subtitle_animation(i: int, n: int) -> tuple[str, str, str]:
    slot = 1.0 / n
    slot_start = i * slot
    slot_end = (i + 1) * slot
    if i == 0:
        # First subtitle fades out at start and re-fades-in at end for a clean loop.
        values = "1;1;0;0;1"
        key_times = f"0.0000;{slot_start + slot - SUBTITLE_FADE:.4f};{slot_end:.4f};{1 - SUBTITLE_FADE:.4f};1.0000"
        return values, key_times, "1"
    values = "0;0;1;1;0;0"
    key_times = (
        f"0.0000;{slot_start:.4f};{slot_start + SUBTITLE_FADE:.4f};"
        f"{slot_end - SUBTITLE_FADE:.4f};{slot_end:.4f};1.0000"
    )
    return values, key_times, "0"


def render(theme: str, name: str, subtitle_lines: list[str]) -> str:
    fg, bg = palette(theme)
    aria = f"{name.title()}, {subtitle_lines[0].title() if subtitle_lines else ''}"

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW_W} {VIEW_H}" '
        f'width="{VIEW_W}" height="{VIEW_H}" role="img" aria-label="{aria}">\n'
        '  <style>\n'
        f'    .name {{ font: 600 44px ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; letter-spacing: 6px; fill: {fg}; }}\n'
        f'    .sub  {{ font: 400 15px ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; letter-spacing: 3.2px; fill: {fg}; fill-opacity: .70; }}\n'
        f'    .cur  {{ fill: {fg}; }}\n'
        '  </style>\n\n'
    ]

    parts.append('  <g>\n')
    for cx, cy, r, op, dur in STARS:
        parts.append(_star(cx, cy, r, op, dur, fg))
    parts.append('  </g>\n\n')

    parts.append(f'  <g transform="rotate({PLANET_ROT} {PLANET_CX} {PLANET_CY})">\n')
    parts.append(_planet_ellipses(fg))
    parts.append(_planet_core_horizon(fg))
    parts.append(f'    <circle cx="{PLANET_CX}" cy="{PLANET_CY}" r="{PLANET_CORE_R}" fill="{bg}"/>\n')
    parts.append(
        f'    <circle cx="{PLANET_CX}" cy="{PLANET_CY}" r="{PLANET_CORE_R}" fill="none" '
        f'stroke="{fg}" stroke-width="1.8" stroke-opacity=".9">\n'
        '      <animate attributeName="stroke-opacity" values=".9;.45;.9" dur="5.5s" repeatCount="indefinite"/>\n'
        '    </circle>\n'
    )
    parts.append(
        f'    <circle cx="{PLANET_CX}" cy="{PLANET_CY}" r="{PLANET_PULSE_R}" fill="none" '
        f'stroke="{fg}" stroke-width="0.7" stroke-opacity=".28">\n'
        f'      <animate attributeName="r" values="{PLANET_PULSE_R};{PLANET_PULSE_R + 8};{PLANET_PULSE_R}" dur="5.5s" repeatCount="indefinite"/>\n'
        '      <animate attributeName="stroke-opacity" values=".28;.05;.28" dur="5.5s" repeatCount="indefinite"/>\n'
        '    </circle>\n'
    )
    parts.append(_planet_bottom_arcs(fg))
    parts.append('  </g>\n\n')

    parts.append(
        f'  <line x1="70" y1="200" x2="470" y2="200" stroke="{fg}" stroke-opacity=".22" stroke-width="1"/>\n'
        f'  <text class="name" x="70" y="150">{name}</text>\n'
    )
    n = len(subtitle_lines)
    for i, line in enumerate(subtitle_lines):
        values, key_times, initial_op = _subtitle_animation(i, n)
        parts.append(
            f'  <text class="sub" x="72" y="182" opacity="{initial_op}">{line}'
            f'<animate attributeName="opacity" values="{values}" keyTimes="{key_times}" '
            f'dur="{SUBTITLE_TOTAL_DUR:.2f}s" repeatCount="indefinite" calcMode="linear"/></text>\n'
        )
    parts.append(
        f'  <rect class="cur" x="58" y="170" width="7" height="16" opacity=".8">\n'
        '    <animate attributeName="opacity" values=".8;0;.8" dur="1.1s" repeatCount="indefinite" calcMode="discrete" keyTimes="0;0.5;1"/>\n'
        '  </rect>\n'
        '</svg>\n'
    )
    return "".join(parts)
