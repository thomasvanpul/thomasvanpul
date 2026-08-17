from . import palette

VIEW_W = 1200
MARGIN_X = 24
GAP = 30
Y_TOP = 40
BOX_H = 54
MIDLINE = Y_TOP + BOX_H / 2  # 67
STEP_SECONDS = 2.2  # each stage highlights for the same wall-clock slice

SIDE_Y = 136
SIDE_H = 34
SIDE_ANIM_DUR = 2.6


def _stage_geometry(n: int):
    box_w = (VIEW_W - 2 * MARGIN_X - (n - 1) * GAP) / n
    xs = [MARGIN_X + i * (box_w + GAP) for i in range(n)]
    centers = [x + box_w / 2 for x in xs]
    return box_w, xs, centers


def _stage(x: float, y: float, w: float, h: float, cx: float,
          label: str, sublabel: str, fg: str, key_a: float, key_b: float, dur: float) -> str:
    return (
        '<g>'
        f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="3" '
        f'fill="none" stroke="{fg}" stroke-opacity=".28" stroke-width="1">'
        f'<animate attributeName="stroke-opacity" values=".28;.95;.28;.28" '
        f'keyTimes="0;{key_a:.4f};{key_b:.4f};1" dur="{dur:.1f}s" repeatCount="indefinite"/>'
        '</rect>'
        f'<text x="{cx:.1f}" y="{y + 24}" text-anchor="middle" '
        'style="font:600 12.5px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;letter-spacing:1.6px" '
        f'fill="{fg}" fill-opacity=".92">{label}</text>'
        f'<text x="{cx:.1f}" y="{y + 42}" text-anchor="middle" '
        'style="font:400 9.5px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;letter-spacing:1.6px" '
        f'fill="{fg}" fill-opacity=".42">{sublabel}</text>'
        '</g>'
    )


def _arrow(from_x: float, to_x: float, y: float, fg: str) -> str:
    return (
        f'<line x1="{from_x:.1f}" y1="{y:.1f}" x2="{to_x:.1f}" y2="{y:.1f}" '
        f'stroke="{fg}" stroke-opacity=".3" stroke-width="1"/>'
        f'<path d="M {to_x - 7:.1f} {y - 3.5:.1f} L {to_x:.1f} {y:.1f} L {to_x - 7:.1f} {y + 3.5:.1f}" '
        f'fill="none" stroke="{fg}" stroke-opacity=".3" stroke-width="1"/>'
    )


def render(theme: str, stages: list[tuple[str, str]], duration: float | None = None,
           side_input: dict | None = None) -> str:
    """Render a stage-flow diagram.

    stages: list of (label, sublabel) tuples.
    duration: total animation cycle in seconds. Defaults to n * 2.2.
    side_input: optional {"label", "sublabel", "connects_to": int, "box_w": float}
                connects_to is the index of the stage the input feeds into.
    """
    fg, _ = palette(theme)
    n = len(stages)
    if n < 2:
        raise ValueError("flow needs at least 2 stages")
    if duration is None:
        duration = n * STEP_SECONDS

    box_w, xs, centers = _stage_geometry(n)
    step = 1.0 / n

    height = 150
    if side_input is not None:
        height = 182

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW_W} {height}" '
        f'width="{VIEW_W}" height="{height}" role="img" aria-label="'
        + " to ".join(label for label, _ in stages) + '">\n'
    ]

    for i, (label, sublabel) in enumerate(stages):
        parts.append(_stage(
            xs[i], Y_TOP, box_w, BOX_H, centers[i], label, sublabel, fg,
            key_a=0.02 + i * step, key_b=0.14 + i * step, dur=duration,
        ))

    for i in range(n - 1):
        parts.append(_arrow(xs[i] + box_w, xs[i + 1], MIDLINE, fg))

    parts.append(
        f'<path id="track" d="M {centers[0]:.1f} {MIDLINE:.1f} L {centers[-1]:.1f} {MIDLINE:.1f}" '
        'fill="none" stroke="none"/>'
    )
    parts.append(
        f'<circle r="3.5" fill="{fg}" fill-opacity=".95">'
        f'<animateMotion dur="{duration:.1f}s" repeatCount="indefinite" calcMode="linear">'
        '<mpath href="#track"/></animateMotion></circle>'
    )
    parts.append(
        f'<circle r="9" fill="none" stroke="{fg}" stroke-opacity=".3" stroke-width="1">'
        f'<animateMotion dur="{duration:.1f}s" repeatCount="indefinite" calcMode="linear">'
        '<mpath href="#track"/></animateMotion></circle>'
    )

    if side_input is not None:
        idx = side_input["connects_to"]
        sx = xs[idx]
        scx = centers[idx]
        sw = box_w
        parts.append(
            '<g>'
            f'<rect x="{sx:.1f}" y="{SIDE_Y}" width="{sw:.1f}" height="{SIDE_H}" rx="3" '
            f'fill="none" stroke="{fg}" stroke-opacity=".22" stroke-width="1" stroke-dasharray="3 3"/>'
            f'<text x="{scx:.1f}" y="{SIDE_Y + 15}" text-anchor="middle" '
            'style="font:600 10.5px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;letter-spacing:1.4px" '
            f'fill="{fg}" fill-opacity=".7">{side_input["label"]}</text>'
            f'<text x="{scx:.1f}" y="{SIDE_Y + 27}" text-anchor="middle" '
            'style="font:400 8.5px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;letter-spacing:1.4px" '
            f'fill="{fg}" fill-opacity=".38">{side_input["sublabel"]}</text>'
            f'<line x1="{scx:.1f}" y1="{SIDE_Y}" x2="{scx:.1f}" y2="{Y_TOP + BOX_H}" '
            f'stroke="{fg}" stroke-opacity=".25" stroke-width="1"/>'
            f'<circle cx="{scx:.1f}" cy="{SIDE_Y}" r="2.5" fill="{fg}" fill-opacity=".7">'
            f'<animate attributeName="cy" values="{SIDE_Y};{Y_TOP + BOX_H}" '
            f'dur="{SIDE_ANIM_DUR}s" repeatCount="indefinite"/>'
            f'<animate attributeName="fill-opacity" values=".85;0" '
            f'dur="{SIDE_ANIM_DUR}s" repeatCount="indefinite"/>'
            '</circle>'
            '</g>'
        )

    parts.append('\n</svg>\n')
    return "".join(parts)
