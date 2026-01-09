# SysML v2 Expert Agent

[![CI Pipeline](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME/actions/workflows/ci.yml)

A CLI-based expert agent for SysML v2 that uses Gemini File Search for RAG (Retrieval-Augmented Generation) to answer conceptual and definitional questions about SysML.

## Features

- Upload PDF documents to Gemini File Search
- Answer SysML conceptual and definitional questions using RAG
- Track uploaded files to prevent duplicates
- Interactive Q&A mode

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your Gemini API key:
   ```bash
   cp .env.example .env
   ```
4. Edit `.env` and add your `GEMINI_API_KEY`

## Usage

### Upload a PDF file
```bash
python -m src.cli upload path/to/document.pdf
```

### Upload all PDFs from a directory
```bash
python -m src.cli upload-dir path/to/pdf/directory
```

### List uploaded files
```bash
python -m src.cli list-files
```

### Ask a question
```bash
python -m src.cli ask "What is a Block in SysML?"
```

### Interactive mode
```bash
python -m src.cli interactive
```

### Clear file tracking cache
```bash
python -m src.cli clear-cache
```

## Project Structure

```
gensys-gemini-file-search-cursor-v20260109/
├── src/              # Source code
├── config/           # Configuration management
├── utils/            # Utility functions
├── tests/            # Unit tests
└── data/             # Data storage (optional)
```

## Development

Run tests:
```bash
python -m pytest tests/
```

## CI/CD

This project includes GitHub Actions workflows for:

- **Continuous Integration** (`.github/workflows/ci.yml`):
  - Automated testing on multiple Python versions (3.10, 3.11, 3.12)
  - Code quality checks (flake8, black, isort)
  - Security scanning (safety, bandit)
  - Build verification

- **Release Pipeline** (`.github/workflows/release.yml`):
  - Automated release asset creation on tag releases
  - Source code archiving

To set up CI/CD:
1. Push your code to GitHub
2. Update the badge URL in README.md with your repository path
3. (Optional) Add `GEMINI_API_KEY` to GitHub Secrets if you need real API testing in CI
4. Workflows will run automatically on push and pull requests

## License

[Add your license here]

