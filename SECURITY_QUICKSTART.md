# Security Quick Start Guide

Get up and running with security tools in under 5 minutes.

## 1. Install Security Tools

### Backend (Python)

```bash
cd backend

# Install all development dependencies (includes security tools)
pip install -r requirements-dev.txt

# Or install just security tools
pip install semgrep bandit safety pip-audit pre-commit
```

### Frontend (JavaScript/TypeScript)

```bash
cd frontend

# Audit is built into npm
npm install
```

## 2. Set Up Pre-commit Hooks

```bash
# From project root
pip install pre-commit

# Install git hooks
pre-commit install

# Test it works
pre-commit run --all-files
```

Now security checks run automatically before every commit!

## 3. Run Your First Semgrep Scan

```bash
# From project root
./scripts/run-semgrep.sh
```

This runs a comprehensive security scan covering:
- OWASP Top 10 vulnerabilities
- Python security issues
- React/TypeScript security patterns
- Hardcoded secrets detection
- SQL injection risks
- Command injection risks

## 4. Quick Security Checks

### Before Committing

```bash
# Quick security scan (30 seconds)
./scripts/run-semgrep.sh quick

# Or let pre-commit do it automatically
git add .
git commit -m "Your changes"  # Semgrep runs automatically!
```

### Before Pushing

```bash
# Full security scan (1-2 minutes)
./scripts/run-semgrep.sh

# Check for secrets
./scripts/run-semgrep.sh secrets

# Backend-specific checks
cd backend
bandit -r src/
safety check
pip-audit

# Frontend-specific checks
cd frontend
npm audit
```

### Weekly Maintenance

```bash
# Check for dependency vulnerabilities
cd backend && safety check && pip-audit
cd frontend && npm audit

# Update pre-commit hooks
pre-commit autoupdate
```

## 5. Understanding Semgrep Output

### Example Output

```
┌────────────────┐
│ 3 Code Findings │
└────────────────┘

  backend/src/api/auth.py
  ❯❯❱ python.django.security.sql-injection
         Potential SQL injection vulnerability

      15┆ query = f"SELECT * FROM users WHERE id = {user_id}"
          ⋮┆----------------------------------------

  Autofix: Use parameterized queries
  Learn more: https://semgrep.dev/r/python.django.security.sql-injection
```

### Severity Levels

- 🔴 **ERROR**: Critical security issue - must fix
- 🟡 **WARNING**: Potential issue - review and fix
- 🔵 **INFO**: Code quality or minor issue

## 6. Common Scan Modes

```bash
# Full scan (recommended weekly)
./scripts/run-semgrep.sh full

# Quick scan (recommended before commits)
./scripts/run-semgrep.sh quick

# Backend only (Python)
./scripts/run-semgrep.sh backend

# Frontend only (TypeScript/React)
./scripts/run-semgrep.sh frontend

# Secrets only (critical!)
./scripts/run-semgrep.sh secrets

# JSON output for reporting
./scripts/run-semgrep.sh json
```

## 7. Fixing Common Issues

### SQL Injection

❌ **Before:**
```python
query = f"SELECT * FROM users WHERE id = {user_id}"
session.execute(query)
```

✅ **After:**
```python
session.query(User).filter(User.id == user_id).first()
```

### Hardcoded Secrets

❌ **Before:**
```python
API_KEY = "sk-1234567890abcdef"
```

✅ **After:**
```python
import os
API_KEY = os.getenv('OPENAI_API_KEY')
```

### XSS in React

❌ **Before:**
```tsx
<div dangerouslySetInnerHTML={{__html: userInput}} />
```

✅ **After:**
```tsx
<div>{sanitize(userInput)}</div>
```

## 8. Bypassing False Positives

If Semgrep flags a false positive (rare but happens):

```python
# nosemgrep: python.lang.security.audit.dangerous-subprocess-use
subprocess.run(["safe", "command"])  # This is safe because...
```

**Important**: Only use `nosemgrep` when you're certain it's a false positive. Add a comment explaining why.

## 9. Integration with Your Workflow

### Option 1: Pre-commit (Automatic)
✅ Installed by default
- Runs on `git commit`
- Catches issues before they're committed
- Can be skipped with `git commit --no-verify` (not recommended)

### Option 2: Manual (Before Push)
```bash
./scripts/run-semgrep.sh
git push
```

### Option 3: Pre-push Hook
Add to `.git/hooks/pre-push`:
```bash
#!/bin/bash
./scripts/run-semgrep.sh
```

## 10. Troubleshooting

### Semgrep Not Found

```bash
pip install semgrep
# or
brew install semgrep
```

### Pre-commit Hook Not Running

```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Test
pre-commit run --all-files
```

### Too Slow

```bash
# Use quick mode
./scripts/run-semgrep.sh quick

# Or disable in pre-commit temporarily
SKIP=semgrep git commit -m "message"
```

## Next Steps

- Read the full [SECURITY.md](SECURITY.md) for detailed policies
- Explore [Semgrep Playground](https://semgrep.dev/playground) to understand rules
- Review [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- Set up a weekly security review schedule

## Need Help?

- Semgrep Docs: https://semgrep.dev/docs/
- Semgrep Community: https://semgrep.dev/community
- Project Issues: https://github.com/marcusradder/data-dictionary-gen/issues

---

**Remember**: Security is a continuous process, not a one-time setup. Run scans regularly and keep dependencies updated!
