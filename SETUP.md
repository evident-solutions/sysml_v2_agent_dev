# Setup Instructions

## Environment Variables

Create a `.env` file in the project root with the following content:

```env
# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# File Search Store Configuration (optional)
FILE_SEARCH_STORE_NAME=sysml-v2-documents

# Gemini Model Configuration (optional)
GEMINI_MODEL=gemini-2.5-flash

# File Paths (optional)
DATA_DIR=./data
PDF_DIR=./data/pdfs
CACHE_DIR=./.cache

# Logging Configuration (optional)
LOG_LEVEL=INFO
LOG_FILE=./logs/agent.log
```

Replace `your_gemini_api_key_here` with your actual Gemini API key.

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create `.env` file (see above)

3. Test the installation:
   ```bash
   python -m src.cli list-files
   ```

4. Upload your first PDF:
   ```bash
   python -m src.cli upload path/to/your/document.pdf
   ```

5. Ask a question:
   ```bash
   python -m src.cli ask "What is SysML?"
   ```

