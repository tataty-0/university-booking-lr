"""Run the quality requirement checks and print a report: python scripts/measure_quality.py"""

import subprocess
import sys
from datetime import UTC, datetime


def main() -> int:
    command = [sys.executable, "-m", "pytest", "tests/quality", "-v", "-s"]
    result = subprocess.run(command, capture_output=True, text=True)
    print(f"# Quality measurement, {datetime.now(UTC).isoformat(timespec='seconds')}\n")
    print(f"Python {sys.version.split()[0]}\n")
    print("```")
    print(result.stdout.strip())
    print("```")
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
