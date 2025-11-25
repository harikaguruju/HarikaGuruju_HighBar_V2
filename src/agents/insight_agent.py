import numpy as np

class InsightAgent:
    """
    Insight Agent:
    Accepts dataset summaries (not raw CSV) and produces a set of candidate hypotheses
    explaining performance changes (ROAS drops, creative issues, audience saturation, etc.).
    """

    def __init__(self, cfg):
        self.cfg = cfg

    def generate_hypotheses(self, summary):
        """
        Input: summary (dict) from DataAgent
        Output: list of hypothesis dicts:
            {
              "hypothesis_id": str,
              "hypothesis": str,
              "reasoning": str,
              "expected_signals": [str,...],
              "confidence": float (0-1)
            }
        """
        hypotheses = []
        daily = summary.get("daily", [])
        campaign_list = summary.get("campaign", [])

        # 1) ROAS drop across windows (last 7 vs prior 7)
        if len(daily) >= 14:
            last7 = daily[-7:]
            prev7 = daily[-14:-7]
            roas_last = np.mean([d.get("roas", 0) for d in last7])
            roas_prev = np.mean([d.get("roas", 0) for d in prev7])
            pct_drop = (roas_prev - roas_last) / roas_prev if roas_prev and roas_prev > 0 else 0.0

            if pct_drop > self.cfg.get("roas_drop_threshold_pct", 0.15):
                hypotheses.append({
                    "hypothesis_id": "h_roas_drop",
                    "hypothesis": f"Average daily ROAS fell by {pct_drop:.2%} in the last 7 days vs the prior 7 days.",
                    "reasoning": "Significant relative decline in average daily ROAS detected across windows.",
                    "expected_signals": ["roas_down", "revenue_down_or_spend_up", "ctr_down"],
                    "confidence": 0.65
                })

        # 2) Creative underperformance (low CTR campaigns)
        low_ctr_campaigns = summary.get("low_ctr_campaigns", [])
        for i, c in enumerate(low_ctr_campaigns[:10]):
            campaign_name = c.get("campaign_name", f"campaign_{i}")
            ctr = c.get("ctr", 0)
            hypotheses.append({
                "hypothesis_id": f"h_creative_{i+1}",
                "hypothesis": f"Campaign '{campaign_name}' has low CTR ({ctr:.3%}) suggesting creative underperformance or poor relevance.",
                "reasoning": "Campaign-level CTR below configured threshold; creatives may not be resonating.",
                "expected_signals": ["low_ctr", "low_clicks", "low_conversion_rate"],
                "confidence": 0.7
            })

        # 3) Audience saturation / targeting overlap
        # Generic hypothesis — evaluator will check spend vs impressions and CPM changes.
        hypotheses.append({
            "hypothesis_id": "h_audience_saturation",
            "hypothesis": "Possible audience saturation or targeting overlap leading to higher costs (CPM) and lower ROAS.",
            "reasoning": "When impressions plateau but cost increases, it indicates saturation or audience overlap.",
            "expected_signals": ["impressions_flat", "cpm_up", "frequency_up"],
            "confidence": 0.45
        })

        # 4) Platform or country-specific drop (if campaign list contains platform/country tokens)
        # Heuristic: if many campaigns include platform/country in name, propose platform-specific hypothesis
        platforms = set()
        for c in campaign_list:
            name = (c.get("campaign_name") or "").lower()
            if "instagram" in name:
                platforms.add("instagram")
            if "facebook" in name:
                platforms.add("facebook")
        if platforms:
            hypotheses.append({
                "hypothesis_id": "h_platform_specific",
                "hypothesis": f"Performance changes may be concentrated on platform(s): {', '.join(platforms)}.",
                "reasoning": "Campaign naming indicates platform-specific targeting; platform-level issues or bid changes may affect ROAS.",
                "expected_signals": ["platform_roas_change", "platform_ctr_change"],
                "confidence": 0.4
            })

        # 5) Data quality / tracking issues (fallback hypothesis)
        hypotheses.append({
            "hypothesis_id": "h_data_quality",
            "hypothesis": "Possible tracking or attribution issues causing artificial ROAS fluctuations.",
            "reasoning": "If purchases or revenue drop without a commensurate drop in clicks/impressions, tracking might be affected.",
            "expected_signals": ["revenue_drop_without_click_drop", "sudden_zero_values", "missing_dates"],
            "confidence": 0.3
        })

        return hypotheses
