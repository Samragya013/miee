# 05 — Authentication Report

**PR-12B — Scientific Readiness Remediation**

## Authentication Architecture

### Token Discovery (PR-12B Enhancement)

The `GitHubAuth` class now auto-discovers tokens from multiple environment variables in priority order:

1. `GITHUB_TOKEN` — Standard GitHub token env var
2. `GH_TOKEN` — GitHub CLI token env var
3. `GITHUB_PAT` — Personal Access Token env var

First non-empty value wins. This improves compatibility with diverse CI/CD environments.

### Resolution Order

```
1. Explicit token parameter (constructor or from_config)
2. GITHUB_TOKEN environment variable
3. GH_TOKEN environment variable
4. GITHUB_PAT environment variable
5. Anonymous access (public repos only)
```

### Rate Limits

| Access Level | Rate Limit | PR Capacity | Review Capacity |
|-------------|-----------|-------------|----------------|
| Anonymous | 60 req/hr | ~30 PRs | ~30 reviews |
| Authenticated | 5000 req/hr | ~2500 PRs | ~2500 reviews |

### Auth Diagnostics (PR-12B New)

```python
auth = GitHubAuth()
auth.diagnostics()
# Returns:
# {
#     "authenticated": True,
#     "anonymous": False,
#     "source": "env:GITHUB_TOKEN",
#     "token_preview": "ghp_...abc1",
#     "searched_env_vars": ["GITHUB_TOKEN", "GH_TOKEN", "GITHUB_PAT"]
# }
```

```python
from miie.providers.github.authentication import summarize_auth_status
summarize_auth_status(auth)
# Returns: "Authenticated via env:GITHUB_TOKEN (token: ghp_...abc1)"
```

### Backward Compatibility

- `GitHubAuth()` with no args: auto-discovers from env vars (enhanced behavior)
- `GitHubAuth(token="..."): explicit token (unchanged)
- `GitHubAuth.from_config({...})`: config dict (unchanged)
- `auth.is_authenticated`, `auth.is_anonymous`: unchanged
- `auth.to_header_dict()`: unchanged

### Fallback Behavior

Without authentication:
- Git provider: unaffected (local operations)
- GitHub PR provider: fails with "Rate limit exhausted"
- Repository Metadata provider: fails with "Rate limit exhausted"
- Pipeline: continues with Git-only observations

With authentication:
- All providers operational
- Full observation coverage
- Rate limit: 5000 req/hr (sufficient for all 10 campaign repos)

## Recommendations

1. **CI/CD:** Set `GITHUB_TOKEN` in pipeline secrets
2. **Local development:** Use `gh auth login` to set `GH_TOKEN`
3. **Campaign execution:** Set token before running `run_campaign.py`
