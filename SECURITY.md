# Security Policy

## Overview

This document outlines the security practices and tools used in the Data Dictionary Generator project.

## Reporting a Vulnerability

If you discover a security vulnerability, please create a GitHub issue

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We aim to respond within 48 hours and provide a fix within 7 days for critical issues.

## Security Tools

### Semgrep - Static Analysis & Security Scanning

Semgrep is our primary tool for detecting security vulnerabilities, bugs, and code quality issues.

#### Installation

```bash
# Via pip
pip install semgrep

# Or via Homebrew (macOS)
brew install semgrep
```

#### Running Semgrep

We provide a convenient script for running different types of scans:

```bash
# Full security scan (recommended)
./scripts/run-semgrep.sh

# Quick scan (faster, security-audit only)
./scripts/run-semgrep.sh quick

# Backend only (Python)
./scripts/run-semgrep.sh backend

# Frontend only (TypeScript/React)
./scripts/run-semgrep.sh frontend

# Check for hardcoded secrets
./scripts/run-semgrep.sh secrets

# Output as JSON for CI/CD
./scripts/run-semgrep.sh json
```

#### What Semgrep Checks

- **OWASP Top 10**: SQL injection, XSS, CSRF, etc.
- **Security audit**: Comprehensive security patterns
- **Python-specific**: FastAPI, SQLAlchemy security issues
- **React/TypeScript**: XSS, unsafe DOM manipulation
- **Secrets detection**: API keys, passwords, tokens
- **SQL injection**: Database query vulnerabilities
- **Command injection**: OS command execution risks

#### Semgrep Rulesets Used

| Ruleset | Purpose | Files |
|---------|---------|-------|
| `p/security-audit` | Comprehensive security patterns | All |
| `p/owasp-top-ten` | OWASP Top 10 vulnerabilities | All |
| `p/python` | Python-specific issues | Backend |
| `p/react` | React security patterns | Frontend |
| `p/typescript` | TypeScript best practices | Frontend |
| `p/secrets` | Hardcoded credentials | All |
| `p/sql-injection` | SQL injection patterns | Backend |
| `p/command-injection` | Command injection patterns | Backend |

### Pre-commit Hooks

We use pre-commit hooks to automatically run security checks before each commit.

#### Setup

```bash
# Install pre-commit
pip install pre-commit

# Install the git hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

#### Enabled Hooks

1. **Semgrep** - Security scanning on changed files
2. **Bandit** - Python security linter
3. **detect-secrets** - Prevents committing secrets
4. **Ruff** - Python linting and formatting
5. **MyPy** - Python type checking
6. **ESLint** - JavaScript/TypeScript linting

### Additional Security Tools (Recommended)

#### Python Backend

```bash
# Install security tools
pip install bandit safety pip-audit

# Run Bandit (security linter)
bandit -r backend/src/

# Run Safety (known vulnerabilities)
safety check

# Run pip-audit (PyPI vulnerabilities)
pip-audit
```

#### Frontend

```bash
# NPM audit
cd frontend
npm audit

# Fix automatically
npm audit fix

# Check outdated packages
npm outdated
```

## Security Best Practices

### For Developers

1. **Never commit secrets**: Use environment variables
   - ✅ `API_KEY = os.getenv('OPENAI_API_KEY')`
   - ❌ `API_KEY = "sk-1234567890abcdef"`

2. **Run Semgrep before pushing**:
   ```bash
   ./scripts/run-semgrep.sh
   ```

3. **Use parameterized queries**: Prevent SQL injection
   ```python
   # ✅ Good - Parameterized
   session.query(User).filter(User.id == user_id)

   # ❌ Bad - String interpolation
   session.execute(f"SELECT * FROM users WHERE id = {user_id}")
   ```

4. **Validate and sanitize input**: Always validate user input
   ```python
   # ✅ Good - Using Pydantic
   class UserInput(BaseModel):
       email: EmailStr
       age: int = Field(ge=0, le=150)
   ```

5. **Use dependency pinning**: Lock file versions
   ```bash
   # Backend
   pip install pip-tools
   pip-compile requirements.txt -o requirements.lock

   # Frontend - commit package-lock.json
   git add package-lock.json
   ```

### Security Checklist for Pull Requests

- [ ] Semgrep scan passes (`./scripts/run-semgrep.sh`)
- [ ] No hardcoded secrets or credentials
- [ ] Input validation implemented for new endpoints
- [ ] SQL queries use parameterized statements
- [ ] No `eval()`, `exec()`, or dangerous functions
- [ ] Dependencies are up-to-date and secure
- [ ] Authentication/authorization properly implemented
- [ ] Error messages don't leak sensitive information

## Dependency Management

### Python Dependencies

We use version ranges to allow security patches:

```txt
# Allow minor and patch updates for security fixes
fastapi>=0.104.0,<1.0.0
```

**Update schedule**:
- Security patches: Immediately upon notification
- Minor updates: Monthly
- Major updates: Quarterly (with testing)

### JavaScript Dependencies

Using caret ranges for automatic security updates:

```json
{
  "axios": "^1.13.2"  // Allows 1.x updates
}
```

**Update schedule**:
- Run `npm audit` weekly
- Apply `npm audit fix` for vulnerabilities
- Review `npm outdated` monthly

## Known Security Considerations

### Current Status

- ✅ Input validation via Pydantic
- ✅ SQL injection prevention via SQLAlchemy ORM
- ✅ CORS configuration in place
- ⚠️ Authentication is placeholder-only (not production-ready)
- ⚠️ Rate limiting not implemented
- ⚠️ No WAF or DDoS protection

### Before Production Deployment

1. **Implement proper authentication**:
   - Use OAuth2/OIDC or JWT
   - Implement password hashing (bcrypt/argon2)
   - Add session management

2. **Add rate limiting**:
   - Install `slowapi` or use nginx rate limiting
   - Protect file upload endpoints

3. **Enable HTTPS only**:
   - Force HTTPS redirects
   - Set secure cookie flags
   - Implement HSTS headers

4. **Add security headers**:
   - Content-Security-Policy
   - X-Frame-Options
   - X-Content-Type-Options
   - Strict-Transport-Security

5. **Implement logging and monitoring**:
   - Log authentication attempts
   - Monitor for suspicious patterns
   - Set up alerts for security events

## Semgrep Configuration Files

### `.semgrepignore`
Defines which files/directories to exclude from scanning.

### `.semgrep.yml`
Can be used for custom rules (currently using registry rules).

### `.pre-commit-config.yaml`
Configures pre-commit hooks including Semgrep.

## Continuous Security

### Weekly Tasks
- [ ] Review dependency alerts
- [ ] Run `npm audit` on frontend
- [ ] Check for new Semgrep rules

### Monthly Tasks
- [ ] Run full security scan: `./scripts/run-semgrep.sh`
- [ ] Update dependencies: `pip-audit` + `npm outdated`
- [ ] Review security logs

### Quarterly Tasks
- [ ] Security audit of authentication/authorization
- [ ] Penetration testing (if applicable)
- [ ] Review and update this security policy

## Resources

- [Semgrep Docs](https://semgrep.dev/docs/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)
- [React Security](https://react.dev/learn/security)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

## Version History

- **v1.0.0** (2025-11-10): Initial security policy with Semgrep integration
