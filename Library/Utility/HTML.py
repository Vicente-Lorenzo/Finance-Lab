def style(**kwargs) -> str:
    parts = []
    for key, value in kwargs.items():
        if value is None:
            continue
        css_key = key.replace("_", "-")
        parts.append(f"{css_key}:{value}")
    return "; ".join(parts) + (";" if parts else "")

def div(
    content: str,
    font_size: str | None = None,
    font_weight: str | None = None,
    font_color: str | None = None,
    font_family: str | None = None,
    **extra_styles,
) -> str:
    s = style(
        font_family=font_family,
        font_size=font_size,
        font_weight=font_weight,
        color=font_color,
        **extra_styles,
    )
    return f'<div style="{s}">{content}</div>'

def span(
    content: str,
    font_size: str | None = None,
    font_weight: str | None = None,
    font_color: str | None = None,
    font_family: str | None = None,
    **extra_styles,
) -> str:
    s = style(
        font_family=font_family,
        font_size=font_size,
        font_weight=font_weight,
        color=font_color,
        **extra_styles,
    )
    return f'<span style="{s}">{content}</span>'

def heading(
    level: int,
    content: str,
    font_size: str | None = None,
    font_weight: str | None = None,
    font_color: str | None = None,
    font_family: str | None = None,
    **extra_styles,
) -> str:
    tag = f"h{level}"
    s = style(
        font_family=font_family,
        font_size=font_size,
        font_weight=font_weight,
        color=font_color,
        **extra_styles,
    )
    return f'<{tag} style="{s}">{content}</{tag}>'

def h1(
    content: str,
    font_size: str | None = None,
    font_weight: str | None = None,
    font_color: str | None = None,
    font_family: str | None = None,
    **extra_styles,
) -> str:
    return heading(
        level=1,
        content=content,
        font_family=font_family,
        font_size=font_size,
        font_weight=font_weight,
        color=font_color,
        **extra_styles,
    )

def h2(
    content: str,
    font_size: str | None = None,
    font_weight: str | None = None,
    font_color: str | None = None,
    font_family: str | None = None,
    **extra_styles,
) -> str:
    return heading(
        level=2,
        content=content,
        font_family=font_family,
        font_size=font_size,
        font_weight=font_weight,
        color=font_color,
        **extra_styles,
    )

def h3(
    content: str,
    font_size: str | None = None,
    font_weight: str | None = None,
    font_color: str | None = None,
    font_family: str | None = None,
    **extra_styles,
) -> str:
    return heading(
        level=3,
        content=content,
        font_family=font_family,
        font_size=font_size,
        font_weight=font_weight,
        color=font_color,
        **extra_styles,
    )

def h4(
    content: str,
    font_size: str | None = None,
    font_weight: str | None = None,
    font_color: str | None = None,
    font_family: str | None = None,
    **extra_styles,
) -> str:
    return heading(
        level=4,
        content=content,
        font_family=font_family,
        font_size=font_size,
        font_weight=font_weight,
        color=font_color,
        **extra_styles,
    )

def h5(
    content: str,
    font_size: str | None = None,
    font_weight: str | None = None,
    font_color: str | None = None,
    font_family: str | None = None,
    **extra_styles,
) -> str:
    return heading(
        level=5,
        content=content,
        font_family=font_family,
        font_size=font_size,
        font_weight=font_weight,
        color=font_color,
        **extra_styles,
    )

def paragraph(
    content: str,
    font_size: str | None = None,
    font_weight: str | None = None,
    font_color: str | None = None,
    font_family: str | None = None,
    line_height: str | None = None,
    **extra_styles,
) -> str:
    s = style(
        font_family=font_family,
        font_size=font_size,
        font_weight=font_weight,
        color=font_color,
        line_height=line_height,
        **extra_styles,
    )
    return f'<p style="{s}">{content}</p>'

def hyperlink(
    link: str,
    content: str,
    font_size: str | None = None,
    font_weight: str | None = None,
    font_color: str | None = None,
    font_family: str | None = None,
    **extra_styles,
) -> str:
    s = style(
        font_family=font_family,
        font_size=font_size,
        font_weight=font_weight,
        color=font_color,
        **extra_styles,
    )
    return f'<a href="{link}" style="{s}">{content}</a>'

def blank_line() -> str:
    return '<p style="margin:0;-size:0; line-height:1em;">&nbsp;</p>'

def blank_space(height: str = "1rem", width: str = "100%") -> str:
    if height in ("1rem", "1em", "16px"):
        return blank_line()
    return div(
        "&nbsp;",
        font_size="0",
        height=height,
        width=width,
        display="block",
    )
