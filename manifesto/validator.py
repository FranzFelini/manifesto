from typing import Dict, Any, Set

DEFAULT_BRANCHES: Set[str] = {"stg", "staging", "dev", "development"}


class PRValidator:
    def __init__(self, branches: Set[str] = None):
        self.branches = {b.lower() for b in branches} if branches else DEFAULT_BRANCHES

    def should_notify(self, pr_data: Dict[str, Any]) -> bool:
        base = pr_data["base"]["ref"].lower()
        head = pr_data["head"]["ref"].lower()
        return base in self.branches or head in self.branches
