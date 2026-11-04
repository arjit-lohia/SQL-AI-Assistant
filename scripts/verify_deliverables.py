"""Audit the six local deliverables and their specification/document links."""
import json
from contextlib import closing
import re
import sqlite3
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
GROUPS = {
    "complete_source": ["src/App.tsx", "src/lib.ts", "api/index.py", "backend/agent.py", "backend/context.py", "backend/provider.py", "backend/sql.py", "backend/database.py", "backend/models.py", "scripts/seed.py", "tests/test_sql.py", "tests/test_agent_api.py", "tests/test_conversation.py", "tests/browser/app.spec.ts", "package-lock.json", "requirements.lock"],
    "setup_readme": ["README.md", "docs/setup.md", ".env.example"],
    "architecture": ["docs/architecture.svg", "docs/architecture.mmd", "docs/architecture.md"],
    "workflow": ["docs/workflow.md", "specs/08-agent-and-prompts.md"],
    "runtime_prompts": ["prompts/system.txt", "prompts/repair.txt"],
    "sample_schema": ["data/schema.sql", "data/sample.db", "docs/database.md", "scripts/seed.py"],
}


def audit():
    for files in GROUPS.values():
        for name in files:
            path = ROOT / name
            assert path.is_file() and path.stat().st_size, f"Missing/empty deliverable: {name}"

    documents = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md")), *sorted((ROOT / "specs").glob("*.md")), *sorted((ROOT / "artifacts").glob("*.md"))]
    local_links = 0
    for document in documents:
        for raw in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
            target = raw.strip().strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            local_links += 1
            resolved = (document.parent / unquote(parsed.path)).resolve()
            assert resolved.is_relative_to(ROOT) and resolved.exists(), f"Broken local link: {document.relative_to(ROOT)} -> {target}"

    diagram = ET.parse(ROOT / "docs/architecture.svg").getroot()
    assert diagram.tag == "{http://www.w3.org/2000/svg}svg"
    assert "flowchart" in (ROOT / "docs/architecture.mmd").read_text(encoding="utf-8")

    from backend.agent import GRAPH
    expected_nodes = {"detect_intent", "validate_scope", "retrieve_schema", "generate_sql", "validate_sql", "repair_sql", "optimize_sql", "execute_sql", "explain_sql"}
    assert expected_nodes <= set(GRAPH.get_graph().nodes)
    workflow = (ROOT / "docs/workflow.md").read_text(encoding="utf-8")
    assert all(node in workflow for node in expected_nodes)
    provider_source = (ROOT / "backend/provider.py").read_text(encoding="utf-8")
    assert all(name in provider_source for name in ["prompts/system.txt", "prompts/repair.txt"])

    from backend import database
    with closing(sqlite3.connect(":memory:")) as scratch:
        scratch.executescript((ROOT / "data/schema.sql").read_text(encoding="utf-8"))
        declared_tables = {row[0] for row in scratch.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    actual = database.schema()
    assert declared_tables == {table["name"] for table in actual["tables"]}
    assert len(declared_tables) == 6
    assert sum(len(table["foreign_keys"]) for table in actual["tables"]) == 5
    with closing(database.connect(False)) as db:
        assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert not db.execute("PRAGMA foreign_key_check").fetchall()

    report = {"status": "passed", "deliverables": {key: {"status": "present", "artifacts": files} for key, files in GROUPS.items()}, "markdown_documents": len(documents), "valid_local_links": local_links, "diagram": "valid SVG and Mermaid source", "langgraph_nodes": sorted(expected_nodes), "runtime_prompts": "source files loaded by provider", "schema_tables": sorted(declared_tables), "foreign_keys": 5, "rows": sum(t["row_count"] for t in actual["tables"]), "database_integrity": "ok"}
    (ROOT / "artifacts/deliverable-audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: six deliverables, {local_links} local links, valid architecture, nine LangGraph nodes, two runtime prompts, six schema tables/five foreign keys")


if __name__ == "__main__":
    audit()
