# Governance profile evaluator

import fnmatch
from typing import List, Tuple
from coherent.config import GovernanceTier, get_settings


def evaluate_diff_policy(
    modified_files: List[str], tier: GovernanceTier
) -> Tuple[bool, str]:
    """Validates if modified files adhere to the active governance tier."""
    if tier == GovernanceTier.AUTONOMOUS:
        return True, "Autonomous policy: open file access allowed."

    immutable_patterns = ["tests/**", ".github/**", "infra/**"]
    for f in modified_files:
        for pattern in immutable_patterns:
            if fnmatch.fnmatch(f, pattern):
                return False, f"Governance violation: '{f}' is an immutable path in {tier.value} tier."

    if tier == GovernanceTier.STRICT and len(modified_files) > 4:
        return False, f"Strict policy violation: exceeded max budget of 4 modified files (found {len(modified_files)})."

    return True, "Governance checks passed."