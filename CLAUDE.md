# Verax CV Assistant — Developer Guide

This document is the authoritative reference for building, maintaining, and extending the Verax CV Assistant application. It covers architecture, data models, implementation strategy, and tactical decisions.

---

## 1. Technology Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **UI** | CustomTkinter | Modern tkinter theming, simplest PyInstaller integration, zero license concerns, cross-platform |
| **Document Parsing** | pdfplumber (PDF), python-docx (DOCX), mammoth (.doc) | Industry standard for PDF metadata, native DOCX manipulation, graceful .doc fallback |
| **LLM** | openai + anthropic SDKs | Pluggable abstraction layer from day one via Protocol-based factory |
| **Output Formats** | python-docx (DOCX), LibreOffice headless (PDF), Jinja2 (HTML) | DOCX for template fidelity, subprocess PDF for portability, HTML for preview |
| **Packaging** | PyInstaller | Battle-tested with tkinter, cross-platform support, no external runtime |
| **Project Tooling** | pyproject.toml (hatchling), ruff, mypy, pytest | Modern Python packaging, unified config, strict type checking |

---

## 2. Folder Structure

```
Verax-CV-Assistant/
├── CLAUDE.md                  # This file — authoritative guide
├── README.md                  # User-facing documentation
├── requirements.md            # Original requirements snapshot
├── pyproject.toml             # Project metadata, dependencies, tooling config
├── .env.example               # Template for API keys and env vars
│
├── src/verax/
│   ├── __init__.py
│   ├── main.py                # Entry point — initializes app, loads config
│   │
│   ├── models/                # Pure dataclasses — no business logic
│   │   ├── __init__.py
│   │   ├── structured_cv.py   # StructuredCV, CVSection, ContactInfo
│   │   ├── template_schema.py # TemplateSchema, SectionTemplate
│   │   └── config.py          # AppConfig, PrivacyMode enum
│   │
│   ├── ui/                    # CustomTkinter windows and panels
│   │   ├── __init__.py
│   │   ├── app.py             # Main application window, root lifecycle
│   │   ├── panels/
│   │   │   ├── __init__.py
│   │   │   ├── upload_panel.py      # CV/template file selection
│   │   │   ├── batch_panel.py       # File list, progress display
│   │   │   ├── settings_panel.py    # LLM provider, API keys, privacy mode
│   │   │   ├── preview_panel.py     # StructuredCV display, section editor
│   │   │   └── export_panel.py      # Output format selection, preview
│   │   └── styles.py          # CustomTkinter color schemes and constants
│   │
│   ├── core/                  # Business logic orchestration
│   │   ├── __init__.py
│   │   ├── pipeline.py        # ProcessingPipeline — orchestrates parser → llm → builder
│   │   ├── batch_processor.py # Batch handling, parallel CV processing
│   │   └── session.py         # Session state — current template, llm config
│   │
│   ├── parsers/               # Document parsing abstraction
│   │   ├── __init__.py
│   │   ├── base.py            # DocumentParser Protocol
│   │   ├── factory.py         # ParserFactory — selects parser by extension
│   │   ├── models.py          # RawDocument dataclass
│   │   ├── docx.py            # DoxcParser implementation
│   │   ├── pdf.py             # PdfParser implementation
│   │   └── doc.py             # DocParser implementation (mammoth-based)
│   │
│   ├── template/              # Template extraction and detection
│   │   ├── __init__.py
│   │   ├── docx_extractor.py  # DOCX → TemplateSchema (heading detection, style mapping)
│   │   ├── pdf_extractor.py   # PDF → TemplateSchema (font-based heading detection)
│   │   └── fallback.py        # Bundled fallback template (DOCX bytes)
│   │
│   ├── llm/                   # LLM provider abstraction
│   │   ├── __init__.py
│   │   ├── base.py            # LLMProvider Protocol
│   │   ├── factory.py         # LLMProviderFactory
│   │   ├── prompts.py         # All prompt strings (structured, mapped, enhanced)
│   │   ├── openai_provider.py # OpenAI implementation
│   │   ├── anthropic_provider.py # Anthropic implementation
│   │   └── local_provider.py  # Local heuristic implementation (no API)
│   │
│   ├── builder/               # Output format builders
│   │   ├── __init__.py
│   │   ├── base.py            # OutputBuilder Protocol
│   │   ├── factory.py         # BuilderFactory by output format
│   │   ├── docx_builder.py    # Clone-and-fill DOCX builder
│   │   ├── pdf_builder.py     # LibreOffice subprocess wrapper
│   │   └── html_builder.py    # Jinja2-based HTML builder (preview)
│   │
│   └── utils/                 # Shared utilities
│       ├── __init__.py
│       ├── events.py          # Progress bus (queue-based, typed events)
│       ├── file_utils.py      # Safe file I/O, cleanup, extension checking
│       ├── logging_config.py  # Structured logging setup
│       └── secrets.py         # keyring/platformdirs integration for API keys
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # pytest fixtures, temp files, mock data
│   ├── unit/
│   │   ├── test_models.py
│   │   ├── test_parsers.py
│   │   ├── test_llm_providers.py
│   │   ├── test_builders.py
│   │   └── test_template_extractors.py
│   ├── integration/
│   │   ├── test_full_pipeline.py
│   │   └── test_batch_processing.py
│   └── fixtures/
│       ├── sample_cv.docx
│       ├── sample_template.docx
│       ├── sample_cv.pdf
│       └── sample_template.pdf
│
├── packaging/
│   ├── verax.spec             # PyInstaller spec file
│   ├── build_windows.sh       # Windows build script
│   ├── build_macos.sh         # macOS build script
│   └── build_linux.sh         # Linux build script
│
└── .gitignore                 # Standard Python + Windows + macOS rules
```

