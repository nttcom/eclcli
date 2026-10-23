"""Compatibility helpers for installed entry points."""

try:
    from importlib import metadata
except ImportError:  # Python 3.7 has no importlib.metadata.
    metadata = None
    import pkg_resources


if metadata is None:
    LOAD_EXCEPTIONS = (ImportError, AttributeError, pkg_resources.UnknownExtra)
else:
    LOAD_EXCEPTIONS = (ImportError, AttributeError)


def iter_entry_points(group, name=None):
    """Iterate over a group, using the API available on this Python version."""
    if metadata is None:
        yield from pkg_resources.iter_entry_points(group, name=name)
        return

    try:
        points = metadata.entry_points(group=group)
    except TypeError:  # Python 3.8 and 3.9 return a group mapping.
        points = metadata.entry_points().get(group, ())

    # Older importlib.metadata can report the same editable install twice.
    seen = set()
    for point in points:
        if name is not None and point.name != name:
            continue
        key = (point.name, point.value)
        if key not in seen:
            seen.add(key)
            yield point


def module_name(point):
    """Return the module path from either entry point implementation."""
    return (getattr(point, 'module_name', None) or
            point.value.partition(':')[0].split()[0])
