# GitHub CI/CD Setup

This directory contains GitHub Actions workflows for continuous integration and deployment.

## Workflows

### CI Pipeline (`.github/workflows/ci.yml`)

Runs automatically on:
- Push to `main`, `master`, or `develop` branches
- Pull requests to `main`, `master`, or `develop` branches
- Manual trigger via `workflow_dispatch`

**Jobs included:**
1. **Test**: Runs pytest on Python 3.10, 3.11, and 3.12
2. **Lint**: Code quality checks with flake8, black, and isort
3. **Security**: Security scanning with safety and bandit
4. **Build Check**: Verifies all core modules can be imported

### Release Pipeline (`.github/workflows/release.yml`)

Runs automatically on:
- Creation of a new release
- Manual trigger with version input

**Features:**
- Creates source code archives
- Runs tests before release
- Uploads release artifacts

## Setup Instructions

### 1. Initial Setup

1. **Push your code to GitHub:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

2. **Update README badge:**
   - Edit `README.md`
   - Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` in the badge URL

### 2. GitHub Secrets (Optional)

If you need real API testing in CI, add secrets to your GitHub repository:

1. Go to: **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Add:
   - `GEMINI_API_KEY`: Your Gemini API key (for real API tests)

### 3. Enable Dependabot (Optional)

Dependabot is configured to automatically:
- Check for Python package updates weekly
- Check for GitHub Actions updates weekly
- Create pull requests for updates

No additional setup needed - it's enabled by default when the workflow runs.

## Local Testing

Before pushing, you can run checks locally:

```bash
# Install development dependencies
pip install -r requirements.txt
pip install flake8 black isort safety bandit

# Run tests
pytest tests/ -v

# Check formatting
black --check src/ config/ utils/ tests/

# Check linting
flake8 src/ config/ utils/ tests/

# Security checks
safety check
bandit -r src/ config/ utils/
```

## Customization

### Modify Python Versions

Edit `.github/workflows/ci.yml`:
```yaml
strategy:
  matrix:
    python-version: ["3.10", "3.11", "3.12"]  # Add/remove versions
```

### Add More Linters

Edit the `lint` job in `.github/workflows/ci.yml`:
```yaml
- name: Install linting dependencies
  run: |
    pip install pylint mypy
```

### Enable PyPI Publishing

Uncomment and configure the `release` job in `.github/workflows/ci.yml`:
1. Add `PYPI_API_TOKEN` to GitHub Secrets
2. Uncomment the release job steps
3. Update versioning strategy as needed

## Troubleshooting

### Tests fail in CI but pass locally
- Check Python version compatibility
- Verify all dependencies are in `requirements.txt`
- Check for environment-specific issues

### Security checks fail
- Review the security warnings
- Update dependencies if vulnerabilities are found
- Use `continue-on-error: true` to make checks non-blocking (already configured)

### Build fails due to imports
- Ensure all dependencies are listed in `requirements.txt`
- Check that `__init__.py` files exist in all packages
- Verify Python path and module structure