---

## 3. Core Data Models

All models are immutable dataclasses with no business logic. Use `@dataclass(frozen=True)` for safety.

### 3.1 StructuredCV

```python
# src/verax/models/structured_cv.py

from dataclasses import dataclass, field
from typing import List
from enum import Enum

@dataclass(frozen=True)
class ContactInfo:
    """Candidate contact information."""
    name: str
    email: str = ""
    phone: str = ""
    location: str = ""
    website: str = ""
    linkedin: str = ""

@dataclass(frozen=True)
class CVEntry:
    """A single work experience, education, skill, or generic entry."""
    title: str                      # Job title, degree, skill name
    subtitle: str = ""              # Company, school, skill category
    dates: str = ""                 # "Jan 2020 - Dec 2021" or "2020 - 2021"
    description: str = ""           # Bullet points, separated by \n

class SectionType(Enum):
    EXPERIENCE = "experience"
    EDUCATION = "education"
    SKILLS = "skills"
    SUMMARY = "summary"
    PROJECTS = "projects"
    CERTIFICATIONS = "certifications"
    CUSTOM = "custom"

@dataclass(frozen=True)
class CVSection:
    """A logical section of the CV (e.g., Experience, Education)."""
    title: str                      # "Experience", "Education", etc.
    section_type: SectionType
    entries: List[CVEntry] = field(default_factory=list)
    raw_text: str = ""              # Fallback if entries failed to parse

@dataclass(frozen=True)
class StructuredCV:
    """The complete structured representation of a CV."""
    contact_info: ContactInfo
    sections: List[CVSection] = field(default_factory=list)
    source_filename: str = ""       # Original file name for audit trail
```

### 3.2 TemplateSchema

```python
# src/verax/models/template_schema.py

from dataclasses import dataclass, field
from typing import List, Optional

@dataclass(frozen=True)
class SectionTemplate:
    """Template structure for a CV section."""
    title: str                      # Heading text as detected in template
    heading_style: str = ""         # "Heading 1", "Heading 2", or "Bold+Size" heuristic name
    font_name: str = ""             # Font name from template
    font_size: int = 0              # Font size in points
    order_index: int = 0            # Position in template

@dataclass(frozen=True)
class TemplateSchema:
    """Detected or configured template structure."""
    sections: List[SectionTemplate] = field(default_factory=list)
    raw_docx_path: Optional[str] = None  # Path to original DOCX template (for clone-and-fill)
    source_format: str = "docx"     # "docx" or "pdf" — PDF is structural only
    contact_block_style: str = ""   # Heading style or font hint for contact info
```

