#!/usr/bin/env python3
"""Validate, build, and search All in One's portable, offline backend library."""

import argparse
from contextlib import closing
from datetime import date
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sqlite3
import sys
import tempfile
from urllib.parse import urlsplit


DOMAINS = ("architecture", "agents", "pipelines", "algorithms", "data", "security", "verification", "delivery", "debugging")
SCHEMA_VERSION = 1
DATABASE_NAME = "backend-knowledge.sqlite"
DEFAULT_DATA_DIR = Path(__file__).resolve().parents[1] / "knowledge"
STOP_WORDS = frozenset("a an and are as at be by do for from how i in is it of on or the to with".split())
WORD_FORMS = {"idempotency": "idempoten", "idempotent": "idempoten", "recovery": "recover"}
IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


class KnowledgeError(ValueError):
    """A source, database, or query cannot be used safely."""


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise KnowledgeError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path):
    try:
        def reject_constant(value):
            raise KnowledgeError(f"Invalid JSON number: {value}")

        return json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_object, parse_constant=reject_constant)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise KnowledgeError(f"Cannot read {path.name}: {error}") from error


def string(value, context):
    if not isinstance(value, str) or not value.strip():
        raise KnowledgeError(f"{context} must be a nonempty string")
    return value


def identifier(value, context):
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise KnowledgeError(f"{context} must use lowercase letters, digits, dots, underscores, or hyphens")
    return value


def string_list(value, context):
    if not isinstance(value, list) or not value:
        raise KnowledgeError(f"{context} must be a nonempty list of strings")
    for index, item in enumerate(value):
        string(item, f"{context}[{index}]")
    if len(value) != len(set(value)):
        raise KnowledgeError(f"{context} contains duplicates")
    return value


def collection(document, name):
    if not isinstance(document, dict) or type(document.get("schema_version")) is not int or document["schema_version"] != SCHEMA_VERSION:
        raise KnowledgeError(f"{name} schema_version must be {SCHEMA_VERSION}")
    items = document.get(name)
    if not isinstance(items, list) or not items:
        raise KnowledgeError(f"{name} must be a nonempty list")
    return items


def validate_sources(document):
    sources = collection(document, "sources")
    reviewed_on = string(document.get("reviewed_on"), "reviewed_on")
    try:
        if date.fromisoformat(reviewed_on).isoformat() != reviewed_on:
            raise ValueError("not an ISO date")
    except ValueError as error:
        raise KnowledgeError("reviewed_on must use YYYY-MM-DD") from error
    seen = set()
    for item in sources:
        if not isinstance(item, dict):
            raise KnowledgeError("Each source must be an object")
        source_id = identifier(item.get("id"), "Source id")
        if source_id in seen:
            raise KnowledgeError(f"Duplicate source id: {source_id}")
        seen.add(source_id)
        for key in ("name", "license", "url"):
            string(item.get(key), f"Source {source_id}.{key}")
        try:
            url = urlsplit(item["url"])
            url.port
        except ValueError as error:
            raise KnowledgeError(f"Source {source_id}.url is malformed") from error
        if url.scheme not in ("http", "https") or not url.hostname or url.username or url.password:
            raise KnowledgeError(f"Source {source_id}.url must be a public HTTP(S) URL")
    return sources


def validate_playbook(value, skill_dir, context):
    value = string(value, context)
    relative = PurePosixPath(value)
    if "\\" in value or relative.is_absolute() or len(relative.parts) < 2 or relative.parts[0] != "references" or any(part in (".", "..") for part in value.split("/")) or relative.suffix != ".md":
        raise KnowledgeError(f"{context} must be a contained references/*.md path")
    target = (skill_dir / Path(*relative.parts)).resolve()
    if not target.is_relative_to(skill_dir.resolve()) or not target.is_file():
        raise KnowledgeError(f"{context} is missing or escapes the skill directory: {value}")


def load_library(data_dir):
    source_document = read_json(data_dir / "sources.json")
    sources = validate_sources(source_document)
    pattern_document = read_json(data_dir / "backend-knowledge.json")
    patterns = collection(pattern_document, "patterns")
    source_ids = {source["id"] for source in sources}
    seen = set()
    for pattern in patterns:
        if not isinstance(pattern, dict):
            raise KnowledgeError("Each pattern must be an object")
        pattern_id = identifier(pattern.get("id"), "Pattern id")
        if pattern_id in seen:
            raise KnowledgeError(f"Duplicate pattern id: {pattern_id}")
        seen.add(pattern_id)
        if pattern.get("domain") not in DOMAINS:
            raise KnowledgeError(f"Pattern {pattern_id} has an unknown domain")
        for key in ("title", "problem", "when_to_use", "approach"):
            string(pattern.get(key), f"Pattern {pattern_id}.{key}")
        for key in ("failure_modes", "verification", "source_ids"):
            string_list(pattern.get(key), f"Pattern {pattern_id}.{key}")
        unknown = set(pattern["source_ids"]) - source_ids
        if unknown:
            raise KnowledgeError(f"Pattern {pattern_id} has unknown source ids: {', '.join(sorted(unknown))}")
        if "tags" in pattern:
            string_list(pattern["tags"], f"Pattern {pattern_id}.tags")
        validate_playbook(pattern.get("playbook"), data_dir.parent, f"Pattern {pattern_id}.playbook")
    return source_document, pattern_document


