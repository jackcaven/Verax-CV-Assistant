"""Anthropic LLM provider."""

import json
import os
from typing import Optional

from anthropic import Anthropic, APIError

from verax.llm.prompts import EXTRACT_CV_PROMPT, SECTION_MAPPING_PROMPT, TEXT_ENHANCEMENT_PROMPT
from verax.models.structured_cv import ContactInfo, CVEntry, CVSection, SectionType, StructuredCV
from verax.models.template_schema import TemplateSchema
from verax.utils import get_logger

logger = get_logger(__name__)


class AnthropicProvider:
    """Anthropic LLM provider using Claude."""

    name = "anthropic"
    supports_local = False
    model = "claude-opus-4-6"
    max_retries = 3

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key. If not provided, uses ANTHROPIC_API_KEY env var.

        Raises:
            ValueError: If no API key is available.
        """
        key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise ValueError("ANTHROPIC_API_KEY not provided or set in environment")

        self.client = Anthropic(api_key=key)
        logger.info(f"Initialized Anthropic provider with model {self.model}")

    def extract_structured_cv(self, raw_text: str, original_filename: str = "") -> StructuredCV:
        """Extract CV structure using Claude.

        Args:
            raw_text: Plain text from parsed document
            original_filename: Original file name

        Returns:
            StructuredCV with extracted structure

        Raises:
            ValueError: If extraction fails after retries
        """
        prompt = EXTRACT_CV_PROMPT.format(cv_text=raw_text[:10000])  # Limit context
        response_json = self._call_llm_with_retry(prompt)
        cv_dict = json.loads(response_json)

        return self._parse_cv_from_dict(cv_dict, original_filename)

    def map_sections(
        self,
        cv: StructuredCV,
        template_schema: TemplateSchema,
    ) -> StructuredCV:
        """Remap CV sections to template structure using Claude.

        Args:
            cv: StructuredCV to remap
            template_schema: Target template

        Returns:
            StructuredCV with remapped sections
        """
        cv_json = self._cv_to_json(cv)
        template_sections = ", ".join([s.title for s in template_schema.sections])

        prompt = SECTION_MAPPING_PROMPT.format(
            current_cv_json=cv_json,
            template_sections=template_sections,
        )

        response_json = self._call_llm_with_retry(prompt)
        response_dict = json.loads(response_json)
        logger.debug(f"Mapped sections: {response_json[:100]}...")

        # Parse remapped CV and preserve contact info
        remapped_cv = self._parse_cv_from_dict(response_dict, cv.source_filename)
        return remapped_cv

    def enhance_text(
        self,
        cv: StructuredCV,
        style_guide: Optional[str] = None,
    ) -> StructuredCV:
        """Enhance CV text using Claude.

        Args:
            cv: StructuredCV to enhance
            style_guide: Optional style guide

        Returns:
            Enhanced StructuredCV
        """
        cv_json = self._cv_to_json(cv)
        prompt = TEXT_ENHANCEMENT_PROMPT.format(cv_json=cv_json)

        response_json = self._call_llm_with_retry(prompt)
        response_dict = json.loads(response_json)
        logger.debug(f"Enhanced text: {response_json[:100]}...")

        # Parse enhanced CV
        enhanced_cv = self._parse_cv_from_dict(response_dict, cv.source_filename)
        return enhanced_cv

    @staticmethod
    def _parse_cv_from_dict(cv_dict: dict, original_filename: str = "") -> StructuredCV:
        """Parse a StructuredCV from a dictionary (from LLM response).

        Args:
            cv_dict: Dictionary with contact_info and sections keys
            original_filename: Source file name for audit trail

        Returns:
            StructuredCV with parsed structure
        """
        # Parse contact info
        contact_info_dict = cv_dict.get("contact_info", {})
        contact = ContactInfo(
            name=contact_info_dict.get("name", ""),
            email=contact_info_dict.get("email", ""),
            phone=contact_info_dict.get("phone", ""),
            location=contact_info_dict.get("location", ""),
            website=contact_info_dict.get("website", ""),
            linkedin=contact_info_dict.get("linkedin", ""),
        )

        # Parse sections with entries
        sections = []
        for section_data in cv_dict.get("sections", []):
            # Map section_type string to enum
            section_type_str = section_data.get("section_type", "custom").lower()
            try:
                section_type = SectionType(section_type_str)
            except ValueError:
                section_type = SectionType.CUSTOM

            # Parse entries
            entries = []
            for entry_data in section_data.get("entries", []):
                entry = CVEntry(
                    title=entry_data.get("title", ""),
                    subtitle=entry_data.get("subtitle", ""),
                    dates=entry_data.get("dates", ""),
                    description=entry_data.get("description", ""),
                )
                entries.append(entry)

            section = CVSection(
                title=section_data.get("title", ""),
                section_type=section_type,
                entries=entries,
                raw_text=section_data.get("raw_text", ""),
            )
            sections.append(section)

        return StructuredCV(
            contact_info=contact,
            sections=sections,
            source_filename=original_filename,
        )

    def _call_llm_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        """Call Anthropic API with retry and error correction.

        Uses prefilling to force JSON response format.

        Args:
            prompt: The prompt to send
            max_retries: Number of retries on JSON decode error

        Returns:
            Response text (valid JSON)

        Raises:
            ValueError: If all retries fail
        """
        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    messages=[
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": "{"},  # Prefill to force JSON start
                    ],
                )
                response_text = "{" + response.content[0].text.strip()

                # Validate JSON
                json.loads(response_text)
                logger.debug(f"LLM response valid JSON (attempt {attempt + 1})")
                return response_text

            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    # Retry with error correction
                    prompt = (
                        f"Previous response had JSON error. Please return ONLY valid JSON.\n\n{prompt}"
                    )
                    continue
                raise ValueError(f"Failed to get valid JSON response after {max_retries} attempts")

            except APIError as e:
                logger.error(f"Anthropic API error: {e}")
                raise ValueError(f"Anthropic API error: {e}")

    @staticmethod
    def _cv_to_json(cv: StructuredCV) -> str:
        """Convert StructuredCV to JSON string for LLM input.

        Args:
            cv: StructuredCV to convert

        Returns:
            JSON string representation
        """
        data = {
            "contact_info": {
                "name": cv.contact_info.name,
                "email": cv.contact_info.email,
                "phone": cv.contact_info.phone,
            },
            "sections": [
                {
                    "title": s.title,
                    "section_type": s.section_type.value,
                    "raw_text": s.raw_text,
                }
                for s in cv.sections
            ],
        }
        return json.dumps(data, indent=2)
