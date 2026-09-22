#!/usr/bin/env python3
"""Verify a bundled/GitHub template and copy it to a new private working file."""
import argparse
import hashlib
import json
import os
from pathlib import Path
from urllib.request import urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("template", choices=["self-purchase", "goods", "service"])
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    folder = Path(__file__).resolve().parents[1] / "assets" / "templates"
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    item = next(t for t in manifest["templates"] if t["id"] == args.template)
    original = folder / item["file"]
    output = args.output.expanduser().resolve()
    if output.suffix.lower() != ".docx":
        parser.error("Output must be a .docx file")
    if folder in output.parents:
        parser.error("Output must be outside the original template directory")
    try:
        if original.exists():
            content = original.read_bytes()
        else:
            with urlopen(item["raw_url"], timeout=30) as response:
                content = response.read(10 * 1024 * 1024 + 1)
        digest = hashlib.sha256(content).hexdigest()
        if digest != item["sha256"]:
            raise ValueError("Template hash mismatch; check the installed manifest/version")
        os.umask(0o077)
        output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with output.open("xb") as stream:
            stream.write(content)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"{exc}\n")
    print(json.dumps({"path": str(output), "template_id": item["id"], "sha256": digest,
                      "status": "template_copy_not_filled"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
