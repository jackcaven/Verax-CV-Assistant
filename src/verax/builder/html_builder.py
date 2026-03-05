"""HTML builder for CV preview via Jinja2."""

from pathlib import Path

from jinja2 import Template

from verax.models.structured_cv import StructuredCV
from verax.models.template_schema import TemplateSchema
from verax.utils import get_logger

logger = get_logger(__name__)


# Inline CSS for professional CV styling
HTML_STYLESHEET = """
<style>
    body {
        font-family: 'Calibri', 'Segoe UI', sans-serif;
        line-height: 1.5;
        margin: 2cm;
        color: #333;
    }

    .contact-block {
        text-align: center;
        margin-bottom: 20px;
        padding-bottom: 15px;
        border-bottom: 2px solid #333;
    }

    .contact-block h1 {
        margin: 0;
        font-size: 28px;
        font-weight: bold;
    }

    .contact-info {
        font-size: 11px;
        margin-top: 5px;
        color: #555;
    }

    .section {
        margin-bottom: 20px;
    }

    .section h2 {
        font-size: 14px;
        font-weight: bold;
        margin: 12px 0 8px 0;
        padding-bottom: 4px;
        border-bottom: 1px solid #999;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .entry {
        margin-bottom: 12px;
    }

    .entry-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 2px;
    }

    .entry-title {
        font-weight: bold;
        font-size: 12px;
    }

    .entry-subtitle {
        font-weight: bold;
        font-size: 12px;
        color: #555;
    }

    .entry-separator {
        color: #999;
        margin: 0 4px;
    }

    .entry-dates {
        font-size: 11px;
        color: #666;
        font-style: italic;
        margin-bottom: 4px;
    }

    .entry-description {
        font-size: 11px;
        margin-left: 20px;
    }

    .entry-description li {
        margin-bottom: 3px;
    }

    .placeholder {
        font-style: italic;
        color: #999;
    }

    @media print {
        body {
            margin: 1.5cm;
        }
    }
</style>
"""

# Jinja2 template for CV HTML
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ contact_info.name }} - CV</title>
    {{ stylesheet | safe }}
</head>
<body>
    <div class="contact-block">
        <h1>{{ contact_info.name }}</h1>
        {% if contact_info.email or contact_info.phone or contact_info.location or contact_info.website or contact_info.linkedin %}
        <div class="contact-info">
            {% set info_parts = [] %}
            {% if contact_info.email %}
                {% set _ = info_parts.append(contact_info.email) %}
            {% endif %}
            {% if contact_info.phone %}
                {% set _ = info_parts.append(contact_info.phone) %}
            {% endif %}
            {% if contact_info.location %}
                {% set _ = info_parts.append(contact_info.location) %}
            {% endif %}
            {% if contact_info.website %}
                {% set _ = info_parts.append(contact_info.website) %}
            {% endif %}
            {% if contact_info.linkedin %}
                {% set _ = info_parts.append(contact_info.linkedin) %}
            {% endif %}
            {{ info_parts | join(' • ') }}
        </div>
        {% endif %}
    </div>

    {% for section in sections %}
    <div class="section">
        <h2>{{ section.title }}</h2>
        {% if section.entries %}
            {% for entry in section.entries %}
            <div class="entry">
                <div class="entry-header">
                    {% if entry.title and entry.subtitle %}
                        <span class="entry-title">{{ entry.title }}<span class="entry-separator">—</span><span class="entry-subtitle">{{ entry.subtitle }}</span></span>
                    {% elif entry.title %}
                        <span class="entry-title">{{ entry.title }}</span>
                    {% elif entry.subtitle %}
                        <span class="entry-subtitle">{{ entry.subtitle }}</span>
                    {% endif %}
                    {% if entry.dates %}
                    <span class="entry-dates">{{ entry.dates }}</span>
                    {% endif %}
                </div>
                {% if entry.description %}
                <div class="entry-description">
                    <ul>
                    {% for line in entry.description.split('\\n') %}
                        {% set clean_line = line.strip() %}
                        {% if clean_line %}
                            {% set display_line = clean_line %}
                            {% if display_line.startswith('•') %}
                                {% set display_line = display_line[1:].strip() %}
                            {% elif display_line.startswith('-') %}
                                {% set display_line = display_line[1:].strip() %}
                            {% endif %}
                        <li>{{ display_line }}</li>
                        {% endif %}
                    {% endfor %}
                    </ul>
                </div>
                {% endif %}
            </div>
            {% endfor %}
        {% else %}
            <p class="placeholder">[Content for this section would go here]</p>
        {% endif %}
    </div>
    {% endfor %}
</body>
</html>
"""


class HtmlBuilder:
    """Build HTML output for CV preview."""

    name = "html"

    def build(
        self,
        cv: StructuredCV,
        template_schema: TemplateSchema,
        output_path: Path,
    ) -> None:
        """Build HTML CV preview.

        Args:
            cv: Structured CV to write
            template_schema: Template structure (unused for HTML, but part of protocol)
            output_path: Where to save the HTML file

        Raises:
            IOError: If file write fails
        """
        logger.info(f"Building HTML for {cv.source_filename} -> {output_path}")

        try:
            # Render template
            template = Template(HTML_TEMPLATE)
            html_content = template.render(
                contact_info=cv.contact_info,
                sections=cv.sections,
                stylesheet=HTML_STYLESHEET,
            )

            # Write to file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(html_content, encoding="utf-8")

            logger.info(f"HTML saved: {output_path}")

        except Exception as e:
            logger.error(f"Failed to build HTML: {e}")
            raise IOError(f"HTML build failed: {e}")
