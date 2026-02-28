from dash.development.base_component import Component

def formatize(name: str, value: object) -> str:
    import html
    if name == "className":
        name = "class"
    if name == "style" and isinstance(value, dict):
        css_parts = []
        for k, v in value.items():
            css_key = (
                k.replace("_", "-")
                .replace(" ", "-")
                .replace(".", "-")
                .replace("--", "-")
            )
            css_key = "".join(
                ["-" + c.lower() if c.isupper() else c for c in css_key]
            ).lstrip("-")
            css_parts.append(f"{css_key}:{v};")
        value = ";".join(css_parts) + (";" if css_parts else "")
    if isinstance(value, bool):
        return name if value else ""
    escaped = html.escape(str(value), quote=True)
    return f'{name}="{escaped}"'

def stylize(component: Component) -> str:
    parts: list[str] = []
    for prop in component._prop_names:
        if prop == "children": continue
        value = getattr(component, prop, None)
        if value is None: continue
        html_key = prop.replace("_", "-")
        attr_str = formatize(html_key, value)
        if attr_str: parts.append(attr_str)
    return "" if not parts else " " + " ".join(parts)

def htmlize(node: str | int | float | list | tuple | Component) -> str:
    if node is None:
        return ""
    if isinstance(node, (str, int, float)):
        return str(node)
    if isinstance(node, (list, tuple)):
        return "".join(htmlize(child) for child in node)
    if isinstance(node, Component):
        tag = node.__class__.__name__.lower()
        attributes = stylize(node)
        children = htmlize(node.children)
        return f"<{tag}{attributes}>{children}</{tag}>"
    raise TypeError(f"Unsupported type for htmlize(): {type(node)}")
