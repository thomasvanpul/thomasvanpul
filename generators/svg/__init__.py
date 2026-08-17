FG_DARK = "#e6edf3"
FG_LIGHT = "#0d1117"
BG_DARK = "#0d1117"
BG_LIGHT = "#ffffff"


def palette(theme: str) -> tuple[str, str]:
    if theme == "dark":
        return FG_DARK, BG_DARK
    if theme == "light":
        return FG_LIGHT, BG_LIGHT
    raise ValueError(f"unknown theme: {theme}")


THEMES = ("dark", "light")