def searchable_fields(pattern):
    fields = [(pattern["title"], 12), (pattern["problem"], 8), (pattern["when_to_use"], 4), (pattern["approach"], 4)]
    fields.extend((" ".join(pattern[key]), 3) for key in ("failure_modes", "verification"))
    fields.extend((" ".join(pattern.get(key, [])), 2) for key in ("tags", "source_ids"))
    fields.extend([(pattern["domain"], 2), (pattern["id"], 1), (pattern["playbook"], 1)])
    return [(value.casefold(), weight) for value, weight in fields]


def searchable_text(pattern):
    return "\n".join(value for value, _ in searchable_fields(pattern))


def expected_metadata(source_document, pattern_document):
    return {"schema_version": str(SCHEMA_VERSION), "sources_sha256": digest(source_document), "patterns_sha256": digest(pattern_document)}


def build(data_dir, force=False):
    source_document, pattern_document = load_library(data_dir)
    destination = data_dir / DATABASE_NAME
    if destination.exists() and not force:
        raise KnowledgeError(f"{DATABASE_NAME} already exists; use build --force to replace it")
    if destination.is_dir():
        raise KnowledgeError(f"Database destination is a directory: {destination}")
    descriptor, temporary_name = tempfile.mkstemp(prefix=".knowledge-build-", suffix=".sqlite", dir=data_dir)
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        with closing(sqlite3.connect(temporary)) as connection, connection:
            connection.executescript("""
                PRAGMA user_version = 1;
                CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE sources (id TEXT PRIMARY KEY, record_json TEXT NOT NULL);
                CREATE TABLE patterns (
                    id TEXT PRIMARY KEY, domain TEXT NOT NULL, title TEXT NOT NULL,
                    problem TEXT NOT NULL, record_json TEXT NOT NULL, search_text TEXT NOT NULL
                );
                CREATE INDEX patterns_domain ON patterns(domain);
            """)
            connection.executemany("INSERT INTO metadata VALUES (?, ?)", sorted(expected_metadata(source_document, pattern_document).items()))
            connection.executemany("INSERT INTO sources VALUES (?, ?)", [(source["id"], canonical(source)) for source in sorted(source_document["sources"], key=lambda item: item["id"])])
            connection.executemany("INSERT INTO patterns VALUES (?, ?, ?, ?, ?, ?)", [(pattern["id"], pattern["domain"], pattern["title"], pattern["problem"], canonical(pattern), searchable_text(pattern)) for pattern in sorted(pattern_document["patterns"], key=lambda item: item["id"])])
        if force:
            os.replace(temporary, destination)
        else:
            # Publishing a hard link is atomic and refuses a concurrent existing target.
            try:
                os.link(temporary, destination)
            except FileExistsError as error:
                raise KnowledgeError(f"{DATABASE_NAME} already exists; use build --force to replace it") from error
        return len(pattern_document["patterns"]), len(source_document["sources"])
    finally:
        temporary.unlink(missing_ok=True)


def open_database(data_dir):
    path = data_dir / DATABASE_NAME
    if not path.is_file():
        raise KnowledgeError(f"Missing {DATABASE_NAME}; run knowledge.py build first")
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        connection.execute("PRAGMA query_only = ON")
        if connection.execute("PRAGMA user_version").fetchone()[0] != SCHEMA_VERSION:
            raise KnowledgeError("Unsupported database schema; rebuild from canonical JSON")
        return connection
    except Exception:
        connection.close()
        raise


