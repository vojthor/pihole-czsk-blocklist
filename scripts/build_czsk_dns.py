#!/usr/bin/env python3
"""Build a conservative Pi-hole list from EasyList Czech and Slovak."""

from __future__ import annotations

import ipaddress
import re
from collections.abc import Iterable, Iterator
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen

SOURCE = (
    "https://raw.githubusercontent.com/"
    "tomasko126/easylistczechandslovak/master/filters.txt"
)
OUTPUT = Path("easylist-czsk-pihole.txt")

INCLUDE_RE = re.compile(r"^!#include\s+(.+?)\s*$")
DOMAIN_RULE_RE = re.compile(r"^\|\|([^/^$*]+)\^\s*$", re.IGNORECASE)


def download_filter(url: str, visited: set[str] | None = None) -> Iterator[str]:
    """Download a filter and recursively resolve its !#include directives."""
    if visited is None:
        visited = set()

    if url in visited:
        return

    visited.add(url)
    request = Request(url, headers={"User-Agent": "pihole-czsk-blocklist/1.0"})

    with urlopen(request, timeout=30) as response:
        text = response.read().decode("utf-8-sig")

    for line in text.splitlines():
        stripped = line.strip()
        include = INCLUDE_RE.fullmatch(stripped)

        if include:
            yield from download_filter(urljoin(url, include.group(1)), visited)
        else:
            yield stripped


def normalize_domain(value: str) -> str | None:
    """Return a safe ASCII domain, or None when the value is unsuitable."""
    value = value.rstrip(".").lower()

    try:
        value = value.encode("idna").decode("ascii")
    except UnicodeError:
        return None

    if "." not in value or len(value) > 253:
        return None

    try:
        ipaddress.ip_address(value)
        return None
    except ValueError:
        pass

    labels = value.split(".")
    if not all(
        1 <= len(label) <= 63
        and not label.startswith("-")
        and not label.endswith("-")
        and re.fullmatch(r"[a-z0-9-]+", label)
        for label in labels
    ):
        return None

    return value


def extract_rules(lines: Iterable[str]) -> list[str]:
    """Keep only unmodified domain-wide ABP rules safe for DNS blocking."""
    rules: set[str] = set()

    for line in lines:
        match = DOMAIN_RULE_RE.fullmatch(line.strip())
        if not match:
            continue

        domain = normalize_domain(match.group(1))
        if domain:
            rules.add(f"||{domain}^")

    return sorted(rules)


def render(rules: Iterable[str]) -> str:
    header = [
        "!",
        "! Title: EasyList Czech and Slovak - safe Pi-hole DNS subset",
        f"! Source: {SOURCE}",
        "! Upstream license: CC BY-SA 4.0",
        "! Only unmodified domain-wide ABP rules are retained.",
        "!",
    ]
    return "\n".join([*header, *rules]) + "\n"


def main() -> None:
    rules = extract_rules(download_filter(SOURCE))
    if not rules:
        raise RuntimeError("Upstream conversion produced no DNS rules")

    OUTPUT.write_text(render(rules), encoding="utf-8")
    print(f"Wrote {len(rules)} DNS rules to {OUTPUT}")


if __name__ == "__main__":
    main()
