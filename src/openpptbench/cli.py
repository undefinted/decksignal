from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from .adapters import import_normalized_csv, import_upstream, write_evidence_records
from .aggregate import aggregate
from .arena import aggregate_elo
from .inspect import inspect_pptx
from .monitoring import check_products, discover_github, merge_discoveries
from .ranking import build_rankings
from .site import build_site
from .validate import validate_path


def _write_json(data: object, output: str | None) -> None:
    rendered = json.dumps(data, ensure_ascii=False, indent=2)
    if output:
        destination = Path(output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="openpptbench")
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect", help="Inspect a native PPTX artifact")
    inspect_parser.add_argument("pptx")
    inspect_parser.add_argument("--output", "-o")
    inspect_parser.add_argument("--overlap-threshold", type=float, default=0.25)

    validate_parser = subparsers.add_parser("validate", help="Validate benchmark tasks")
    validate_parser.add_argument("target")
    validate_parser.add_argument(
        "--schema", default=str(Path("benchmark/schema/task.schema.json"))
    )

    aggregate_parser = subparsers.add_parser("aggregate", help="Build leaderboard JSON")
    aggregate_parser.add_argument("submissions")
    aggregate_parser.add_argument("--output", "-o")

    rank_parser = subparsers.add_parser("rank", help="Build evidence-aware leaderboards")
    rank_parser.add_argument("evidence")
    rank_parser.add_argument("--products", required=True)
    rank_parser.add_argument("--config", default="benchmark/config/capabilities-v0.2.yaml")
    rank_parser.add_argument("--as-of", help="ISO-8601 timestamp for reproducible ranking")
    rank_parser.add_argument("--output", "-o")

    import_parser = subparsers.add_parser(
        "import-csv", help="Import normalized upstream benchmark evidence"
    )
    import_parser.add_argument("input")
    import_parser.add_argument("--source", required=True)
    import_parser.add_argument("--source-version", required=True)
    import_parser.add_argument("--registry", default="benchmark/sources/registry-v0.2.yaml")
    import_parser.add_argument("--output-dir", required=True)

    upstream_parser = subparsers.add_parser(
        "import-upstream", help="Import a supported upstream benchmark output"
    )
    upstream_parser.add_argument("adapter", choices=["slidesgen", "presentbench", "gloss"])
    upstream_parser.add_argument("input")
    upstream_parser.add_argument("--product-snapshot", required=True)
    upstream_parser.add_argument("--source-version", required=True)
    upstream_parser.add_argument("--observed-at", required=True)
    upstream_parser.add_argument("--scenario", default="general")
    upstream_parser.add_argument("--language", default="und")
    upstream_parser.add_argument("--registry", default="benchmark/sources/registry-v0.2.yaml")
    upstream_parser.add_argument("--output-dir", required=True)

    site_parser = subparsers.add_parser("build-site", help="Build the static results website")
    site_parser.add_argument("rankings")
    site_parser.add_argument("--products", required=True)
    site_parser.add_argument("--output-dir", required=True)

    monitor_parser = subparsers.add_parser("check-products", help="Check product URL health")
    monitor_parser.add_argument("products")
    monitor_parser.add_argument("--timeout", type=float, default=10)
    monitor_parser.add_argument("--workers", type=int, default=6)
    monitor_parser.add_argument("--output", "-o")

    discovery_parser = subparsers.add_parser(
        "ingest-discovery", help="Merge product discoveries into a review queue"
    )
    discovery_parser.add_argument("input")
    discovery_parser.add_argument("--queue", required=True)

    github_parser = subparsers.add_parser(
        "discover-github", help="Discover open-source presentation candidates"
    )
    github_parser.add_argument("--query", action="append", required=True)
    github_parser.add_argument("--per-query", type=int, default=10)
    github_parser.add_argument("--output", "-o")

    arena_parser = subparsers.add_parser("arena", help="Aggregate blinded pairwise reviews")
    arena_parser.add_argument("reviews")
    arena_parser.add_argument("--initial-rating", type=float, default=1000)
    arena_parser.add_argument("--k-factor", type=float, default=24)
    arena_parser.add_argument("--output", "-o")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "inspect":
            if not 0 < args.overlap_threshold <= 1:
                raise ValueError("--overlap-threshold must be in (0, 1]")
            _write_json(
                inspect_pptx(args.pptx, overlap_threshold=args.overlap_threshold), args.output
            )
        elif args.command == "validate":
            errors = validate_path(args.target, args.schema)
            if errors:
                _write_json({"valid": False, "errors": errors}, None)
                return 1
            _write_json({"valid": True, "target": args.target}, None)
        elif args.command == "aggregate":
            _write_json(aggregate(args.submissions), args.output)
        elif args.command == "rank":
            as_of = datetime.fromisoformat(args.as_of.replace("Z", "+00:00")) if args.as_of else None
            _write_json(
                build_rankings(args.evidence, args.products, args.config, as_of=as_of), args.output
            )
        elif args.command == "import-csv":
            records = import_normalized_csv(
                args.input,
                source_id=args.source,
                source_version=args.source_version,
                registry_path=args.registry,
            )
            written = write_evidence_records(records, args.output_dir)
            _write_json({"imported": len(written), "files": written}, None)
        elif args.command == "import-upstream":
            records = import_upstream(
                args.adapter,
                args.input,
                product_snapshot_id=args.product_snapshot,
                source_version=args.source_version,
                registry_path=args.registry,
                observed_at=args.observed_at,
                scenario=args.scenario,
                language=args.language,
            )
            written = write_evidence_records(records, args.output_dir)
            _write_json({"imported": len(written), "files": written}, None)
        elif args.command == "build-site":
            _write_json(build_site(args.rankings, args.products, args.output_dir), None)
        elif args.command == "check-products":
            if args.timeout <= 0 or args.workers <= 0:
                raise ValueError("--timeout and --workers must be positive")
            _write_json(
                check_products(args.products, timeout=args.timeout, workers=args.workers), args.output
            )
        elif args.command == "ingest-discovery":
            _write_json(merge_discoveries(args.input, args.queue), None)
        elif args.command == "discover-github":
            if not 1 <= args.per_query <= 100:
                raise ValueError("--per-query must be between 1 and 100")
            _write_json(discover_github(args.query, per_query=args.per_query), args.output)
        elif args.command == "arena":
            if args.initial_rating <= 0 or args.k_factor <= 0:
                raise ValueError("--initial-rating and --k-factor must be positive")
            _write_json(
                aggregate_elo(
                    args.reviews,
                    initial_rating=args.initial_rating,
                    k_factor=args.k_factor,
                ),
                args.output,
            )
    except (FileNotFoundError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
