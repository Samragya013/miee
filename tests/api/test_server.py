"""Tests for the MIIE REST API server."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from miie.api.dependencies import get_job_store
from miie.api.server import app

_transport = ASGITransport(app=app)


@pytest.fixture
async def client():
    async with AsyncClient(transport=_transport, base_url="http://testserver") as c:
        yield c


class TestHealthEndpoint:
    """GET /v1/health"""

    async def test_health_returns_200(self, client):
        response = await client.get("/v1/health")
        assert response.status_code == 200

    async def test_health_status_healthy(self, client):
        data = response_json(await client.get("/v1/health"))
        assert data["status"] == "healthy"

    async def test_health_version_matches(self, client):
        from miie import __version__

        data = response_json(await client.get("/v1/health"))
        assert data["version"] == __version__

    async def test_health_has_uptime(self, client):
        data = response_json(await client.get("/v1/health"))
        assert "uptime_seconds" in data
        assert isinstance(data["uptime_seconds"], float)
        assert data["uptime_seconds"] >= 0.0


class TestAnalyzeEndpoint:
    """POST /v1/analyze"""

    async def test_analyze_returns_202(self, client):
        response = await client.post(
            "/v1/analyze",
            json={
                "repo": "https://github.com/test/repo.git",
            },
        )
        assert response.status_code == 202

    async def test_analyze_returns_job_id(self, client):
        data = response_json(
            await client.post(
                "/v1/analyze",
                json={
                    "repo": "https://github.com/test/repo.git",
                },
            )
        )
        assert "job_id" in data
        assert data["status"] == "created"
        assert data["poll_url"].startswith("/v1/jobs/")

    async def test_analyze_missing_repo_returns_422(self, client):
        response = await client.post("/v1/analyze", json={})
        assert response.status_code == 422

    async def test_analyze_empty_repo_returns_422(self, client):
        response = await client.post("/v1/analyze", json={"repo": ""})
        assert response.status_code == 422

    async def test_analyze_default_values(self, client):
        data = response_json(
            await client.post(
                "/v1/analyze",
                json={
                    "repo": "https://github.com/test/repo.git",
                },
            )
        )
        job_id = data["job_id"]
        store = get_job_store()
        job = store.get_job(job_id)
        assert job["params"]["window_strategy"] == "time"
        assert job["params"]["window_size"] == 7
        assert job["params"]["seed"] == 42

    async def test_analyze_custom_params(self, client):
        data = response_json(
            await client.post(
                "/v1/analyze",
                json={
                    "repo": "https://github.com/test/repo.git",
                    "metrics": ["M-02"],
                    "detectors": ["D-01"],
                    "window_strategy": "commit",
                    "window_size": 50,
                    "seed": 123,
                },
            )
        )
        job_id = data["job_id"]
        store = get_job_store()
        job = store.get_job(job_id)
        assert job["params"]["metrics"] == ["M-02"]
        assert job["params"]["detectors"] == ["D-01"]
        assert job["params"]["window_strategy"] == "commit"
        assert job["params"]["window_size"] == 50
        assert job["params"]["seed"] == 123


class TestJobStatusEndpoint:
    """GET /v1/jobs/{job_id}"""

    async def test_nonexistent_job_returns_404(self, client):
        fake_id = str(uuid.uuid4())
        response = await client.get(f"/v1/jobs/{fake_id}")
        assert response.status_code == 404

    async def test_404_returns_rfc7807_format(self, client):
        fake_id = str(uuid.uuid4())
        data = response_json(await client.get(f"/v1/jobs/{fake_id}"))
        assert "type" in data
        assert "title" in data
        assert "status" in data
        assert "detail" in data
        assert "instance" in data
        assert data["status"] == 404

    async def test_created_job_returns_status(self, client):
        create_data = response_json(
            await client.post(
                "/v1/analyze",
                json={
                    "repo": "https://github.com/test/repo.git",
                },
            )
        )
        job_id = create_data["job_id"]

        response = await client.get(f"/v1/jobs/{job_id}")
        assert response.status_code in (200, 202)

    async def test_completed_job_returns_200(self, client):
        store = get_job_store()
        job_id = store.create_job("analyze", {"repo": "test"})
        store.set_result(
            job_id,
            {
                "repo_id": "abc123",
                "integrity_overall": 0.95,
                "confidence_overall": 0.80,
                "integrity_per_metric": {"M-02": 0.95},
            },
        )

        response = await client.get(f"/v1/jobs/{job_id}")
        assert response.status_code == 200
        data = response_json(response)
        assert data["status"] == "completed"
        assert "summary" in data

    async def test_failed_job_returns_error(self, client):
        store = get_job_store()
        job_id = store.create_job("analyze", {"repo": "test"})
        store.set_error(
            job_id,
            {
                "type": "https://miie.dev/errors/analysis-failed",
                "title": "Analysis Failed",
                "status": 500,
                "detail": "Test error",
            },
        )

        response = await client.get(f"/v1/jobs/{job_id}")
        assert response.status_code == 500


class TestJobResultsEndpoint:
    """GET /v1/jobs/{job_id}/results"""

    async def test_nonexistent_job_returns_404(self, client):
        fake_id = str(uuid.uuid4())
        response = await client.get(f"/v1/jobs/{fake_id}/results")
        assert response.status_code == 404

    async def test_running_job_returns_409(self, client):
        store = get_job_store()
        job_id = store.create_job("analyze", {"repo": "test"})
        store.update_status(job_id, "running", progress=0.5)

        response = await client.get(f"/v1/jobs/{job_id}/results")
        assert response.status_code == 409

    async def test_completed_job_returns_results(self, client):
        store = get_job_store()
        job_id = store.create_job("analyze", {"repo": "test"})
        result = {
            "repo_id": "abc123",
            "integrity_overall": 0.95,
            "confidence_overall": 0.80,
            "integrity_per_metric": {"M-02": 0.95, "M-06": 0.88},
        }
        store.set_result(job_id, result)

        response = await client.get(f"/v1/jobs/{job_id}/results")
        assert response.status_code == 200
        data = response_json(response)
        assert data["repo_id"] == "abc123"
        assert data["integrity_overall"] == 0.95


class TestBenchmarkEndpoint:
    """POST /v1/benchmark"""

    async def test_benchmark_returns_202(self, client):
        response = await client.post(
            "/v1/benchmark",
            json={
                "suite": "metric-drift-v1",
            },
        )
        assert response.status_code == 202

    async def test_benchmark_returns_job_id(self, client):
        data = response_json(
            await client.post(
                "/v1/benchmark",
                json={
                    "suite": "metric-drift-v1",
                },
            )
        )
        assert "job_id" in data
        assert data["status"] == "created"

    async def test_benchmark_missing_suite_returns_422(self, client):
        response = await client.post("/v1/benchmark", json={})
        assert response.status_code == 422


class TestExplainEndpoint:
    """POST /v1/explain"""

    async def test_explain_nonexistent_job_returns_404(self, client):
        fake_id = str(uuid.uuid4())
        response = await client.post("/v1/explain", json={"job_id": fake_id})
        assert response.status_code == 404

    async def test_explain_running_job_returns_409(self, client):
        store = get_job_store()
        job_id = store.create_job("analyze", {"repo": "test"})
        store.update_status(job_id, "running", progress=0.5)

        response = await client.post("/v1/explain", json={"job_id": job_id})
        assert response.status_code == 409

    async def test_explain_completed_job_returns_200(self, client):
        store = get_job_store()
        job_id = store.create_job("analyze", {"repo": "test"})
        store.set_result(
            job_id,
            {
                "repo_id": "abc",
                "integrity_overall": 0.9,
                "confidence_overall": 0.8,
            },
        )

        response = await client.post("/v1/explain", json={"job_id": job_id})
        assert response.status_code == 200
        data = response_json(response)
        assert "explanation" in data
        assert "metric" in data
        assert "detector" in data

    async def test_explain_missing_job_id_returns_422(self, client):
        response = await client.post("/v1/explain", json={})
        assert response.status_code == 422


class TestExportEndpoint:
    """POST /v1/export"""

    async def test_export_nonexistent_job_returns_404(self, client):
        fake_id = str(uuid.uuid4())
        response = await client.post("/v1/export", json={"job_id": fake_id})
        assert response.status_code == 404

    async def test_export_completed_job_returns_200(self, client):
        store = get_job_store()
        job_id = store.create_job("analyze", {"repo": "test"})
        store.set_result(job_id, {"repo_id": "abc"})

        response = await client.post("/v1/export", json={"job_id": job_id})
        assert response.status_code == 200
        data = response_json(response)
        assert "download_urls" in data
        assert "json" in data["download_urls"]
        assert "md" in data["download_urls"]

    async def test_export_custom_formats(self, client):
        store = get_job_store()
        job_id = store.create_job("analyze", {"repo": "test"})
        store.set_result(job_id, {"repo_id": "abc"})

        response = await client.post(
            "/v1/export",
            json={
                "job_id": job_id,
                "formats": ["json", "csv"],
            },
        )
        data = response_json(response)
        assert "json" in data["download_urls"]
        assert "csv" in data["download_urls"]
        assert "md" not in data["download_urls"]

    async def test_export_missing_job_id_returns_422(self, client):
        response = await client.post("/v1/export", json={})
        assert response.status_code == 422


class TestRFC7807ErrorFormat:
    """Verify all error responses follow RFC 7807 Problem Details."""

    async def test_404_has_rfc7807_fields(self, client):
        fake_id = str(uuid.uuid4())
        data = response_json(await client.get(f"/v1/jobs/{fake_id}"))
        for field in ("type", "title", "status", "detail", "instance"):
            assert field in data, f"Missing RFC 7807 field: {field}"
        assert data["status"] == 404

    async def test_422_has_error_detail(self, client):
        response = await client.post("/v1/analyze", json={})
        assert response.status_code == 422

    async def test_type_is_uri(self, client):
        fake_id = str(uuid.uuid4())
        data = response_json(await client.get(f"/v1/jobs/{fake_id}"))
        assert data["type"].startswith("https://")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def response_json(response):
    """Extract JSON from a TestClient response, failing on non-2xx."""
    assert response.status_code < 500, f"Server error {response.status_code}: {response.text}"
    return response.json()
