"""LLM prompts for CV processing.

All prompts are centralized here as string constants.
Update them in one place to keep LLM behavior consistent.
"""

EXTRACT_CV_PROMPT = """{
You are a CV parsing expert. Extract structured information from the following CV text.

Return a JSON object with this exact schema (no markdown, just valid JSON):
{{
  "contact_info": {{
    "name": "...",
    "email": "...",
    "phone": "...",
    "location": "...",
    "website": "...",
    "linkedin": "..."
  }},
  "sections": [
    {{
      "title": "Experience",
      "section_type": "experience",
      "entries": [
        {{
          "title": "Job Title",
          "subtitle": "Company Name",
          "dates": "Jan 2020 - Dec 2021",
          "description": "• Bullet point 1\n• Bullet point 2"
        }}
      ]
    }}
  ]
}}

Sections types: experience, education, skills, summary, projects, certifications, custom

CV Text:
{cv_text}
}}"""

SECTION_MAPPING_PROMPT = """You are a CV section mapping expert. Reassign CV sections to match a template structure.

Current CV (JSON format):
{current_cv_json}

Template sections to match:
{template_sections}

For each template section, find the best matching CV section by title/type.
If no good match exists, create an empty section with the template title.

Return the updated CV in the same JSON schema, with sections reordered to match template.
Return only valid JSON, no markdown."""

TEXT_ENHANCEMENT_PROMPT = """You are a CV enhancement expert. Improve the clarity, impact, and conciseness of the following CV.

Rules:
- Keep the same tone and structure
- Expand vague bullet points with specific achievements
- Use action verbs (led, designed, implemented, etc.)
- Quantify results where possible (percentages, numbers)
- Maintain ATS compatibility (avoid excessive formatting)
- Keep original contact info unchanged

CV (JSON format):
{cv_json}

Return enhanced CV in the same JSON schema with improved text.
Return only valid JSON, no markdown."""
