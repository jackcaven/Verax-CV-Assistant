"""Application configuration and enums."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class PrivacyMode(Enum):
    """Privacy and API usage modes."""

    FULL = "full"  # All API calls; full LLM enhancement
    TEMPLATE_ONLY = "template_only"  # Parse CV, extract to template sections; no enhancement
    OFFLINE = "offline"  # Local heuristic parser only (no API)


class OutputFormat(Enum):
    """Supported output formats."""

    DOCX = "docx"
    PDF = "pdf"
    HTML = "html"


@dataclass
class AppConfig:
    """Application configuration — mutable, persisted to disk.

    Attributes:
        llm_provider: "openai", "anthropic", or "local"
        privacy_mode: PrivacyMode enum
        openai_api_key: OpenAI API key (from environment or keyring)
        anthropic_api_key: Anthropic API key (from environment or keyring)
        output_formats: List of output formats to generate
        batch_parallel_count: Number of CVs to process in parallel
        enhance_text: If True, LLM polishes text (requires FULL privacy mode)
    """

    llm_provider: str = "anthropic"
    privacy_mode: PrivacyMode = PrivacyMode.FULL
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    output_formats: List[OutputFormat] = field(default_factory=lambda: [OutputFormat.DOCX])
    batch_parallel_count: int = 1
    enhance_text: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to JSON (excluding sensitive keys).

        Returns:
            Dictionary safe for JSON serialization or logging.
        """
        return {
            "llm_provider": self.llm_provider,
            "privacy_mode": self.privacy_mode.value,
            "output_formats": [f.value for f in self.output_formats],
            "batch_parallel_count": self.batch_parallel_count,
            "enhance_text": self.enhance_text,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AppConfig":
        """Deserialize from JSON dictionary.

        Args:
            data: Dictionary with config keys.

        Returns:
            AppConfig instance.
        """
        return cls(
            llm_provider=data.get("llm_provider", "anthropic"),
            privacy_mode=PrivacyMode(data.get("privacy_mode", "full")),
            output_formats=[
                OutputFormat(f) for f in data.get("output_formats", ["docx"])
            ],
            batch_parallel_count=data.get("batch_parallel_count", 1),
            enhance_text=data.get("enhance_text", True),
        )
