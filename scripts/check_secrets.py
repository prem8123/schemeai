from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]


def main() -> int:
    tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    failures: list[str] = []
    for name in tracked:
        if Path(name).name == ".env" or name.endswith("/.env"):
            failures.append(f"tracked secret file: {name}")
            continue
        path = ROOT / name
        if not path.is_file() or path.stat().st_size > 1_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                failures.append(f"possible secret pattern in: {name}")
                break
    if failures:
        print("Secret-safety check failed:")
        print("\n".join(f"- {item}" for item in failures))
        return 1
    print("Secret-safety check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
