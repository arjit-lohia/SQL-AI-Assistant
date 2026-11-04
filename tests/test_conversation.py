"""Real multi-dialect execution plus independent live-response context checks."""
from contextlib import closing
import pytest
from fastapi.testclient import TestClient
from api.index import app
from backend import database, provider
from backend.context import check_preserved_filters
from backend.models import ModelOutput
from backend.sql import InvalidSQL

client = TestClient(app)
DIALECTS = ["sqlite", "postgres", "mysql"]


@pytest.fixture(autouse=True)
def sample_mode(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)


def ask(message, **kwargs):
    response = client.post("/api/chat", json={"message": message, **kwargs})
    assert response.status_code == 200, response.text
    return response.json()


def turn(response):
    return {"role": "assistant", "content": response["explanation"], "sql": response["sql"], "dialect": response["dialect"]}


@pytest.mark.parametrize("source", DIALECTS)
@pytest.mark.parametrize("target", DIALECTS)
def test_austin_date_refinement_across_dialects(source, target):
    first = ask("Give all people from Austin", dialect=source)
    assert first["status"] == "success"
    second = ask("Show people who joined before 24th Oct, 2024", dialect=target, history=[turn(first)], execute=True)
    assert second["status"] == "success", second
    assert second["dialect"] == target
    assert second["result"]["engine"] == "sqlite"
    with closing(database.connect(False)) as db:
        expected = [list(r) for r in db.execute("SELECT id, name, email, city, state, created_at FROM customers WHERE city='Austin' AND created_at < '2024-10-24'")]
    assert expected and second["result"]["rows"] == expected
    assert any("account creation" in a for a in second["assumptions"])
    third = ask("Sort by name", dialect=target, history=[turn(first), turn(second)], execute=True)
    assert third["status"] == "success" and "2024-10-24" in third["sql"] and "Austin" in third["sql"]
    assert third["result"]["rows"] == sorted(expected, key=lambda r: r[1])


@pytest.mark.parametrize("date", ["2024-10-24", "24 October 2024", "Oct 24, 2024"])
def test_date_formats(date):
    first = ask("Show customers in California")
    second = ask(f"Only those who joined before {date}", history=[turn(first)])
    assert second["status"] == "success"
    assert "California" in second["sql"] and "2024-10-24" in second["sql"]


def test_date_absent_context_invalid_date_and_new_conversation():
    assert ask("Show people who joined before 24th Oct, 2024")["status"] == "clarification"
    first = ask("Give all people from Austin")
    invalid = ask("Show people who joined before 31st Feb, 2024", history=[turn(first)])
    assert invalid["status"] == "clarification" and invalid["sql"] is None
    fresh = ask("Show all customers", history=[turn(first)])
    assert fresh["status"] == "success" and "Austin" not in fresh["sql"]
    assert ask("Only those from California")["status"] == "clarification"


def test_employee_date_preserves_previous_cutoff():
    first = ask("Show all employees hired after January 2024")
    second = ask("Only those hired before 2024-10-24", history=[turn(first)], execute=True)
    assert second["status"] == "success", second
    assert "2024-01-01" in second["sql"] and "2024-10-24" in second["sql"]
    i = second["result"]["columns"].index("hire_date")
    assert second["result"]["rows"] and all("2024-01-01" <= r[i] < "2024-10-24" for r in second["result"]["rows"])


@pytest.mark.parametrize("repaired", [True, False])
def test_live_model_dropped_filter_requires_repair(monkeypatch, repaired):
    first = ask("Give all people from Austin", dialect="mysql")
    monkeypatch.setenv("GROQ_API_KEY", "mock-only")
    calls = []
    async def propose(payload, repair=False):
        calls.append(repair)
        assert "Austin" in payload["previous_sql"]
        assert payload["dialect"] == "postgres"
        if repair:
            assert any("dropped an earlier filter" in d for d in payload["validation_issue"])
        clause = "c.city='Austin' AND " if repair and repaired else ""
        return ModelOutput(status="success", sql=f"SELECT c.name FROM customers c WHERE {clause}c.created_at < '2024-10-24'")
    monkeypatch.setattr(provider, "propose", propose)
    result = ask("Show people who joined before 24th Oct, 2024", dialect="postgres", history=[turn(first)], execute=True)
    assert calls == [False, True]
    if repaired:
        assert result["status"] == "success" and "Austin" in result["sql"]
        assert result["result"] is not None
    else:
        assert result["status"] == "error" and result["sql"] is None and result["result"] is None
        assert "execute_sql" not in result["steps"]


def test_aliases_boolean_conditions_and_deliberate_reset():
    before = "SELECT c.name FROM customers c WHERE c.city='Austin'"
    check_preserved_filters(before, "SELECT x.name FROM customers x WHERE x.city='Austin' AND x.created_at < '2024-10-24'", "Show people who joined before 2024-10-24", "generate")
    with pytest.raises(InvalidSQL, match="dropped"):
        check_preserved_filters(before, "SELECT name FROM customers WHERE city='Austin' OR state='California'", "Only California", "generate")
    check_preserved_filters(before, "SELECT name FROM customers", "Remove the city filter", "generate")
    check_preserved_filters(before, "SELECT name FROM employees", "Show employees", "generate")
    check_preserved_filters(before, "SELECT name FROM customers", "SELECT name FROM customers", "generate")
