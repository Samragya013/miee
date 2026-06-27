# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability within MIIE, please send an email to the project maintainer. All security vulnerabilities will be promptly addressed.

**Please do not report security vulnerabilities through public GitHub issues.**

## Disclosure Policy

When the security team receives a security bug report, they will assign it to a primary handler. This person will coordinate the fix and release process, involving the following steps:

1. Confirm the problem and determine the affected versions.
2. Audit code to find any potential similar problems.
3. Prepare fixes for all releases still under maintenance.
4. Release patches as soon as possible.

## Security Best Practices

When using MIIE:

- Never commit API tokens or secrets to version control
- Use environment variables or `.env` files for sensitive configuration
- The `.env` file is git-ignored by default
- CLI output filters sensitive information (paths, tokens, hashes)

## Verification

```bash
# Verify no secrets in codebase
grep -r "api_key\|secret\|token\|password" src/ --include="*.py"

# Verify .env is git-ignored
git check-ignore .env
```
