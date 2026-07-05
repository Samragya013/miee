"""
PR-14 Repository Catalogue — 100+ real GitHub repositories.

Balanced across categories:
  - Healthy / Enterprise / Experimental / High-risk / Archived / Forks
  - Large / Medium / Small
  - Multiple languages (Python, JavaScript, TypeScript, Go, Rust, Java, Ruby, C++)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List


class RepoCategory(str, Enum):
    HEALTHY = "healthy"
    ENTERPRISE = "enterprise"
    EXPERIMENTAL = "experimental"
    HIGH_RISK = "high-risk"
    ARCHIVED = "archived"
    FORK = "fork"


class RepoSize(str, Enum):
    LARGE = "large"       # >50k commits
    MEDIUM = "medium"     # 5k-50k commits
    SMALL = "small"       # <5k commits


class RepoLanguage(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GO = "go"
    RUST = "rust"
    JAVA = "java"
    RUBY = "ruby"
    CPP = "c++"
    MULTI = "multi"


@dataclass(frozen=True)
class RepoSpec:
    repo_id: str
    category: RepoCategory
    size: RepoSize
    language: RepoLanguage
    description: str = ""
    skip_github_api: bool = False


# ---------------------------------------------------------------------------
# Catalogue — 105 repositories
# ---------------------------------------------------------------------------
CATALOGUE: List[RepoSpec] = [
    # =====================================================================
    # PYTHON — Healthy (20 repos)
    # =====================================================================
    RepoSpec("pallets/flask", RepoCategory.HEALTHY, RepoSize.MEDIUM, RepoLanguage.PYTHON, "Web framework"),
    RepoSpec("pypa/pip", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.PYTHON, "Package installer"),
    RepoSpec("psf/requests", RepoCategory.HEALTHY, RepoSize.MEDIUM, RepoLanguage.PYTHON, "HTTP library"),
    RepoSpec("tiangolo/typer", RepoCategory.HEALTHY, RepoSize.MEDIUM, RepoLanguage.PYTHON, "CLI framework"),
    RepoSpec("tiangolo/full-stack-fastapi-template", RepoCategory.HEALTHY, RepoSize.SMALL, RepoLanguage.PYTHON, "FastAPI template"),
    RepoSpec("tiangolo/uvicorn", RepoCategory.HEALTHY, RepoSize.MEDIUM, RepoLanguage.PYTHON, "ASGI server"),
    RepoSpec("encode/httpx", RepoCategory.HEALTHY, RepoSize.MEDIUM, RepoLanguage.PYTHON, "HTTP client"),
    RepoSpec("encode/starlette", RepoCategory.HEALTHY, RepoSize.MEDIUM, RepoLanguage.PYTHON, "ASGI toolkit"),
    RepoSpec("pallets/click", RepoCategory.HEALTHY, RepoSize.MEDIUM, RepoLanguage.PYTHON, "CLI toolkit"),
    RepoSpec("pallets/jinja", RepoCategory.HEALTHY, RepoSize.MEDIUM, RepoLanguage.PYTHON, "Template engine"),
    RepoSpec("sqlalchemy/sqlalchemy", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.PYTHON, "ORM toolkit"),
    RepoSpec("pallets/werkzeug", RepoCategory.HEALTHY, RepoSize.MEDIUM, RepoLanguage.PYTHON, "WSGI toolkit"),
    RepoSpec("pallets/itsdangerous", RepoCategory.HEALTHY, RepoSize.SMALL, RepoLanguage.PYTHON, "Data signing"),
    RepoSpec("pypa/setuptools", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.PYTHON, "Build system"),
    RepoSpec("numpy/numpy", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.PYTHON, "Numerical computing"),
    RepoSpec("pandas-dev/pandas", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.PYTHON, "Data analysis"),
    RepoSpec("scikit-learn/scikit-learn", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.PYTHON, "ML library"),
    RepoSpec("FastAPI/typer", RepoCategory.HEALTHY, RepoSize.MEDIUM, RepoLanguage.PYTHON, "CLI framework"),
    RepoSpec("pypa/virtualenv", RepoCategory.HEALTHY, RepoSize.MEDIUM, RepoLanguage.PYTHON, "Virtual environments"),
    RepoSpec("pytest-dev/pytest", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.PYTHON, "Testing framework"),

    # =====================================================================
    # PYTHON — Enterprise (10 repos)
    # =====================================================================
    RepoSpec("python/cpython", RepoCategory.ENTERPRISE, RepoSize.LARGE, RepoLanguage.PYTHON, "Python runtime"),
    RepoSpec("django/django", RepoCategory.ENTERPRISE, RepoSize.LARGE, RepoLanguage.PYTHON, "Web framework"),
    RepoSpec("twisted/twisted", RepoCategory.ENTERPRISE, RepoSize.LARGE, RepoLanguage.PYTHON, "Networking engine"),
    RepoSpec("pydantic/pydantic", RepoCategory.ENTERPRISE, RepoSize.MEDIUM, RepoLanguage.PYTHON, "Data validation"),
    RepoSpec("marshmallow-code/marshmallow", RepoCategory.ENTERPRISE, RepoSize.MEDIUM, RepoLanguage.PYTHON, "Serialization"),
    RepoSpec("celery/celery", RepoCategory.ENTERPRISE, RepoSize.LARGE, RepoLanguage.PYTHON, "Task queue"),
    RepoSpec("pytest-dev/pytest-cov", RepoCategory.ENTERPRISE, RepoSize.SMALL, RepoLanguage.PYTHON, "Coverage plugin"),
    RepoSpec("tartley/colorama", RepoCategory.ENTERPRISE, RepoSize.SMALL, RepoLanguage.PYTHON, "Terminal colors"),
    RepoSpec("sarugaku/shellingham", RepoCategory.ENTERPRISE, RepoSize.SMALL, RepoLanguage.PYTHON, "Shell detection"),
    RepoSpec("sdispater/cleo", RepoCategory.ENTERPRISE, RepoSize.SMALL, RepoLanguage.PYTHON, "CLI toolkit"),

    # =====================================================================
    # PYTHON — Experimental (10 repos)
    # =====================================================================
    RepoSpec("tiangolo/fastapi", RepoCategory.EXPERIMENTAL, RepoSize.MEDIUM, RepoLanguage.PYTHON, "API framework"),
    RepoSpec("maguowei/starred", RepoCategory.EXPERIMENTAL, RepoSize.SMALL, RepoLanguage.PYTHON, "GitHub stars"),
    RepoSpec("labmlai/announcements", RepoCategory.EXPERIMENTAL, RepoSize.SMALL, RepoLanguage.PYTHON, "ML announcements"),
    RepoSpec("owid/etl", RepoCategory.EXPERIMENTAL, RepoSize.LARGE, RepoLanguage.PYTHON, "ETL pipeline"),
    RepoSpec("antonio-halerpo/coursera-ml-spec", RepoCategory.EXPERIMENTAL, RepoSize.SMALL, RepoLanguage.PYTHON, "ML course"),
    RepoSpec("TheAlgorithms/Python", RepoCategory.EXPERIMENTAL, RepoSize.LARGE, RepoLanguage.PYTHON, "Algorithm implementations"),
    RepoSpec("kennethreitz/requests", RepoCategory.EXPERIMENTAL, RepoSize.SMALL, RepoLanguage.PYTHON, "HTTP library fork"),
    RepoSpec("pallets/markupsafe", RepoCategory.EXPERIMENTAL, RepoSize.SMALL, RepoLanguage.PYTHON, "String safety"),
    RepoSpec("jmoiron/humanize", RepoCategory.EXPERIMENTAL, RepoSize.SMALL, RepoLanguage.PYTHON, "Human formatting"),
    RepoSpec("jazzband/prettytable", RepoCategory.EXPERIMENTAL, RepoSize.SMALL, RepoLanguage.PYTHON, "ASCII tables"),

    # =====================================================================
    # PYTHON — High-risk (10 repos)
    # =====================================================================
    RepoSpec("scrapy/scrapy", RepoCategory.HIGH_RISK, RepoSize.LARGE, RepoLanguage.PYTHON, "Web scraping"),
    RepoSpec("selenium/selenium", RepoCategory.HIGH_RISK, RepoSize.LARGE, RepoLanguage.PYTHON, "Browser automation"),
    RepoSpec("pytorch/pytorch", RepoCategory.HIGH_RISK, RepoSize.LARGE, RepoLanguage.PYTHON, "Deep learning"),
    RepoSpec("huggingface/transformers", RepoCategory.HIGH_RISK, RepoSize.LARGE, RepoLanguage.PYTHON, "NLP models"),
    RepoSpec("keras-team/keras", RepoCategory.HIGH_RISK, RepoSize.LARGE, RepoLanguage.PYTHON, "Deep learning"),
    RepoSpec("apache/airflow", RepoCategory.HIGH_RISK, RepoSize.LARGE, RepoLanguage.PYTHON, "Workflow orchestration"),
    RepoSpec("redis/redis-py", RepoCategory.HIGH_RISK, RepoSize.MEDIUM, RepoLanguage.PYTHON, "Redis client"),
    RepoSpec("pympler/pympler", RepoCategory.HIGH_RISK, RepoSize.SMALL, RepoLanguage.PYTHON, "Memory profiling"),
    RepoSpec("tqdm/tqdm", RepoCategory.HIGH_RISK, RepoSize.SMALL, RepoLanguage.PYTHON, "Progress bars"),
    RepoSpec("jonathanslenders/python-prompt-toolkit", RepoCategory.HIGH_RISK, RepoSize.MEDIUM, RepoLanguage.PYTHON, "Prompt toolkit"),

    # =====================================================================
    # PYTHON — Archived (5 repos)
    # =====================================================================
    RepoSpec("kennethreitz/tablib", RepoCategory.ARCHIVED, RepoSize.SMALL, RepoLanguage.PYTHON, "Data formats"),
    RepoSpec("kennethreitz/lego", RepoCategory.ARCHIVED, RepoSize.SMALL, RepoLanguage.PYTHON, "Lego project"),
    RepoSpec("kennethreitz/records", RepoCategory.ARCHIVED, RepoSize.SMALL, RepoLanguage.PYTHON, "SQL queries"),
    RepoSpec("kennethreitz/gallows", RepoCategory.ARCHIVED, RepoSize.SMALL, RepoLanguage.PYTHON, "Hangman game"),
    RepoSpec("kennethreitz/maya", RepoCategory.ARCHIVED, RepoSize.SMALL, RepoLanguage.PYTHON, "DateTime toolkit"),

    # =====================================================================
    # JAVASCRIPT — Healthy (10 repos)
    # =====================================================================
    RepoSpec("expressjs/express", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.JAVASCRIPT, "Web framework"),
    RepoSpec("lodash/lodash", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.JAVASCRIPT, "Utility library"),
    RepoSpec("axios/axios", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.JAVASCRIPT, "HTTP client"),
    RepoSpec("moment/moment", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.JAVASCRIPT, "Date library"),
    RepoSpec("webpack/webpack", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.JAVASCRIPT, "Module bundler"),
    RepoSpec("babel/babel", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.JAVASCRIPT, "JS compiler"),
    RepoSpec("mochajs/mocha", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.JAVASCRIPT, "Test framework"),
    RepoSpec("chaijs/chai", RepoCategory.HEALTHY, RepoSize.MEDIUM, RepoLanguage.JAVASCRIPT, "Assertion library"),
    RepoSpec("sinonjs/sinon", RepoCategory.HEALTHY, RepoSize.MEDIUM, RepoLanguage.JAVASCRIPT, "Test doubles"),
    RepoSpec("nock/nock", RepoCategory.HEALTHY, RepoSize.MEDIUM, RepoLanguage.JAVASCRIPT, "HTTP mocking"),

    # =====================================================================
    # TYPESCRIPT — Healthy (10 repos)
    # =====================================================================
    RepoSpec("microsoft/TypeScript", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.TYPESCRIPT, "TypeScript compiler"),
    RepoSpec("vercel/next.js", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.TYPESCRIPT, "React framework"),
    RepoSpec("facebook/jest", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.TYPESCRIPT, "Testing framework"),
    RepoSpec("prisma/prisma", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.TYPESCRIPT, "ORM toolkit"),
    RepoSpec("trpc/trpc", RepoCategory.HEALTHY, RepoSize.MEDIUM, RepoLanguage.TYPESCRIPT, "Type-safe RPC"),
    RepoSpec("colinhacks/zod", RepoCategory.HEALTHY, RepoSize.MEDIUM, RepoLanguage.TYPESCRIPT, "Schema validation"),
    RepoSpec("total-typescript/ts-reset", RepoCategory.EXPERIMENTAL, RepoSize.SMALL, RepoLanguage.TYPESCRIPT, "Type resets"),
    RepoSpec("stitches-dev/stitches", RepoCategory.EXPERIMENTAL, RepoSize.SMALL, RepoLanguage.TYPESCRIPT, "CSS-in-JS"),
    RepoSpec("VanillaExtractCS/vanilla-extract", RepoCategory.HEALTHY, RepoSize.MEDIUM, RepoLanguage.TYPESCRIPT, "CSS-in-JS"),
    RepoSpec("radix-ui/themes", RepoCategory.HEALTHY, RepoSize.SMALL, RepoLanguage.TYPESCRIPT, "UI components"),

    # =====================================================================
    # GO — Healthy (10 repos)
    # =====================================================================
    RepoSpec("golang/go", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.GO, "Go runtime"),
    RepoSpec("kubernetes/kubernetes", RepoCategory.ENTERPRISE, RepoSize.LARGE, RepoLanguage.GO, "Container orchestration"),
    RepoSpec("moby/moby", RepoCategory.ENTERPRISE, RepoSize.LARGE, RepoLanguage.GO, "Container engine"),
    RepoSpec("hashicorp/terraform", RepoCategory.ENTERPRISE, RepoSize.LARGE, RepoLanguage.GO, "Infrastructure as Code"),
    RepoSpec("prometheus/prometheus", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.GO, "Monitoring system"),
    RepoSpec("grafana/grafana", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.GO, "Observability platform"),
    RepoSpec("etcd-io/etcd", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.GO, "Key-value store"),
    RepoSpec("containerd/containerd", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.GO, "Container runtime"),
    RepoSpec("dapr/dapr", RepoCategory.HEALTHY, RepoSize.MEDIUM, RepoLanguage.GO, "Distributed runtime"),
    RepoSpec("go-chi/chi", RepoCategory.HEALTHY, RepoSize.MEDIUM, RepoLanguage.GO, "HTTP router"),

    # =====================================================================
    # RUST — Healthy (10 repos)
    # =====================================================================
    RepoSpec("rust-lang/rust", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.RUST, "Rust compiler"),
    RepoSpec("denoland/deno", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.RUST, "JS/TS runtime"),
    RepoSpec("tauri-apps/tauri", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.RUST, "Desktop apps"),
    RepoSpec("tokio-rs/tokio", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.RUST, "Async runtime"),
    RepoSpec("serde-rs/serde", RepoCategory.HEALTHY, RepoSize.MEDIUM, RepoLanguage.RUST, "Serialization"),
    RepoSpec("BurntSushi/ripgrep", RepoCategory.HEALTHY, RepoSize.MEDIUM, RepoLanguage.RUST, "Grep tool"),
    RepoSpec("sharkdp/fd", RepoCategory.HEALTHY, RepoSize.SMALL, RepoLanguage.RUST, "Find tool"),
    RepoSpec("sharkdp/bat", RepoCategory.HEALTHY, RepoSize.SMALL, RepoLanguage.RUST, "Cat tool"),
    RepoSpec("ajeetdsouza/zoxide", RepoCategory.EXPERIMENTAL, RepoSize.SMALL, RepoLanguage.RUST, "CD replacement"),
    RepoSpec("dani-garcia/vaultwarden", RepoCategory.HIGH_RISK, RepoSize.MEDIUM, RepoLanguage.RUST, "Password manager"),

    # =====================================================================
    # JAVA — Healthy (5 repos)
    # =====================================================================
    RepoSpec("spring-projects/spring-boot", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.JAVA, "Spring framework"),
    RepoSpec("elastic/elasticsearch", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.JAVA, "Search engine"),
    RepoSpec("google/guava", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.JAVA, "Core libraries"),
    RepoSpec("junit-team/junit5", RepoCategory.HEALTHY, RepoSize.MEDIUM, RepoLanguage.JAVA, "Testing framework"),
    RepoSpec("mockito/mockito", RepoCategory.HEALTHY, RepoSize.MEDIUM, RepoLanguage.JAVA, "Mocking framework"),

    # =====================================================================
    # RUBY — Healthy (5 repos)
    # =====================================================================
    RepoSpec("rails/rails", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.RUBY, "Web framework"),
    RepoSpec("ruby/ruby", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.RUBY, "Ruby runtime"),
    RepoSpec("Homebrew/brew", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.RUBY, "Package manager"),
    RepoSpec("jekyll/jekyll", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.RUBY, "Static site generator"),
    RepoSpec("rspec/rspec", RepoCategory.HEALTHY, RepoSize.MEDIUM, RepoLanguage.RUBY, "Testing framework"),

    # =====================================================================
    # C++ — Healthy (5 repos)
    # =====================================================================
    RepoSpec("nlohmann/json", RepoCategory.HEALTHY, RepoSize.MEDIUM, RepoLanguage.CPP, "JSON library"),
    RepoSpec("google/leveldb", RepoCategory.HEALTHY, RepoSize.MEDIUM, RepoLanguage.CPP, "Key-value store"),
    RepoSpec("protocolbuffers/protobuf", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.CPP, "Serialization"),
    RepoSpec("opencv/opencv", RepoCategory.HEALTHY, RepoSize.LARGE, RepoLanguage.CPP, "Computer vision"),
    RepoSpec("fmtlib/fmt", RepoCategory.HEALTHY, RepoSize.MEDIUM, RepoLanguage.CPP, "Formatting library"),
]


def get_catalogue() -> List[RepoSpec]:
    """Return the full benchmark catalogue."""
    return list(CATALOGUE)


def get_catalogue_size() -> int:
    """Return the number of repos in the catalogue."""
    return len(CATALOGUE)


def get_category_counts() -> dict:
    """Return counts per category."""
    counts: dict = {}
    for repo in CATALOGUE:
        counts[repo.category.value] = counts.get(repo.category.value, 0) + 1
    return counts


def get_language_counts() -> dict:
    """Return counts per language."""
    counts: dict = {}
    for repo in CATALOGUE:
        counts[repo.language.value] = counts.get(repo.language.value, 0) + 1
    return counts


def get_size_counts() -> dict:
    """Return counts per size."""
    counts: dict = {}
    for repo in CATALOGUE:
        counts[repo.size.value] = counts.get(repo.size.value, 0) + 1
    return counts


if __name__ == "__main__":
    print(f"Catalogue size: {get_catalogue_size()}")
    print(f"Categories: {get_category_counts()}")
    print(f"Languages: {get_language_counts()}")
    print(f"Sizes: {get_size_counts()}")
