"""Validate project skill metadata and local Markdown references without network access."""

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def validate() -> tuple[int, list[str]]:
    """Check every existing skill without rewriting third-party skills."""
    problems: list[str] = []
    count = 0
    for base in (ROOT / ".github/skills", ROOT / ".agents/skills"):
        names: set[str] = set()
        for folder in sorted(base.iterdir()):
            if folder.is_dir() and not (folder / "SKILL.md").is_file():
                problems.append(f"{folder.relative_to(ROOT)}: missing SKILL.md")
        for path in sorted(base.glob("*/SKILL.md")):
            count += 1
            rel = path.relative_to(ROOT)
            text = path.read_text(encoding="utf-8-sig")
            parts = text.split("---", 2)
            if not text.startswith("---\n") or len(parts) != 3:
                problems.append(f"{rel}: missing frontmatter")
                continue
            try:
                meta = yaml.safe_load(parts[1])
            except yaml.YAMLError as error:
                problems.append(f"{rel}: invalid YAML: {error}")
                continue
            if not isinstance(meta, dict):
                problems.append(f"{rel}: metadata must be a mapping")
                continue
            name = meta.get("name", "")
            if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
                problems.append(f"{rel}: invalid name")
            elif name != path.parent.name or len(name) > 64 or name in names:
                problems.append(f"{rel}: mismatched, long, or duplicate name")
            else:
                names.add(name)
            description = meta.get("description")
            if not isinstance(description, str) or not description.strip():
                problems.append(f"{rel}: missing description")
            for doc in path.parent.rglob("*.md"):
                # Ignore optional locally downloaded reference snapshots.
                if "references/docs" in doc.relative_to(path.parent).as_posix():
                    continue
                for target in LINK.findall(doc.read_text(encoding="utf-8-sig")):
                    if target.startswith(("http://", "https://", "mailto:", "#")):
                        continue
                    target = target.split("#", 1)[0].split(" ", 1)[0].strip("<>")
                    if target and not (doc.parent / target).exists():
                        problems.append(f"{doc.relative_to(ROOT)}: missing link {target}")
    return count, problems


if __name__ == "__main__":
    total, errors = validate()
    print(f"Checked {total} skills; {len(errors)} issue(s).")
    for issue in errors:
        print(issue)
    raise SystemExit(bool(errors))
