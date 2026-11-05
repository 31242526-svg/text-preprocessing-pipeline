"""CLI: textprep corpus.txt --config configs/default.yml -o tokens.jsonl."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from textprep.core import Config, preprocess


def load_config(path: Path | None) -> Config:
    if path is None:
        return Config()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"config must be a mapping: {path}")
    return Config.from_mapping(data)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="textprep",
        description="Normalise and tokenise a text corpus with an explicit config.",
    )
    parser.add_argument("source", type=Path, help="input text file, one document per line")
    parser.add_argument("--config", type=Path, default=None, help="YAML config file")
    parser.add_argument("-o", "--output", type=Path, default=None, help="output file")
    parser.add_argument(
        "--format", choices=["jsonl", "text"], default="jsonl", help="output format"
    )
    parser.add_argument("--show-config", action="store_true", help="print the resolved config")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        cfg = load_config(args.config)
    except (ValueError, yaml.YAMLError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not args.source.exists():
        print(f"error: no such file: {args.source}", file=sys.stderr)
        return 2

    if args.show_config:
        print(json.dumps(cfg.to_dict(), indent=2))

    lines = args.source.read_text(encoding="utf-8").splitlines()
    results = [preprocess(line, cfg) for line in lines]

    if args.output is None:
        for i, tokens in enumerate(results, start=1):
            if args.format == "jsonl":
                print(json.dumps({"line": i, "tokens": tokens}))
            else:
                print(" ".join(tokens))
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as handle:
            for i, tokens in enumerate(results, start=1):
                if args.format == "jsonl":
                    handle.write(json.dumps({"line": i, "tokens": tokens}) + "\n")
                else:
                    handle.write(" ".join(tokens) + "\n")
        total = sum(len(t) for t in results)
        print(f"{args.output} written: {len(results)} lines, {total} tokens")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