### 3.3 AppConfig

```python
# src/verax/models/config.py

from dataclasses import dataclass
from enum import Enum
from typing import Optional

class PrivacyMode(Enum):
    FULL = "full"                   # All API calls; full LLM enhancement
    TEMPLATE_ONLY = "template_only" # Parse CV, extract to template sections; no enhancement
    OFFLINE = "offline"             # Local heuristic parser only

class OutputFormat(Enum):
    DOCX = "docx"
    PDF = "pdf"
    HTML = "html"

@dataclass
class AppConfig:
    """Application configuration — mutable, persisted to disk."""
    llm_provider: str = "anthropic"       # "openai", "anthropic", "local"
    privacy_mode: PrivacyMode = PrivacyMode.FULL
    openai_api_key: Optional[str] = None  # Loaded from environment or keyring
    anthropic_api_key: Optional[str] = None
    output_formats: List[OutputFormat] = field(default_factory=lambda: [OutputFormat.DOCX])
    batch_parallel_count: int = 1
    enhance_text: bool = True             # If true, LLM polishes text

    def to_dict(self) -> dict:
        """Serialize to JSON (excluding sensitive keys)."""
        return {
            "llm_provider": self.llm_provider,
            "privacy_mode": self.privacy_mode.value,
            "output_formats": [f.value for f in self.output_formats],
            "batch_parallel_count": self.batch_parallel_count,
            "enhance_text": self.enhance_text,
        }
```

---

## 4. Processing Pipeline

The core pipeline is a linear process:

```
Input CV (DOCX/PDF/.doc)
    ↓
[ParserFactory] → RawDocument(text, source_filename)
    ↓
[LLMProvider.extract_structured_cv()] → StructuredCV
    ↓
[LLMProvider.map_sections(cv, template_schema)] → StructuredCV (with template sections)
    ↓
[Optional: LLMProvider.enhance_text(cv)] → StructuredCV (polished text)
    ↓
[OutputBuilder.build(cv, template_schema, output_path)] → output file
```

**Key responsibilities:**

- **Pipeline** (`core/pipeline.py`): Orchestrates the sequence, handles errors, collects metrics
- **BatchProcessor** (`core/batch_processor.py`): Manages parallel processing of multiple CVs, thread-safe
- **Session** (`core/session.py`): Holds current template, llm config, and template schema across multiple operations

---

## 5. LLMProvider Protocol

All LLM interactions go through a unified abstraction.

```python
# src/verax/llm/base.py

from typing import Protocol
from verax.models.structured_cv import StructuredCV
from verax.models.template_schema import TemplateSchema

class LLMProvider(Protocol):
    """Contract for LLM-based CV processing."""

    name: str  # "openai", "anthropic", "local"
    supports_local: bool  # Can run without API keys

    def extract_structured_cv(self, raw_text: str, original_filename: str = "") -> StructuredCV:
        """Parse raw CV text into StructuredCV with automatic section detection."""
        ...

    def map_sections(
        self,
        cv: StructuredCV,
        template_schema: TemplateSchema,
    ) -> StructuredCV:
        """Reassign CV sections to match template structure."""
        ...

    def enhance_text(
        self,
        cv: StructuredCV,
        style_guide: Optional[str] = None,
    ) -> StructuredCV:
        """Polish CV text: improve clarity, expand bullets, maintain tone."""
        ...
```

### Implementations

1. **OpenAIProvider** (`openai_provider.py`)
   - Uses `gpt-4` (or configurable model)
   - Enforces JSON responses via `response_format: {"type": "json_object"}`
   - Retry loop with error correction (3 attempts)

2. **AnthropicProvider** (`anthropic_provider.py`)
   - Uses `claude-opus-4-6` (or configurable model)
   - Prefills assistant message with `{` to force JSON start
   - Same retry logic

3. **LocalProvider** (`local_provider.py`)
   - Heuristic-based, no API calls
   - Detects sections by keyword matching
   - No enhancement (returns cv unchanged)
   - Safe fallback if API keys missing

