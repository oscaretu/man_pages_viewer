import subprocess
import re
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ManSection:
    title: str
    content: str


@dataclass
class ManPage:
    name: str
    description: str
    sections: list[ManSection]


class ManParser:
    def __init__(self):
        pass

    def exists(self, name: str, section: Optional[int] = None) -> bool:
        try:
            result = subprocess.run(
                ["man", "-w", f"{name}({section})" if section else name],
                capture_output=True,
                text=True,
                timeout=5,
            )
            path = result.stdout.strip()
            return bool(path and os.path.exists(path))
        except Exception:
            return False

    def get_raw(self, name: str, section: Optional[int] = None) -> str:
        try:
            if section:
                result = subprocess.run(
                    ["man", "-P", "cat", f"{name}({section})"],
                    capture_output=True,
                    text=True,
                )
            else:
                result = subprocess.run(
                    ["man", "-P", "cat", name], capture_output=True, text=True
                )
            return result.stdout
        except Exception as e:
            raise RuntimeError(f"Failed to get man page: {e}")

    def parse(self, name: str, section: Optional[int] = None) -> ManPage:
        raw = self.get_raw(name, section)
        return self.parse_text(name, raw)

    def parse_text(self, name: str, text: str) -> ManPage:
        lines = text.split("\n")
        sections = []
        current_title = None
        current_content = []

        for line in lines:
            stripped = line.strip()
            is_header = (
                stripped.isupper()
                and len(stripped) > 2
                and not stripped.startswith("-")
                and not stripped.startswith("[")
                and len([c for c in stripped if c.isalpha()]) / len(stripped) > 0.7
            )

            if is_header and not any(c.isdigit() for c in stripped):
                if current_title and current_content:
                    sections.append(
                        ManSection(
                            title=current_title,
                            content="\n".join(current_content).strip(),
                        )
                    )
                current_title = stripped
                current_content = []
            elif current_title:
                current_content.append(line)

        if current_title and current_content:
            sections.append(
                ManSection(
                    title=current_title, content="\n".join(current_content).strip()
                )
            )

        description = ""
        if sections and "NAME" in sections[0].title.upper():
            first_lines = sections[0].content.split("\n")
            for l in first_lines:
                if " - " in l:
                    description = l.split(" - ", 1)[1].strip()
                    break

        return ManPage(name=name, description=description, sections=sections)

    def search(self, query: str) -> list[tuple[str, str]]:
        try:
            result = subprocess.run(["apropos", query], capture_output=True, text=True)
            results = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = line.split(" - ", 1)
                    if len(parts) >= 1:
                        name = parts[0].strip()
                        desc = parts[1].strip() if len(parts) > 1 else ""
                        results.append((name, desc))
            return results
        except Exception:
            return []
