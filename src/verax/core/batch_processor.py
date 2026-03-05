"""Batch processing for multiple CVs with parallel execution."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional

from verax.core.pipeline import ProcessingPipeline
from verax.models.config import AppConfig
from verax.models.structured_cv import StructuredCV
from verax.models.template_schema import TemplateSchema
from verax.utils import get_logger

logger = get_logger(__name__)


class BatchProcessor:
    """Process multiple CVs in parallel."""

    def __init__(self, config: AppConfig):
        """Initialize batch processor.

        Args:
            config: AppConfig with parallelism settings
        """
        self.config = config
        self.pipeline = ProcessingPipeline(config)

    def process_batch(
        self,
        cv_paths: List[Path],
        template_schema: TemplateSchema,
        progress_callback: Optional[callable] = None,
    ) -> List[tuple[Path, StructuredCV | None, Optional[Exception]]]:
        """Process multiple CVs in parallel.

        Args:
            cv_paths: List of CV file paths
            template_schema: Template to map to
            progress_callback: Optional callback for progress updates
                              Called with (cv_path, stage, percent)

        Returns:
            List of tuples: (cv_path, structured_cv, error)
            structured_cv is None if processing failed
        """
        results = []
        max_workers = min(self.config.batch_parallel_count, len(cv_paths))

        logger.info(f"Starting batch processing: {len(cv_paths)} CVs, {max_workers} workers")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            futures = {
                executor.submit(self._process_single, cv_path, template_schema): cv_path
                for cv_path in cv_paths
            }

            # Collect results as they complete
            completed_count = 0
            for future in as_completed(futures):
                cv_path = futures[future]
                try:
                    structured_cv = future.result()
                    results.append((cv_path, structured_cv, None))
                    logger.info(f"Completed: {cv_path.name}")
                except Exception as e:
                    logger.error(f"Failed: {cv_path.name}: {e}")
                    results.append((cv_path, None, e))

                # Call progress callback if provided
                completed_count += 1
                if progress_callback is not None:
                    try:
                        progress_callback(cv_path, completed_count, len(cv_paths))
                    except Exception as e:
                        logger.warning(f"Progress callback error: {e}")

        logger.info(f"Batch processing complete: {len(results)} CVs processed")
        return results

    def _process_single(
        self,
        cv_path: Path,
        template_schema: TemplateSchema,
    ) -> StructuredCV:
        """Process a single CV.

        Args:
            cv_path: Path to CV file
            template_schema: Template to map to

        Returns:
            StructuredCV

        Raises:
            Exception: If processing fails
        """
        return self.pipeline.process(cv_path, template_schema)
