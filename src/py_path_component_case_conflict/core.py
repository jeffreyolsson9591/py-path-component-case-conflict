from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Conflict:
    """Represents a case-insensitive path component collision.

    ``base_dir`` is the directory searched. ``lower_form`` is the lowercased
    component name shared by the colliding entries. ``paths`` are the concrete
    directory entries (exact on-disk casing) that map to ``lower_form``.
    """

    base_dir: str
    lower_form: str
    paths: tuple[str, ...]


def find_case_conflicts(directory: str) -> list[Conflict]:
    """Detect case-insensitive collisions among entries in a single directory.

    The filesystem this runs on may or may not itself be case-sensitive; the
    caller should point ``directory`` at a path known to contain sibling
    entries that differ only in letter case (commonly produced by extracting a
    case-sensitive archive onto a case-insensitive filesystem).

    Only direct children of ``directory`` are compared. A collision is defined
    as two or more distinct entry names sharing the same lowercase form.

    Rationale for *not* recursing: real-world corruption is almost always a
    single flat directory (an archive extraction, a git checkout at a
    specific revision). A recursive walk silently misses conflicts in
    directories the os cannot enumerate (permission errors) and makes the
    result hard to attribute to a specific parent. Each conflict explicitly
    records its ``base_dir`` so the caller can act on it.

    Raises:
        FileNotFoundError: if ``directory`` does not exist or is not
            traversable.
        NotADirectoryError: if ``directory`` is a regular file.
    """
    entries = sorted(os.listdir(directory))
    by_lower: dict[str, list[str]] = {}
    for name in entries:
        by_lower.setdefault(name.lower(), []).append(name)

    conflicts: list[Conflict] = []
    for lower_form, names in by_lower.items():
        if len(names) >= 2:
            conflicts.append(
                Conflict(
                    base_dir=directory,
                    lower_form=lower_form,
                    paths=tuple(names),
                )
            )
    return conflicts
