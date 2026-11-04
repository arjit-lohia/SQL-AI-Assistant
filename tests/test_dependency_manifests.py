"""Deployment contracts: exact runtime pins without nested file discovery."""
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

from scripts.lock_dependencies import write_manifests

ROOT = Path(__file__).resolve().parents[1]


def pins(path):
    result = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        assert not line.lstrip().startswith("-"), "Runtime requirements must not include another file or pip options"
        req = Requirement(line)
        specs = list(req.specifier)
        assert len(specs) == 1 and specs[0].operator == "==" and "*" not in specs[0].version
        assert not req.url
        key = canonicalize_name(req.name)
        assert key not in result, f"Duplicate runtime dependency: {key}"
        result[key] = (str(req.specifier), str(req.marker) if req.marker else None)
    return result


def test_deployment_manifest_is_flat_and_matches_verified_lock():
    actual = pins(ROOT / "requirements.txt")
    assert actual == pins(ROOT / "requirements.lock")
    assert {"fastapi", "uvicorn", "langgraph", "sqlglot", "httpx", "python-dotenv"} <= actual.keys()


def test_regeneration_keeps_deployment_manifest_self_contained(tmp_path):
    runtime = {"httpx": "httpx==0.28.1", "fastapi": "fastapi==0.162.0"}
    dev = {"pytest": "pytest==9.2.0"}
    (tmp_path / "requirements.txt").write_text("-r requirements.lock\n", encoding="utf-8")
    write_manifests(runtime, dev, root=tmp_path)
    assert (tmp_path / "requirements.txt").read_bytes() == (tmp_path / "requirements.lock").read_bytes()
    assert set(pins(tmp_path / "requirements.txt")) == set(runtime)
    assert "pytest" not in pins(tmp_path / "requirements.txt")
    assert "pytest==9.2.0" in (tmp_path / "requirements-dev.lock").read_text()