---

## 6. Template Extraction Strategy

### 6.1 DOCX Templates

**Detection (docx_extractor.py):**

1. Open template DOCX with `python-docx`
2. Iterate paragraphs; detect headings by:
   - **Style name:** `Heading 1`, `Heading 2`, etc.
   - **Heuristic:** Bold + font size > 12pt, or all-caps + larger size
3. Store each heading as `SectionTemplate` with font info
4. Save original DOCX path in `TemplateSchema.raw_docx_path` for later clone-and-fill

**Example detection logic:**

```python
def detect_headings(docx_path: str) -> List[SectionTemplate]:
    doc = Document(docx_path)
    headings = []
    for i, para in enumerate(doc.paragraphs):
        style_name = para.style.name
        is_heading_style = style_name.startswith("Heading")

        # Heuristic: bold + large font
        is_bold_large = (
            para.runs
            and any(run.bold for run in para.runs)
            and any(run.font.size and run.font.size > Pt(12) for run in para.runs)
        )

        if is_heading_style or is_bold_large:
            headings.append(SectionTemplate(
                title=para.text,
                heading_style=style_name,
                font_name=para.runs[0].font.name if para.runs else "",
                font_size=int(para.runs[0].font.size / Pt(1)) if para.runs and para.runs[0].font.size else 0,
                order_index=len(headings),
            ))
    return headings
```

### 6.2 PDF Templates

**Detection (pdf_extractor.py):**

1. Open PDF with `pdfplumber`
2. Extract font metrics for each text object
3. Detect headings: font size > 1.15× median size, or bold/italic variant names
4. Store `TemplateSchema.source_format = "pdf"`
5. **UI Warning:** "PDF templates provide structural info only. Use DOCX for best fidelity."

**Important:** PDF templates are **structural references only**. The actual output is always DOCX-based (clone-and-fill). The user gets a warning in the UI.

### 6.3 Fallback Template

If no template is provided, use a bundled fallback:

```python
# src/verax/template/fallback.py

FALLBACK_TEMPLATE_DOCX = b"""..."""  # Base64-encoded minimal DOCX

def get_fallback_template() -> Path:
    """Extract bundled fallback template to temp file."""
    fallback_path = Path(tempfile.gettempdir()) / "verax_fallback.docx"
    fallback_path.write_bytes(base64.b64decode(FALLBACK_TEMPLATE_DOCX))
    return fallback_path
```

---

## 7. CV Rebuilding Strategy (DocxBuilder)

### 7.1 Clone-and-Fill Approach

1. **Copy template:** `shutil.copy2(template.raw_docx_path, output_path)`
2. **Clear body:** Remove all body paragraphs (keep section headings as style references)
3. **Rebuild from StructuredCV:**
   - Insert contact block (name, email, phone, location, website)
   - For each template section:
     - Insert heading (reuse heading style from template)
     - Insert entries (title, subtitle, dates, description bullets)
   - If CV missing a section in template: insert empty placeholder
4. **Preserve styles:** All formatting (fonts, sizes, colors, spacing) inherited from template

**Pseudo-code:**

```python
# src/verax/builder/docx_builder.py

def build(cv: StructuredCV, template: TemplateSchema, output_path: Path):
    # Copy template
    shutil.copy2(template.raw_docx_path, output_path)
    doc = Document(output_path)

    # Clear body (keep section heading styles as references)
    body_paras = doc.paragraphs[:]
    for para in body_paras:
        if not para.style.name.startswith("Heading"):
            # Remove non-heading paragraphs
            p = para._element
            p.getparent().remove(p)

    # Rebuild
    # 1. Add contact block at top
    add_contact_block(doc, cv.contact_info, template)

    # 2. For each template section, add corresponding CV entries
    for template_section in template.sections:
        # Find matching CV section
        cv_section = find_cv_section(cv, template_section.title)
        if cv_section:
            add_section(doc, template_section, cv_section)
        else:
            add_placeholder_section(doc, template_section)

    doc.save(output_path)
```

### 7.2 PDF Output

Use LibreOffice headless conversion:

