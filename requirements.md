The product is an **OS-agnostic desktop application for recruiters** that standardises multiple CVs into the format of a chosen template CV.

Focus on **simplicity, speed to build, and maintainability**.

---

# Product Overview

The application allows a **solo recruiter** to upload:

1. A **template CV**
2. One or more **candidate CVs**

The application then:

1. Extracts the structure and layout of the **template CV**
2. Extracts the content of each **candidate CV**
3. Rebuilds each CV so that it **matches the template structure and layout**
4. Optionally **improves wording and clarity using an LLM**
5. Allows the user to **preview and edit before exporting**

Primary goal:

**Standardise many CVs into the same visual template.**

---

# Core MVP Workflow

User workflow:

1. Launch desktop app
2. Upload **template CV**
3. Upload **one or multiple CVs**
4. Click **Standardise**
5. System processes all CVs
6. User can **preview and edit**
7. Export CVs in chosen format

---

# Supported File Types

Input formats:

* .pdf
* .doc
* .docx

Design should be **extensible for future formats**.

Template CV can also be **any of the above formats**.

---

# Output Formats

User can choose export format:

* .docx
* .pdf
* .html (optional but helpful)
* potentially others later

---

# Template Behaviour

The template CV defines:

* section order
* headings
* layout
* typography
* spacing

The system should **recreate the template layout as closely as possible**.

Important constraint:

The output CV must **strictly follow the template structure**.

Example:

Template sections:

Profile
Experience
Education
Skills

Candidate CV may contain:

Summary
Work History
Education
Technical Skills

The system should **map semantically but force the template structure**.

Future feature:

Allow skipping template sections if candidate lacks data.

---

# AI Usage

MVP AI capability:

**Moderate AI usage**

LLM tasks:

* Extract structured CV data
* Improve clarity and wording
* Ensure text fits the template sections

Examples:

* rewrite bullet points
* remove fluff
* standardise formatting

However:

Users must be able to **disable sending CVs to external APIs**.

---

# LLM Provider Architecture

The system must support a **pluggable LLM provider architecture**.

User can choose provider.

Examples:

* OpenAI
* Anthropic
* local models
* future providers

Implement via an abstraction layer.

Example interface:

LLMProvider

Methods like:

* extractStructuredCV()
* enhanceText()
* mapSections()

---

# Privacy Modes

User can choose:

### Mode 1 — Local Only

No external API calls.

Only:

* document parsing
* formatting
* template application

### Mode 2 — AI Enhanced

Allows sending text to LLM providers.

Important:

Raw documents should ideally be parsed locally first.

---

# UI Requirements

Keep UI minimal.

Main screen contains:

Upload Template
Upload CV(s)
Processing progress
Preview pane
Edit pane
Export options

Allow:

* batch processing
* preview each generated CV
* minor edits before export

---

# Desktop Technology Requirement

The application must be:

* cross-platform (Windows / Mac / Linux)
* easy to package and distribute
* lightweight

Recommend the **best stack for fastest MVP development**.

Possible options include:

* Tauri
* Electron
* Python desktop frameworks
* Flutter

Choose one and justify the decision.

---

# Document Processing Requirements

The system must:

1. Parse PDFs
2. Parse DOC/DOCX
3. Extract text and structure
4. Convert to a **common internal representation**

Suggest libraries and architecture for this.

Example pipeline:

Document → Text Extraction → Structured CV → Template Renderer → Output Document

---

# Template Replication

This is the hardest part.

The system must attempt to replicate:

* font styles
* spacing
* headings
* section layout
* bullet styles

Suggest an approach for:

Extracting template layout and rebuilding it.

Potential strategies:

* Convert template to HTML then render
* Use DOCX templating
* Use a structured template schema

Provide the **simplest workable solution for MVP**.

---

# Batch Processing

The system must support:

Upload 1–N CVs
Process all in one batch
Export results individually

---

# Future Features (Not MVP)

Design architecture so these can be added later:

* LinkedIn profile import
* CV scoring
* Job description optimisation
* ATS keyword optimisation

---

# What I Want From You

Produce a detailed answer containing:

1. Recommended **technology stack**
2. **System architecture diagram**
3. Document processing pipeline
4. Template extraction strategy
5. LLM integration design
6. Folder structure
7. Key libraries
8. Data schema for a structured CV
9. Example prompts for the LLM
10. Step-by-step MVP build plan
11. Hard technical challenges and solutions
12. Packaging and distribution strategy

Assume the developer building this is experienced but working alone.

Your recommendations should optimise for:

* speed to MVP
* simplicity
* maintainability
* extensibility

Avoid unnecessary complexity.
