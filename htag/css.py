_scoped_style_cache: dict[type, tuple[str, str]] = {}


def _scope_css(css: str, scope_cls: str) -> str:
    """Prefix CSS selectors with a scope class, handling @-rules correctly."""
    result: list[str] = []
    depth = 0
    buf = ""

    for ch in css:
        buf += ch
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                blocks_item = buf.strip()
                buf = ""
                brace = blocks_item.index("{")
                selector = blocks_item[:brace].strip()
                body = blocks_item[brace:]

                if selector.startswith("@"):
                    if selector.startswith(("@keyframes", "@font-face")):
                        result.append(blocks_item)  # Pass through unchanged
                    else:
                        # @media, @supports, etc.: recursively scope inner rules
                        inner = body[body.index("{") + 1 : body.rindex("}")]
                        result.append(f"{selector} {{{_scope_css(inner, scope_cls)}}}")
                else:
                    # For each selector, match both the root element itself and descendants
                    parts = [s.strip() for s in selector.split(",")]
                    scoped_parts: list[str] = []
                    for p in parts:
                        if not p:
                            continue
                        # .htag-X.selector = root element itself (if selector is a class/id/pseudo)
                        # selector.htag-X = root element itself (if selector is a tag)
                        # .htag-X .selector = descendant elements
                        if p[0] in (".", "#", ":", "["):
                            scoped_parts.append(f".{scope_cls}{p}")
                        else:
                            scoped_parts.append(f"{p}.{scope_cls}")
                        scoped_parts.append(f".{scope_cls} {p}")
                    result.append(f"{', '.join(scoped_parts)} {body}")

    return " ".join(result)