```python
# src/verax/builder/pdf_builder.py

def build(cv: StructuredCV, template: TemplateSchema, output_path: Path):
    # First, build DOCX
    docx_path = output_path.with_suffix(".docx")
    docx_builder.build(cv, template, docx_path)

    # Convert to PDF via LibreOffice
    subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(output_path.parent), str(docx_path)],
        check=True,
    )

    # Optionally clean up DOCX
    docx_path.unlink()
```

**PDF availability detection:**

```python
# During app startup
def detect_libreoffice() -> Optional[Path]:
    """Detect LibreOffice soffice binary."""
    candidates = [
        "soffice",
        "/usr/bin/soffice",
        "C:\\Program Files\\LibreOffice\\program\\soffice.exe",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    ]
    for candidate in candidates:
        if shutil.which(candidate):
            return Path(candidate)
    return None

# In UI settings, disable PDF export if not found
if not detect_libreoffice():
    disable_pdf_format_in_ui()
```

---

## 8. LLM JSON Reliability

All LLM responses are JSON. Use retry and error correction.

### 8.1 Response Format Enforcement

**OpenAI:**
```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[...],
    response_format={"type": "json_object"},
)
```

**Anthropic:**
```python
response = client.messages.create(
    model="claude-opus-4-6",
    messages=[
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": "{"}  # Prefill with {
    ],
)
```

### 8.2 Retry Loop with Error Correction

```python
import json

def extract_json_with_retry(llm_call, max_retries=3):
    """Call LLM, parse JSON with retry."""
    for attempt in range(max_retries):
        try:
            response_text = llm_call()
            # Strip markdown fences defensively
            response_text = response_text.strip()
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            return json.loads(response_text)

        except json.JSONDecodeError as e:
            if attempt < max_retries - 1:
                # Retry with error-correction prompt
                error_message = f"JSON parsing failed: {str(e)}. Please return valid JSON."
                continue
            else:
                raise
```

---

## 9. UI Threading

All heavy operations run in background threads. Never block the UI.

### 9.1 Progress Bus (queue-based)

```python
# src/verax/utils/events.py

from dataclasses import dataclass
from typing import Literal
from queue import Queue

@dataclass(frozen=True)
class ProgressEvent:
    """Typed progress event from processing thread."""
    cv_filename: str
    stage: Literal["parsing", "extracting", "mapping", "building"]
    percent: int  # 0-100

# Global queue
progress_queue: Queue[ProgressEvent] = Queue()

def emit_progress(event: ProgressEvent):
    progress_queue.put(event)
```

### 9.2 UI Polling Loop

```python
# src/verax/ui/app.py

class VeraxApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.progress_queue = progress_queue
        self.poll_progress()

    def poll_progress(self):
        """Poll progress queue, update UI."""
        while not self.progress_queue.empty():
            try:
                event = self.progress_queue.get_nowait()
                self.update_progress_display(event.cv_filename, event.stage, event.percent)
            except:
                break

        # Schedule next poll
        self.after(50, self.poll_progress)
```

### 9.3 Processing Thread Wrapper

```python
def process_cv_async(cv_path: Path, template_schema: TemplateSchema):
    """Wrapper for background thread."""
    def work():
        try:
            pipeline = ProcessingPipeline(config)
            pipeline.process(cv_path, template_schema)
        except Exception as e:
            emit_progress(ProgressEvent(
                cv_filename=cv_path.name,
                stage="error",
                percent=0,
            ))

    thread = threading.Thread(target=work, daemon=False)
    thread.start()
```

---

## 10. MVP Build Order (12 Phases)

