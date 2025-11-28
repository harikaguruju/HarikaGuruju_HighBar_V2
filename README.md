\# Kasparro Agentic Facebook Performance Analyst



This repository contains my solution for the Kasparro Applied AI Engineer Assignment — Agentic Facebook Performance Analyst.



The system is a multi-agent AI pipeline that analyzes Facebook Ads performance data, detects ROAS drops, generates insights, validates hypotheses, and suggests creative improvements.



---



\## 🚀 Key Features



\- Multi-agent architecture (Planner, Data Agent, Insight Agent, Evaluator, Creative Generator)

\- Automatic ROAS drop detection

\- Campaign-level low CTR detection

\- Hypothesis generation \& validation

\- Creative recommendation generation

\- Markdown + JSON reporting

\- Test-driven validation using Pytest



---



\## 🧠 System Workflow



1\. User enters a query (example: "Analyze ROAS drop in last 7 days")

2\. Planner agent breaks it into tasks

3\. Data Agent loads and summarizes the dataset

4\. Insight Agent generates performance hypotheses

5\. Evaluator validates hypotheses using metrics

6\. Creative Generator produces creative suggestions

7\. Final results are saved to the `reports/` folder



---



## 📁 Project Structure

```text
kasparro-agentic-fb-analyst-harika-guruju/
│
├── src/
│   ├── agents/
│   │   ├── planner.py              # Breaks user query into tasks
│   │   ├── data_agent.py           # Loads & summarizes Facebook Ads data
│   │   ├── insight_agent.py        # Generates performance hypotheses
│   │   ├── evaluator.py            # Validates hypotheses with metrics
│   │   └── creative_generator.py   # Produces creative improvement ideas
│   │
│   ├── utils/
│   │   └── loader.py               # CSV loading + retry logic + logging
│   │
│   └── run.py                      # Main pipeline entrypoint
│
├── data/
│   └── synthetic_fb_ads_undergarments.csv
│
├── reports/
│   ├── insights.json               # Generated hypotheses
│   ├── validations.json           # Hypothesis validation results
│   ├── creatives.json             # Creative suggestions
│   └── report.md                  # Final Markdown report
│
├── tests/
│   └── test_evaluator.py          # Pytest for Evaluator logic
│
├── config/
│   └── config.yaml                # Global configuration
│
├── requirements.txt
├── README.md
└── LICENSE
```







