# Verax CV Assistant

A modern CV structuring and template-based rebuilding tool powered by LLM capabilities.

## Features

- **CV Parsing**: Extract structured data from DOCX, PDF, and .doc files
- **Template Detection**: Automatically detect CV template structure
- **LLM-Powered**: Leverage OpenAI, Anthropic, or local heuristic processing
- **Multiple Output Formats**: Generate DOCX, PDF, and HTML output
- **Batch Processing**: Process multiple CVs in parallel
- **Privacy Modes**: Choose between full API enhancement, template-only, or offline processing
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Quick Start

### Installation

```bash
git clone <repo>
cd Verax-CV-Assistant
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

### Running

```bash
python src/verax/main.py
```

### Testing

```bash
pytest
pytest --cov=src/verax --cov-report=html
```

## Configuration

Set API keys via environment variables or in the app settings:

```bash
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
```

## Architecture

See [CLAUDE.md](CLAUDE.md) for detailed architecture and development guide.

## License

Proprietary