| Phase | Task | Duration | Dependencies |
|-------|------|----------|--------------|
| 1 | **Project bootstrap:** pyproject.toml, basic logging, AppConfig data model | 1-2 hours | None |
| 2 | **Data models:** StructuredCV, TemplateSchema, ContactInfo, CVSection, CVEntry | 1-2 hours | Phase 1 |
| 3 | **Parsers:** DocumentParser Protocol + DOCX/PDF/.doc implementations | 2-3 hours | Phase 2 |
| 4 | **Template extractors:** DOCX + PDF → TemplateSchema detection | 2-3 hours | Phase 3 |
| 5 | **LLM providers:** prompts.py (all strings first), then OpenAI, Anthropic, Local | 3-4 hours | Phase 2 |
| 6 | **Core pipeline:** ProcessingPipeline, BatchProcessor, Session, error handling | 2-3 hours | Phase 3, 4, 5 |
| 7 | **Output builders:** DocxBuilder (clone-and-fill), PdfBuilder (subprocess), HtmlBuilder (Jinja2) | 3-4 hours | Phase 2, 6 |
| 8 | **UI skeleton:** App window, basic panels, navigation, CustomTkinter setup | 2-3 hours | Phase 1 |
| 9 | **UI features:** Upload, batch list, settings, preview, export panels fully functional | 4-5 hours | Phase 8, all prior |
| 10 | **Wire threading + events:** Connect processing thread to progress queue, UI updates | 1-2 hours | Phase 9 |
| 11 | **Integration test:** End-to-end with real files, all providers | 1-2 hours | Phase 10 |
| 12 | **Packaging:** PyInstaller on Windows, macOS, Linux; documentation | 2-3 hours | Phase 11 |

**Total estimate:** ~30-45 hours for complete MVP with all features.

---

## 11. Key Technical Challenges

### Challenge 1: Template Fidelity from DOCX
**Problem:** Preserving template styles when rebuilding CV.
**Solution:** Clone-and-fill. Copy template DOCX, remove non-heading paragraphs, rebuild from StructuredCV while keeping heading styles as references.
**Iteration:** Test with various DOCX templates (ATS-friendly, creative). Verify fonts, sizes, spacing preserved.

### Challenge 2: PDF Template → DOCX Output
**Problem:** PDF templates can't be edited directly; output should be DOCX for fidelity.
**Solution:** Use PDF for structural detection only. Output always uses bundled fallback template or user's DOCX template. Show UI warning: "PDF templates provide structural info only. Use DOCX for best fidelity."
**Iteration:** Validate PDF detection logic with real resumes and templates.

### Challenge 3: LLM JSON Reliability
**Problem:** LLM responses sometimes malformed, wrapped in markdown, incomplete.
**Solution:** Enforce `response_format` (OpenAI) or prefill (Anthropic). Retry loop with error-correction prompt. Strip markdown fences defensively.
**Iteration:** Test with edge cases (very long CVs, non-English text, special characters). Log every failure for debugging.

### Challenge 4: UI Blocking
**Problem:** Parsing/LLM calls freeze the UI if on main thread.
**Solution:** All processing in background threads. Progress communicated via `queue.Queue` polled by `root.after()` loop.
**Iteration:** Stress test with large batch (50+ CVs). Verify responsiveness.

### Challenge 5: .doc Files (legacy)
**Problem:** .doc format (OLE2, binary) not natively supported by python-docx.
**Solution:** Use `mammoth` for plain-text extraction. LLM recovers structure from text.
**Caveat:** .doc output is loss-of-quality; recommend users convert to DOCX first.
**Iteration:** Test with real .doc files. Document user warning in UI.

### Challenge 6: LibreOffice Path Detection
**Problem:** LibreOffice binary location varies by OS and installation.
**Solution:** Try candidate paths at startup. Use `shutil.which("soffice")`. If not found, disable PDF export in UI.
**Iteration:** Test on Windows, macOS, Linux. Handle edge cases (portable LibreOffice, non-standard paths).

---

## 12. pyproject.toml Dependencies

```toml
[project]
name = "verax"
version = "0.1.0"
description = "CV structuring and template-based rebuilding with LLM"
requires-python = ">=3.9"

dependencies = [
    "customtkinter>=5.2.2",
    "pdfplumber>=0.11.0",
    "python-docx>=1.1.0",
    "mammoth>=1.7.0",
    "openai>=1.30.0",
    "anthropic>=0.28.0",
    "jinja2>=3.1.4",
    "python-dotenv>=1.0.1",
    "keyring>=25.2.0",
    "platformdirs>=4.2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "mypy>=1.5.0",
    "ruff>=0.1.0",
    "pyinstaller>=6.0.0",
]

[tool.mypy]
python_version = "3.9"
strict = true
exclude = ["venv", "tests/fixtures"]

[tool.ruff]
line-length = 100
target-version = "py39"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=src/verax --cov-report=html --cov-report=term-missing"
```

