# py-path-component-case-conflict

Detects case-insensitive path collisions in a single directory — the kind of collision that silently corrupts data when a case-sensitive source (a tarball, a git tree) is unpacked onto a case-insensitive filesystem (macOS APFS default, Windows NTFS) or vice versa.

```python
from py_path_component_case_conflict import find_case_conflicts, Conflict

# Given a directory containing these entries:
#   README
#   readme
for conflict in find_case_conflicts("."):
    print(conflict.base_dir, conflict.lower_form, conflict.paths)
    # . readme ('README', 'readme')
```

`find_case_conflicts(directory)` returns a `list[Conflict]`, where each `Conflict` is a frozen dataclass with `base_dir: str`, `lower_form: str`, and `paths: tuple[str, ...]`. The filesystem you call it on must actually expose the colliding sibling entries — typically you point it at a directory where an extraction has already failed or where you suspect a tree contains case-variant siblings.

## Why this exists

Moving trees between case-sensitive and case-insensitive filesystems is a well-known source of silent data loss: one of `LICENSE` / `License` / `license` overwrites the others on a case-insensitive target, and no error is reported. This library gives you a precise, attributable report of which directory contains a collision and which exact on-disk names are involved, so a packaging or migration step can refuse to proceed.

The scope is deliberately narrow: **only direct children of the given directory are compared, and there is no recursion.** Real-world collisions are almost always a flat directory produced by an archive extraction or a checkout at a specific revision; a recursive walk would silently swallow permission errors and make each conflict harder to attribute to a parent. If you need to scan a tree, call `find_case_conflicts` on each directory yourself — you stay in control of error handling and the result stays tied to a single `base_dir`.

## The awkward edge

A single directory entry by itself is never a conflict, even if its name happens to look "wrong"; a conflict requires two or more distinct names sharing the same lowercase form. On a filesystem that is itself case-insensitive, `os.listdir` will not surface two siblings differing only in case (one overwrote the other at write time), so the function will report an empty list. It is designed for directories on a case-sensitive filesystem, or for a case-insensitive filesystem that has preserved both entries through some other mechanism (e.g. an extractor that renames the second occurrence). Check the filesystem type if a zero-result is suspicious.
