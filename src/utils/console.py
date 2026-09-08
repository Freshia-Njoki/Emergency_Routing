"""
Windows-safe console and file encoding helpers.

The original pipeline crashed on Windows cp1252 when printing arrows
(U+2192) or almost-equals (U+2248).  Call configure_utf8() at the top
of every entry-point script, and prefer ASCII arrows in log lines.
"""
from __future__ import annotations

import os
import sys


def configure_utf8() -> None:
    """Force UTF-8 for stdio and subprocess-inherited PYTHONIOENCODING."""
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    os.environ.setdefault("PYTHONUTF8", "1")
    for stream in (sys.stdout, sys.stderr):
        reconf = getattr(stream, "reconfigure", None)
        if callable(reconf):
            try:
                reconf(encoding="utf-8", errors="replace")
            except Exception:
                pass


def ascii_safe(text) -> str:
    """Replace common unicode glyphs so cp1252 consoles never crash."""
    if not isinstance(text, str):
        text = str(text)
    replacements = {
        "\u2192": "->",
        "\u2190": "<-",
        "\u2248": "~",
        "\u03b4": "delta",
        "\u03b4": "delta",
        "\u2713": "OK",
        "\u2717": "X",
        "\u2014": "-",
        "\u2013": "-",
        "\u00d7": "x",
        "\u2265": ">=",
        "\u2264": "<=",
        "\u00b1": "+/-",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


def safe_print(*args, **kwargs) -> None:
    kwargs.setdefault("flush", False)
    msg = " ".join(ascii_safe(a) for a in args)
    try:
        print(msg, **kwargs)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, "encoding", None) or "ascii"
        print(msg.encode(enc, errors="replace").decode(enc, errors="replace"), **kwargs)
