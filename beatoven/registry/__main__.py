"""CLI for rune registry operations."""

from __future__ import annotations

import argparse
from beatoven.registry.loader import RuneRegistry


def main() -> None:
    parser = argparse.ArgumentParser(description="ABX-Runes registry CLI")
    parser.add_argument("command", choices=["list", "validate"], help="Command to execute")
    args = parser.parse_args()

    registry = RuneRegistry()

    if args.command == "list":
        registry.load()
        for spec in registry.list_runes():
            print(f"{spec.rune_id} :: {spec.data.get('name')}")
        return

    if args.command == "validate":
        registry.load()
        results = registry.validate_all()
        failures = {rune_id: errs for rune_id, errs in results.items() if errs}
        if failures:
            for rune_id, errs in failures.items():
                print(f"{rune_id} errors:")
                for err in errs:
                    print(f"  - {err}")
            raise SystemExit(1)
        print("All runes valid")
        return


if __name__ == "__main__":
    main()
