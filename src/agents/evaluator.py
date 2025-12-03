import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class Evaluator:
    """
    High-bar evaluator that validates hypotheses using:
    - Baseline vs current comparison
    - Absolute and relative deltas
    - Impact classification
    - Confidence scoring
    """

    def __init__(self, cfg: Dict[str, Any]) -> None:
        self.cfg = cfg
        self.min_relative_drop = cfg.get("min_relative_drop_pct", 0.20)
        self.min_impressions = cfg.get("min_impressions_for_insight", 500)
        self.min_confidence = cfg.get("min_confidence", 0.6)

    def _classify_impact(self, relative_delta: float) -> str:
        """Convert % drop into impact level."""
        if relative_delta >= 0.40:
            return "high"
        elif relative_delta >= 0.25:
            return "medium"
        else:
            return "low"

    def _estimate_confidence(self, relative_delta: float, impressions: int) -> float:
        """
        Simple confidence heuristic using magnitude of change + data volume.
        """
        volume_factor = min(impressions / 5000, 1.0)
        delta_factor = min(relative_delta / 0.5, 1.0)
        confidence = round(0.5 * volume_factor + 0.5 * delta_factor, 2)
        return confidence

    def validate(
        self,
        hypotheses: List[Dict[str, Any]],
        summary: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Validate hypotheses using structured evidence:
        - baseline vs current
        - absolute + relative delta
        - impact
        - confidence
        """

        validated_results: List[Dict[str, Any]] = []

        for h in hypotheses:
            baseline_val = h["baseline"]
            current_val = h["current"]
            impressions = h.get("impressions", 0)

            if baseline_val == 0:
                logger.warning(
                    "Skipping hypothesis %s because baseline is zero",
                    h["id"],
                )
                continue

            absolute_delta = current_val - baseline_val
            relative_delta = abs(absolute_delta) / baseline_val

            impact = self._classify_impact(relative_delta)
            confidence = self._estimate_confidence(relative_delta, impressions)

            validated = (
                relative_delta >= self.min_relative_drop
                and impressions >= self.min_impressions
                and confidence >= self.min_confidence
            )

            result = {
                "hypothesis_id": h["id"],
                "hypothesis": h["hypothesis"],
                "segment": h["segment"],
                "metric": h["metric"],
                "evidence": {
                    "baseline": baseline_val,
                    "current": current_val,
                    "absolute_delta": round(absolute_delta, 4),
                    "relative_delta_pct": round(relative_delta * 100, 2),
                    "impressions": impressions,
                },
                "impact": impact,
                "confidence": confidence,
                "validated": validated,
            }

            logger.info(
                "Evaluated hypothesis %s | impact=%s | confidence=%.2f | validated=%s",
                h["id"],
                impact,
                confidence,
                validated,
            )

            validated_results.append(result)

        return validated_results
