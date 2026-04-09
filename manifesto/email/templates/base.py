from abc import ABC, abstractmethod
from typing import Dict, Any


class EmailTemplate(ABC):
    @abstractmethod
    def generate(self, pr_data: Dict[str, Any]) -> tuple[str, str]:
        """Return (subject, html_body) for the given PR data."""
        ...
