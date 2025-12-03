import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class Evaluator:
    """
    Robust evaluator with:
    - baseline fallback
    - delta computation
    - confidence scoring
    - zero-crash guarantee
    """

    def validate(self, hypotheses: List[Dict], summary: Dict) -> List[Dict]:
        results = []

        for h in hypotheses:
            try:
                metric = h.get("metric", "unknown")
                current_val = h.get("current", None)

                # ✅ SAFE BASELINE HANDLING
                baseline_val = h.get("baseline", None)

                if baseline_val is None:
                    logger.warning(
                        "Baseline missing for hypothesis '%s'. Falling back to overall summary.",
                        h.get("hypothesis", "N/A"),
                    )

                    # fallback from summary safely
                    if metric == "ctr":
                        baseline_val = summary.get("overall_ctr", 0)
                    elif metric == "roas":
                        baseline_val = summary.get("overall_roas", 0)
                    else:
                        baseline_val = 0

                # ✅ SAFE DELTA CALCULATION
                if baseline_val == 0:
                    delta = 0
                else:
                    delta = (current_val - baseline_val) / baseline_val

                confidence = round(min(abs(delta) * 2, 1.0), 2)

                impact = "low"
                if abs(delta) > 0.3:
                    impact = "high"
                elif abs(delta) > 0.15:
                    impact = "medium"

                evaluated = {
                    "hypothesis": h.get("hypothesis", "unknown"),
                    "metric": metric,
                    "baseline": round(baseline_val, 4),
                    "current": round(current_val, 4),
                    "delta_pct": round(delta * 100, 2),
                    "impact": impact,
                    "confidence": confidence,
                }

                logger.info(
                    "Evaluated hypothesis: %s | delta=%.2f%% | impact=%s | confidence=%.2f",
                    evaluated["hypothesis"],
                    evaluated["delta_pct"],
                    evaluated["impact"],
                    evaluated["confidence"],
                )

                results.append(evaluated)

            except Exception as e:
                logger.exception("Evaluator failed on hypothesis: %s", h)
                results.append({
                    "hypothesis": h.get("hypothesis", "unknown"),
                    "error": str(e),
                    "impact": "unknown",
                    "confidence": 0.0,
                })

        return results
