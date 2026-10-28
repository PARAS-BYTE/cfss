"""
Sample Python Code for CodeFlow Studio Verification.
Tests indentation spaces, docstrings, lambdas, and special characters.
"""

from typing import List, Optional


class DataPipeline:
    """Robust data processing pipeline with exact indentation."""

    def __init__(self, name: str, batch_size: int = 64):
        self.name = name
        self.batch_size = batch_size
        self._processed_count = 0

    def process_records(self, items: List[int]) -> List[int]:
        """Transform records using mapping and filtering."""
        if not items:
            return []

        # 4-space indentation preservation test
        transformed = [
            (x * 2) + 1
            for x in items
            if x % 2 == 0
        ]
        self._processed_count += len(transformed)
        return transformed


if __name__ == "__main__":
    pipeline = DataPipeline("DemoPipeline", batch_size=32)
    sample_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    output = pipeline.process_records(sample_data)
    print(f"Pipeline '{pipeline.name}' processed: {output}")
