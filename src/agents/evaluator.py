import numpy as np
from scipy import stats

class Evaluator:
    """
    Evaluator Agent:
    Takes hypotheses from InsightAgent and validates them quantitatively using
    available summary statistics (daily aggregates, campaign aggregates).
    Returns validation records with simple statistical evidence.
    """

    def __init__(self, cfg):
        self.cfg = cfg

    def validate(self, hypotheses, summary):
        """
        Validate each hypothesis and return a list of validation dicts:
        {
            "hypothesis_id": str,
            "validated": bool,
            "p_value": float or None,
            "effect_size": float or None,
            "evidence": str
        }
        """
        validations = []
        daily = summary.get("daily", [])

        for h in hypotheses:
            hid = h.get("hypothesis_id")
            evidence = ""
            validated = False
            p_value = None
            effect = None

            # Validate ROAS drop hypothesis by comparing last 7 vs prior 7 daily roas
            if hid in ("h_roas_drop", "h_roas_drop"):
                if len(daily) >= 14:
                    prev7 = [d.get("roas", 0) for d in daily[-14:-7]]
                    last7 = [d.get("roas", 0) for d in daily[-7:]]
                    try:
                        tstat, p_value = stats.ttest_ind(prev7, last7, equal_var=False, nan_policy="omit")
                        roas_prev = np.mean(prev7)
                        roas_last = np.mean(last7)
                        effect = roas_prev - roas_last
                        validated = (p_value is not None and p_value < 0.1 and effect > 0)
                        evidence = f"prev_mean={roas_prev:.3f}, last_mean={roas_last:.3f}, p={p_value:.4f}"
                    except Exception as e:
                        evidence = f"t-test error: {str(e)}"
                else:
                    evidence = "Insufficient daily data (<14 days) to test ROAS windows."

            # Validate creative low CTR hypotheses
            elif hid.startswith("h_creative"):
                # Attempt to extract campaign name from hypothesis text
                txt = h.get("hypothesis", "")
                campaign_name = None
                import re
                m = re.search(r"Campaign '(.+?)' has low CTR", txt)
                if m:
                    campaign_name = m.group(1)
                # Look up campaign metrics in summary
                campaign_list = summary.get("campaign", [])
                match = None
                for c in campaign_list:
                    # try exact match, else substring match
                    if campaign_name and c.get("campaign_name") == campaign_name:
                        match = c
                        break
                if not match:
                    low = summary.get("low_ctr_campaigns", [])
                    match = low[0] if low else None

                if match:
                    ctr = match.get("ctr", 0)
                    impressions = match.get("impressions", 0)
                    validated = (ctr < self.cfg.get("low_ctr_threshold", 0.01)) and (impressions >= self.cfg.get("min_impressions_for_stat", 50))
                    evidence = f"campaign_ctr={ctr:.4f}, impressions={impressions}"
                else:
                    evidence = "No matching campaign found in summary."

            # Validate audience saturation hypothesis by checking cost-per-impression change
            elif hid == "h_audience_saturation":
                if len(daily) >= 14:
                    prev_spend = np.mean([d.get("spend", 0) for d in daily[-14:-7]])
                    last_spend = np.mean([d.get("spend", 0) for d in daily[-7:]])
                    prev_imp = np.mean([d.get("impressions", 0) for d in daily[-14:-7]])
                    last_imp = np.mean([d.get("impressions", 0) for d in daily[-7:]])
                    cp_prev = prev_spend / prev_imp if prev_imp > 0 else 0
                    cp_last = last_spend / last_imp if last_imp > 0 else 0
                    cp_change = (cp_last - cp_prev) / cp_prev if cp_prev > 0 else 0
                    validated = cp_change > 0.1  # >10% increase in cost per impression signals saturation
                    evidence = f"cp_prev={cp_prev:.3f}, cp_last={cp_last:.3f}, cp_change={cp_change:.3f}"
                else:
                    evidence = "Insufficient daily data to evaluate audience saturation."

            # Default fallback (data quality / other)
            elif hid == "h_data_quality":
                # Basic check: if revenue drops but clicks/impressions do not, flag data issue
                recent = summary.get("recent_summary", {})
                overall_daily = daily
                if overall_daily and recent:
                    # compute average prior window (exclude last 7 if possible)
                    if len(overall_daily) >= 14:
                        prev7 = overall_daily[-14:-7]
                        prev_revenue = np.mean([d.get("revenue", 0) for d in prev7])
                        last7 = overall_daily[-7:]
                        last_revenue = np.mean([d.get("revenue", 0) for d in last7])
                        prev_clicks = np.mean([d.get("clicks", 0) for d in prev7])
                        last_clicks = np.mean([d.get("clicks", 0) for d in last7])
                        # If revenue drops a lot while clicks are stable, suspect tracking
                        if prev_revenue > 0:
                            rev_drop_pct = (prev_revenue - last_revenue) / prev_revenue
                        else:
                            rev_drop_pct = 0
                        clicks_change = (last_clicks - prev_clicks) / prev_clicks if prev_clicks > 0 else 0
                        validated = (rev_drop_pct > 0.2) and (abs(clicks_change) < 0.1)
                        evidence = f"prev_rev={prev_revenue:.2f}, last_rev={last_revenue:.2f}, rev_drop_pct={rev_drop_pct:.2f}, clicks_change={clicks_change:.2f}"
                    else:
                        evidence = "Insufficient daily data to assess data-quality signals."
                else:
                    evidence = "No recent_summary or daily data present."

            else:
                evidence = "No validation logic for this hypothesis id."

            validations.append({
                "hypothesis_id": hid,
                "validated": bool(validated),
                "p_value": None if p_value is None else float(p_value),
                "effect_size": None if effect is None else float(effect),
                "evidence": evidence
            })

        return validations
