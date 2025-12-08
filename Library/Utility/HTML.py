from dash.development.base_component import Component

def stylize(component: Component) -> str:
    parts: list[str] = []
    for name in component._prop_names:
        if name == "children":
            continue
        value = getattr(component, name, None)
        if value is None:
            continue
        html_key = name.replace("_", "-")
        parts.append(f'{html_key}="{value}"')
    return "" if not parts else " " + " ".join(parts)

def htmlize(node: str | int | float | list | tuple | Component | None) -> str:
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
