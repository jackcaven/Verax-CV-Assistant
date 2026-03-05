"""Local heuristic LLM provider (no API calls)."""

import re
from typing import Optional

from verax.models.structured_cv import (
    ContactInfo,
    CVSection,
    SectionType,
    StructuredCV,
)
from verax.models.template_schema import TemplateSchema
from verax.utils import get_logger

logger = get_logger(__name__)


class LocalProvider:
    """Local heuristic parser using keyword matching (no API calls).

    Safe fallback when API keys are missing or network unavailable.
    """

    name = "local"
    supports_local = True

    SECTION_KEYWORDS = {
        SectionType.EXPERIENCE: ["experience", "work history", "employment", "professional"],
        SectionType.EDUCATION: ["education", "degree", "university", "college", "school"],
        SectionType.SKILLS: ["skills", "competencies", "technical skills", "languages"],
        SectionType.SUMMARY: ["summary", "objective", "professional summary", "about"],
        SectionType.PROJECTS: ["projects", "portfolio", "case studies"],
        SectionType.CERTIFICATIONS: ["certifications", "licenses", "awards"],
    }

    def extract_structured_cv(self, raw_text: str, original_filename: str = "") -> StructuredCV:
        """Extract CV structure using keyword matching.

        Args:
            raw_text: Plain text from parsed document
            original_filename: Original file name

        Returns:
            StructuredCV with detected sections
        """
        logger.info("Using local heuristic parser (no API)")

        # Try to extract contact info from first lines
        contact_info = self._extract_contact_info(raw_text)

        # Detect sections by keywords
        sections = self._detect_sections(raw_text)

        cv = StructuredCV(
            contact_info=contact_info,
            sections=sections,
            source_filename=original_filename,
        )
        logger.debug(f"Extracted CV: {len(sections)} sections detected")
        return cv

    def map_sections(
        self,
        cv: StructuredCV,
        template_schema: TemplateSchema,
    ) -> StructuredCV:
        """Reorder CV sections to match template.

        Args:
            cv: StructuredCV to remap
            template_schema: Target template

        Returns:
            StructuredCV with reordered sections
        """
        # Simple mapping: match by title prefix
        reordered_sections: list[CVSection] = []

        for template_section in template_schema.sections:
            template_title_lower = template_section.title.lower()

            # Find best match in CV sections
            best_match = None
            for cv_section in cv.sections:
                cv_title_lower = cv_section.title.lower()
                if template_title_lower in cv_title_lower or cv_title_lower in template_title_lower:
                    best_match = cv_section
                    break

            if best_match:
                reordered_sections.append(best_match)
            else:
                # Create empty section with template title
                empty_section = CVSection(
                    title=template_section.title,
                    section_type=SectionType.CUSTOM,
                )
                reordered_sections.append(empty_section)

        return StructuredCV(
            contact_info=cv.contact_info,
            sections=reordered_sections,
            source_filename=cv.source_filename,
        )

    def enhance_text(
        self,
        cv: StructuredCV,
        style_guide: Optional[str] = None,
    ) -> StructuredCV:
        """No enhancement in local mode.

        Args:
            cv: StructuredCV (returned unchanged)
            style_guide: Ignored

        Returns:
            Original cv unchanged
        """
        logger.debug("Local provider: enhancement disabled")
        return cv

    @staticmethod
    def _extract_contact_info(text: str) -> ContactInfo:
        """Extract contact info from text using regex patterns.

        Args:
            text: Raw CV text

        Returns:
            ContactInfo with extracted values
        """
        lines = text.split("\n")
        name = lines[0].strip() if lines else ""

        # Simple email regex
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
        email = email_match.group() if email_match else ""

        # Simple phone regex (US format)
        phone_match = re.search(r"\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}", text)
        phone = phone_match.group() if phone_match else ""

        # LinkedIn profile
        linkedin_match = re.search(r"linkedin\.com/in/([\w\-]+)", text, re.IGNORECASE)
        linkedin = f"linkedin.com/in/{linkedin_match.group(1)}" if linkedin_match else ""

        return ContactInfo(
            name=name,
            email=email,
            phone=phone,
            linkedin=linkedin,
        )

    @classmethod
    def _detect_sections(cls, text: str) -> list[CVSection]:
        """Detect sections by keyword matching.

        Args:
            text: Raw CV text

        Returns:
            List of detected CVSection objects
        """
        sections: list[CVSection] = []
        lines = text.split("\n")

        current_section = None
        current_entries: list[str] = []

        for line in lines:
            line_lower = line.lower()

            # Check if this line is a section header
            section_type = None
            for stype, keywords in cls.SECTION_KEYWORDS.items():
                if any(kw in line_lower for kw in keywords):
                    section_type = stype
                    break

            if section_type:
                # Save previous section
                if current_section:
                    section = CVSection(
                        title=current_section,
                        section_type=SectionType.CUSTOM,
                        raw_text="\n".join(current_entries),
                    )
                    sections.append(section)

                current_section = line.strip()
                current_entries = []
            elif current_section and line.strip():
                current_entries.append(line.strip())

        # Save last section
        if current_section:
            section = CVSection(
                title=current_section,
                section_type=SectionType.CUSTOM,
                raw_text="\n".join(current_entries),
            )
            sections.append(section)

        return sections
