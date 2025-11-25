import random
import re

class CreativeGenerator:
    """
    Creative Generator Agent:
    Produces new creative recommendations (headline, body, CTA)
    for campaigns that show low CTR.
    """

    def __init__(self, cfg):
        self.cfg = cfg
        random.seed(self.cfg.get("random_seed", 42))

    def generate(self, summary):
        """
        Input:
            summary["low_ctr_campaigns"]: list of low-CTR campaign dicts
        Output:
            list of:
            {
              "campaign_name": str,
              "creative_suggestions": [
                 {"headline": str, "body": str, "cta": str},
                 ...
              ]
            }
        """
        low_campaigns = summary.get("low_ctr_campaigns", [])
        campaign_data = summary.get("campaign", [])
        outputs = []

        # Build a simple vocabulary from campaign names
        vocab = set()
        for c in campaign_data:
            name = c.get("campaign_name", "") or ""
            tokens = re.findall(r"\w+", name.lower())
            for t in tokens:
                if len(t) > 2:
                    vocab.add(t)
        vocab = list(vocab)

        for c in low_campaigns:
            campaign_name = c.get("campaign_name", "Unknown")
            suggestions = []

            for _ in range(3):  # generate 3 creative ideas
                headline = self._generate_headline(campaign_name)
                body = self._generate_body(vocab)
                cta = random.choice(["Shop Now", "Buy Today", "Learn More", "Limited Offer"])

                suggestions.append({
                    "headline": headline,
                    "body": body,
                    "cta": cta
                })

            outputs.append({
                "campaign_name": campaign_name,
                "creative_suggestions": suggestions
            })

        return outputs

    def _generate_headline(self, campaign_name):
        """Simple headline templates"""
        templates = [
            f"New styles from {campaign_name} — Don’t Miss Out!",
            f"{campaign_name}: Trending Now!",
            f"Upgrade Your Look with {campaign_name}"
        ]
        return random.choice(templates)

    def _generate_body(self, vocab):
        """Generate short descriptive text using random vocab tokens"""
        if vocab:
            words = random.sample(vocab, min(5, len(vocab)))
            phrase = " ".join(words)
            return f"Discover premium comfort and style. {phrase}. Order now for fast delivery!"
        else:
            return "Discover premium comfort and style. Shop now for exclusive offers!"
