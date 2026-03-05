"""Main processing pipeline for CV transformation."""

from pathlib import Path

from verax.llm.factory import LLMProviderFactory
from verax.models.config import AppConfig
from verax.models.structured_cv import StructuredCV
from verax.models.template_schema import TemplateSchema
from verax.parsers import ParserFactory
from verax.utils import ProgressEvent, emit_progress, get_logger

logger = get_logger(__name__)


class ProcessingPipeline:
    """Orchestrates CV parsing, extraction, mapping, enhancement, and building."""

    def __init__(self, config: AppConfig):
        """Initialize pipeline with configuration.

        Args:
            config: AppConfig with LLM provider and privacy settings
        """
        self.config = config
        self.llm_provider = LLMProviderFactory.create(config.llm_provider)
        logger.info(f"Pipeline initialized with provider: {config.llm_provider}")

    def process(
        self,
        cv_path: Path,
        template_schema: TemplateSchema,
    ) -> StructuredCV:
        """Process a single CV through the full pipeline.

        Pipeline stages:
        1. Parse CV file to RawDocument
        2. Extract structured CV via LLM
        3. Map sections to template
        4. Enhance text (optional)
        5. Return StructuredCV ready for building

        Args:
            cv_path: Path to CV file (DOCX/PDF/.doc)
            template_schema: Target template structure

        Returns:
            StructuredCV ready for output builder

        Raises:
            ValueError: If any stage fails
        """
        logger.info(f"Processing CV: {cv_path.name}")

        # Stage 1: Parse
        try:
            emit_progress(ProgressEvent(cv_path.name, "parsing", 10))
            parser = ParserFactory.create(cv_path)
            raw_doc = parser.parse(cv_path)
            logger.debug(f"Parsed {raw_doc.source_filename}: {len(raw_doc.text)} chars")
            emit_progress(ProgressEvent(cv_path.name, "parsing", 25))
        except Exception as e:
            logger.error(f"Parse error: {e}")
            emit_progress(ProgressEvent(cv_path.name, "error", 0))
            raise

        # Stage 2: Extract
        try:
            emit_progress(ProgressEvent(cv_path.name, "extracting", 40))
            cv = self.llm_provider.extract_structured_cv(
                raw_doc.text, raw_doc.source_filename
            )
            logger.debug(f"Extracted CV: {len(cv.sections)} sections")
            emit_progress(ProgressEvent(cv_path.name, "extracting", 50))
        except Exception as e:
            logger.error(f"Extraction error: {e}")
            emit_progress(ProgressEvent(cv_path.name, "error", 0))
            raise

        # Stage 3: Map sections to template
        try:
            emit_progress(ProgressEvent(cv_path.name, "mapping", 60))
            cv = self.llm_provider.map_sections(cv, template_schema)
            logger.debug("Mapped sections to template")
            emit_progress(ProgressEvent(cv_path.name, "mapping", 75))
        except Exception as e:
            logger.error(f"Mapping error: {e}")
            emit_progress(ProgressEvent(cv_path.name, "error", 0))
            raise

        # Stage 4: Enhance text (optional, only in FULL privacy mode)
        if self.config.enhance_text and self.config.llm_provider != "local":
            try:
                emit_progress(ProgressEvent(cv_path.name, "enhancing", 85))
                cv = self.llm_provider.enhance_text(cv)
                logger.debug("Enhanced text")
                emit_progress(ProgressEvent(cv_path.name, "enhancing", 95))
            except Exception as e:
                logger.warning(f"Enhancement failed (non-fatal): {e}")
        else:
            emit_progress(ProgressEvent(cv_path.name, "enhancing", 95))

        emit_progress(ProgressEvent(cv_path.name, "complete", 100))
        logger.info(f"Pipeline complete for {cv_path.name}")
        return cv