def check(data_dir):
    source_document, pattern_document = load_library(data_dir)
    connection = open_database(data_dir)
    try:
        if connection.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
            raise KnowledgeError("SQLite integrity check failed")
        metadata = dict(connection.execute("SELECT key, value FROM metadata"))
        if metadata != expected_metadata(source_document, pattern_document):
            raise KnowledgeError("Database metadata differs from canonical JSON; run build --force")
        actual_sources = dict(connection.execute("SELECT id, record_json FROM sources"))
        expected_sources = {item["id"]: canonical(item) for item in source_document["sources"]}
        if actual_sources != expected_sources:
            raise KnowledgeError("Database source records differ from canonical JSON")
        actual_patterns = {row[0]: row[1:] for row in connection.execute("SELECT id, domain, title, problem, record_json, search_text FROM patterns")}
        expected_patterns = {item["id"]: (item["domain"], item["title"], item["problem"], canonical(item), searchable_text(item)) for item in pattern_document["patterns"]}
        if actual_patterns != expected_patterns:
            raise KnowledgeError("Database pattern records differ from canonical JSON")
    finally:
        connection.close()
    return len(pattern_document["patterns"]), len(source_document["sources"])


def query_tokens(query):
    if len(query) > 1000:
        raise KnowledgeError("Search query must contain at most 1000 characters")
    words = set(re.findall(r"[^\W_]+", query.casefold())) - STOP_WORDS
    tokens = sorted({WORD_FORMS.get(word, word) for word in words})
    if not tokens:
        raise KnowledgeError("Search query must contain a word other than common stop words")
    if len(tokens) > 32:
        raise KnowledgeError("Search query must contain at most 32 distinct words")
    return tokens


def search(data_dir, query, domain=None, limit=5):
    tokens = query_tokens(query)
    # Prefixes find "recover" in "recovery" without finding "table" in "stable".
    terms = [re.compile(r"(?<!\w)" + re.escape(token)) for token in tokens]
    connection = open_database(data_dir)
    try:
        clauses = " OR ".join("search_text LIKE ?" for _ in tokens)
        parameters = [f"%{token}%" for token in tokens]
        statement = f"SELECT record_json FROM patterns WHERE ({clauses})"
        if domain:
            statement += " AND domain = ?"
            parameters.append(domain)
        source_map = {source_id: json.loads(record) for source_id, record in connection.execute("SELECT id, record_json FROM sources")}
        matches = []
        for (record,) in connection.execute(statement, parameters):
            pattern = json.loads(record)
            fields = searchable_fields(pattern)
            score = sum(weight for value, weight in fields for term in terms if term.search(value))
            if not score:
                continue
            pattern["score"] = score
            pattern["matched_terms"] = sum(any(term.search(value) for value, _ in fields) for term in terms)
            pattern["sources"] = [source_map[source_id] for source_id in pattern["source_ids"]]
            matches.append(pattern)
        matches.sort(key=lambda pattern: (-pattern["matched_terms"], -pattern["score"], pattern["id"]))
        return matches[:limit]
    finally:
        connection.close()


def positive_limit(value):
    try:
        limit = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("limit must be an integer from 1 to 100") from error
    if not 1 <= limit <= 100:
        raise argparse.ArgumentTypeError("limit must be an integer from 1 to 100")
    return limit


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR, help="Directory containing canonical JSON and SQLite; defaults to the bundled knowledge directory")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("build", "search", "sources", "check"):
        child = subparsers.add_parser(command)
        child.add_argument("--data-dir", type=Path, default=argparse.SUPPRESS, help=argparse.SUPPRESS)
        if command == "build":
            child.add_argument("--force", action="store_true", help="Atomically replace an existing database")
        if command == "search":
            child.add_argument("query")
            child.add_argument("--domain", choices=DOMAINS)
            child.add_argument("--limit", type=positive_limit, default=5)
        if command in ("search", "sources"):
            child.add_argument("--json", action="store_true", help="Emit structured JSON")
    return parser.parse_args()


def main():
    args = parse_args()
    data_dir = args.data_dir.resolve()
    try:
        if args.command in ("build", "check"):
            counts = build(data_dir, args.force) if args.command == "build" else check(data_dir)
            verb = "Built" if args.command == "build" else "Validated"
            print(f"{verb} {counts[0]} patterns and {counts[1]} sources: {data_dir / DATABASE_NAME}")
        elif args.command == "sources":
            result = validate_sources(read_json(data_dir / "sources.json"))
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                for item in result:
                    print(f"{item['id']}: {item['name']}\n  {item['url']}")
        else:
            result = search(data_dir, args.query, args.domain, args.limit)
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            elif not result:
                print("No matching backend patterns.")
            else:
                for item in result:
                    print(f"{item['id']} [{item['domain']}] {item['title']}\n  Problem: {item['problem']}\n  Approach: {item['approach']}\n  Playbook: {item['playbook']}")
                    for source in item["sources"]:
                        print(f"  Source: {source['url']}")
        return 0
    except (KnowledgeError, OSError, sqlite3.Error, KeyError, TypeError, json.JSONDecodeError) as error:
        print(f"Knowledge error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
