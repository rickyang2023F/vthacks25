
# Centralized thresholds and guardrails for selection/generation.
from typing import Dict

RULES: Dict[str, float] = {
    # cardinality thresholds
    "tiny_cats_max": 6,
    "small_cats_max": 20,
    "medium_cats_max": 100,

    # numeric distribution cues
    "skew_right_threshold": 1.0,  # skew > 1 → consider log scale / special binning
    "corr_strong_threshold": 0.5,

    # size limits
    "max_bars": 100,
    "default_top_k": 15,

    # time coverage
    "min_time_coverage": 0.8,  # after resampling
}
