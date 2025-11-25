# Creative Generator Prompt

**Goal:** Generate improved creative ideas (headlines, bodies, CTAs) for campaigns with low CTR.  
Ground new creatives in *existing creative messages* and product context found in the dataset summary.

---

## Required Behaviors

### 1. Input:
- List of low-CTR campaigns
- Campaign names
- Creative messages (if available)
- Vocabulary extracted from campaign names/messages

### 2. Output:
Generate **3 creative suggestions per campaign**:
- `headline`
- `body`
- `cta`

Each suggestion must follow these guidelines:
- Be short, engaging, and relevant to the type of product
- Use wording inspired by existing creative_message fields
- Include urgency or value-focused language (e.g., comfort, fit, discount, limited offer)
- CTA should be strong and varied (e.g., “Shop Now”, “Buy Today”, “Discover More”)

---

## Output Format (JSON)

```json
[
  {
    "campaign_name": "xyz campaign",
    "creative_suggestions": [
      {
        "headline": "New Styles You'll Love",
        "body": "Soft, breathable and made for comfort — upgrade your wardrobe today.",
        "cta": "Shop Now"
      }
    ]
  }
]
