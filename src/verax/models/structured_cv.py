"""Core CV data structures."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List


@dataclass(frozen=True)
class ContactInfo:
    """Candidate contact information.

    Attributes:
        name: Full name
        email: Email address
        phone: Phone number
        location: Physical location (city, state)
        website: Personal website or portfolio URL
        linkedin: LinkedIn profile URL
    """

    name: str
    email: str = ""
    phone: str = ""
    location: str = ""
    website: str = ""
    linkedin: str = ""


@dataclass(frozen=True)
class CVEntry:
    """A single entry in a CV section.

    Represents one work experience, education item, skill, project, or generic entry.

    Attributes:
        title: Job title, degree name, skill name, or project title
        subtitle: Company, school, skill category, or project context
        dates: Date range like "Jan 2020 - Dec 2021" or "2020 - 2021" or ""
        description: Detailed text, typically bullet points separated by newlines
    """

    title: str
    subtitle: str = ""
    dates: str = ""
    description: str = ""


class SectionType(Enum):
    """Enumeration of CV section types."""

    EXPERIENCE = "experience"
    EDUCATION = "education"
    SKILLS = "skills"
    SUMMARY = "summary"
    PROJECTS = "projects"
    CERTIFICATIONS = "certifications"
    CUSTOM = "custom"


@dataclass(frozen=True)
class CVSection:
    """A logical section of a CV.

    Represents all entries of a particular type (e.g., all work experience items).

    Attributes:
        title: Section heading (e.g., "Experience", "Education")
        section_type: Type of section (from SectionType enum)
        entries: List of CVEntry items in this section
        raw_text: Fallback raw text if structured parsing fails
    """

    title: str
    section_type: SectionType
    entries: List[CVEntry] = field(default_factory=list)
    raw_text: str = ""


@dataclass(frozen=True)
class StructuredCV:
    """Complete structured representation of a CV.

    This is the primary data structure passed through the pipeline:
    Parser → LLM extraction → LLM mapping → Builder → Output file.

    Attributes:
        contact_info: Candidate contact details
        sections: List of CV sections (experience, education, etc.)
        source_filename: Original file name for audit trail and user reference
    """

    contact_info: ContactInfo
    sections: List[CVSection] = field(default_factory=list)
    source_filename: str = ""
