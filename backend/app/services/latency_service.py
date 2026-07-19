from contextlib import contextmanager
from time import perf_counter
from typing import Dict, List

from app.core.logging import logger


class LatencyTrace:
    def __init__(self, request_label: str):
        self.request_label = request_label
        self._started_at = perf_counter()
        self._stages: List[Dict] = []

    @contextmanager
    def stage(self, name: str, **metadata):
        started_at = perf_counter()
        try:
            yield
        finally:
            self.add(
                name=name, duration_ms=(perf_counter() - started_at) * 1000, **metadata
            )

    def add(self, name: str, duration_ms: float, **metadata):
        self._stages.append(
            {
                "name": name,
                "duration_ms": round(duration_ms, 2),
                "metadata": {
                    key: value for key, value in metadata.items() if value is not None
                },
            }
        )

    def total_ms(self) -> float:
        return round((perf_counter() - self._started_at) * 1000, 2)

    def as_dict(self) -> Dict:
        return {
            "request": self.request_label,
            "total_ms": self.total_ms(),
            "stages": self._stages,
        }

    def log_summary(self):
        lines = [
            "",
            "========== AI LATENCY TRACE ==========",
            f"Request: {self.request_label}",
        ]

        for stage in self._stages:
            metadata = stage["metadata"]
            suffix = ""

            if metadata:
                details = ", ".join(f"{key}={value}" for key, value in metadata.items())
                suffix = f" ({details})"

            lines.append(f"{stage['name']}: {stage['duration_ms']} ms{suffix}")

        lines.append(f"Total: {self.total_ms()} ms")
        lines.append("======================================")

        logger.info("\n".join(lines))