---

## 13. Critical Files (Implementation Order)

Build in this order to minimize dependencies:

1. **`src/verax/models/structured_cv.py`** — All downstream code depends on this
2. **`src/verax/models/template_schema.py`** — Required by template extractors
3. **`src/verax/models/config.py`** — AppConfig used everywhere
4. **`src/verax/llm/base.py`** — Define LLMProvider Protocol
5. **`src/verax/llm/prompts.py`** — All prompt strings, centralized
6. **`src/verax/parsers/models.py`** + **base.py** — RawDocument and Parser Protocol
7. **`src/verax/parsers/docx.py`**, **pdf.py**, **doc.py** — Parser implementations
8. **`src/verax/template/docx_extractor.py`** — Most complex, highest iteration
9. **`src/verax/llm/openai_provider.py`**, **anthropic_provider.py**, **local_provider.py** — Provider implementations
10. **`src/verax/builder/docx_builder.py`** — Clone-and-fill logic, high iteration
11. **`src/verax/builder/pdf_builder.py`**, **html_builder.py** — Remaining builders
12. **`src/verax/core/pipeline.py`**, **batch_processor.py**, **session.py** — Orchestration
13. **`src/verax/ui/app.py`** + **panels/** — UI (last, depends on all prior)
14. **`tests/`** — Unit + integration tests
15. **`packaging/`** — PyInstaller specs and build scripts

---

## 14. Prompt Templates (in `src/verax/llm/prompts.py`)

All prompts are centralized as string constants. Update them in one place.

### 14.1 CV Extraction Prompt

```python
EXTRACT_CV_PROMPT = """
You are a CV parsing expert. Extract structured information from the following CV text.

Return a JSON object with this schema:
{
  "contact_info": {
    "name": "...",
    "email": "...",
    "phone": "...",
    "location": "...",
    "website": "...",
    "linkedin": "..."
  },
  "sections": [
    {
      "title": "Experience",
      "section_type": "experience",
      "entries": [
        {
          "title": "Job Title",
          "subtitle": "Company",
          "dates": "Jan 2020 - Dec 2021",
          "description": "• Bullet point 1\\n• Bullet point 2"
        }
      ]
    }
  ]
}

CV Text:
{cv_text}
"""
```

### 14.2 Section Mapping Prompt

```python
SECTION_MAPPING_PROMPT = """
You are a CV section mapping expert. Reassign the following CV sections to match a template structure.

Current CV sections: {current_sections}
Template sections: {template_sections}

For each template section, find the best match in the CV. If a CV section doesn't fit, mark it as "no_match".

Return JSON matching the new structure.
"""
```

### 14.3 Text Enhancement Prompt

```python
ENHANCE_TEXT_PROMPT = """
You are a CV enhancement expert. Improve the clarity, impact, and conciseness of the following CV.

Rules:
- Keep the same tone and structure
- Expand vague bullet points with specific achievements
- Use action verbs (led, designed, implemented, etc.)
- Quantify results where possible
- Maintain ATS compatibility (avoid excessive formatting)

CV:
{cv_json}

Return enhanced CV in the same JSON schema.
"""
```

---

## 15. Secrets Management

API keys should never be hardcoded or in .gitignore. Use:

1. **Environment variables** (`.env` file, user sets at runtime)
2. **OS Keyring** (via `keyring` library) for local secrets
3. **platformdirs** for config location (respects XDG on Linux, ~/Library on macOS, %APPDATA% on Windows)

```python
# src/verax/utils/secrets.py

import keyring
from pathlib import Path
import os
from dotenv import load_dotenv

def get_api_key(provider: str) -> Optional[str]:
    """Get API key from environment or keyring."""
    env_var = f"{provider.upper()}_API_KEY"

    # 1. Check environment
    if key := os.getenv(env_var):
        return key

    # 2. Check keyring
    if key := keyring.get_password("verax", provider):
        return key

    return None

def set_api_key(provider: str, key: str):
    """Store API key in OS keyring."""
    keyring.set_password("verax", provider, key)
```

---

## 16. Testing Strategy

### 16.1 Unit Tests

- **test_models.py** — Validate dataclass construction, immutability
- **test_parsers.py** — Mock file I/O, test parsing logic
- **test_llm_providers.py** — Mock API calls, validate JSON parsing, retry logic
- **test_builders.py** — Mock document objects, test rebuild logic
- **test_template_extractors.py** — Fixture DOCX/PDF files, validate heading detection

### 16.2 Integration Tests

- **test_full_pipeline.py** — End-to-end: parse CV, extract, map, build with each provider
- **test_batch_processing.py** — Multi-file batch with progress events

### 16.3 Test Fixtures

Keep sample CVs and templates in `tests/fixtures/`:
- ATS-friendly DOCX
- Creative DOCX with colors/fonts
- PDF template
- Real .doc file

---

## 17. Packaging & Distribution

### 17.1 PyInstaller Spec

```python
# packaging/verax.spec

block_cipher = None

a = Analysis(
    ['src/verax/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/verax/template/fallback.docx', 'verax/template'),
        ('src/verax/ui/styles.css', 'verax/ui'),
    ],
    hiddenimports=['customtkinter'],
    hookspath=[],
    runtime_hooks=[],
    excludedimports=['matplotlib', 'numpy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Verax',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

### 17.2 Build Scripts

```bash
# packaging/build_windows.sh
#!/bin/bash
cd "$(dirname "$0")/.."
python -m PyInstaller packaging/verax.spec --distpath=dist/windows
```

**Repeat for macOS, Linux with appropriate settings.**

---

## 18. Development Workflow

### 18.1 Setup

```bash
# Clone repo
git clone <repo>
cd Verax-CV-Assistant

# Create venv
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dev deps
pip install -e ".[dev]"

# Create .env
cp .env.example .env
# Fill in API keys
```

### 18.2 Running Locally

```bash
python src/verax/main.py
```

### 18.3 Testing

```bash
# All tests
pytest

# Coverage
pytest --cov=src/verax --cov-report=html

# Linting
ruff check src tests
mypy src
```

### 18.4 Building

```bash
# Windows
bash packaging/build_windows.sh

# macOS
bash packaging/build_macos.sh

# Linux
bash packaging/build_linux.sh
```

---

## 19. API Key Configuration

Users provide API keys via:

1. **Environment variables** (recommended for CI/CD)
   ```bash
   export OPENAI_API_KEY=sk-...
   export ANTHROPIC_API_KEY=sk-ant-...
   ```

2. **App settings UI** → stored in OS keyring
3. **.env file** (dev only, not version-controlled)

**Never ask for or log API keys.** Use `***` in logs.

---

## 20. Known Limitations & Future Work

### MVP Scope (Out of Scope)
- Multi-language CV parsing (English focus only)
- Handwriting recognition
- Photo/image handling
- Real-time collaboration
- Cloud storage integration

### Future Enhancements
- Custom model fine-tuning for domain-specific CVs
- Support for resume video, portfolio links
- ATS scoring feedback
- Batch templates (e.g., "FAANG format", "Academic format")
- CLI mode (headless processing)

---

## 21. Troubleshooting

| Issue | Solution |
|-------|----------|
| PDF output not available | LibreOffice not installed. Run `soffice --version` to check. |
| JSON parsing fails | Check LLM API response in logs. Ensure API key is valid. |
| DOCX template styles not preserved | Verify template uses named styles (Heading 1/2). Fallback to clone-and-fill. |
| Batch processing hangs | Check thread safety of queue. Ensure no deadlocks in progress events. |
| API rate limits | Implement exponential backoff in provider retry loop. |

---

## 22. Contact & Support

- **Bug reports:** GitHub Issues
- **Questions:** GitHub Discussions
- **Documentation:** README.md (user-facing), this CLAUDE.md (dev reference)

---

**Last Updated:** 2026-03-05
**Version:** 0.1.0 (MVP)
**Status:** Ready for Phase 1 implementation
