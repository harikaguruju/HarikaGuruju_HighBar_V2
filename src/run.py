#!/usr/bin/env python3
import os
import json
import argparse
import logging
import yaml

from src.agents.planner import Planner
from src.agents.data_agent import DataAgent
from src.agents.insight_agent import InsightAgent
from src.agents.evaluator import Evaluator
from src.agents.creative_generator import CreativeGenerator

CONFIG_PATH = "config/config.yaml"

# ---------- logging setup ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)
# -----------------------------------


def load_config(path: str = CONFIG_PATH) -> dict:
    """Load YAML config file."""
    logger.info("Loading config from %s", path)
    with open(path) as f:
        cfg = yaml.safe_load(f)
    logger.info("Config loaded successfully")
    return cfg


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="User query, e.g. 'Analyze ROAS drop'")
    args = parser.parse_args()

    logger.info("Starting pipeline for query: %s", args.query)

    cfg = load_config()

    # Instantiate agents
    logger.info("Instantiating agents")
    planner = Planner(cfg)
    data_agent = DataAgent(cfg)
    insight_agent = InsightAgent(cfg)
    evaluator = Evaluator(cfg)
    creative = CreativeGenerator(cfg)

    # 1. Planner decomposes the query into tasks
    logger.info("Step 1/5: Planner creating task list")
    tasks = planner.plan(args.query)
    logger.info("Planner produced %d tasks", len(tasks))

    # 2. Data agent loads and summarizes the dataset
    logger.info("Step 2/5: DataAgent loading and summarising dataset")
    summary = data_agent.load_and_summarize()
    logger.info("Data summary created")

    # 3. Insight agent generates hypotheses
    logger.info("Step 3/5: InsightAgent generating hypotheses")
    hypotheses = insight_agent.generate_hypotheses(summary)
    logger.info("Generated %d hypotheses", len(hypotheses))

    # 4. Evaluator validates hypotheses
    logger.info("Step 4/5: Evaluator validating hypotheses")
    validations = evaluator.validate(hypotheses, summary)
    logger.info("Validation complete")

    # 5. Creative generator produces new ideas for low-CTR campaigns
    logger.info("Step 5/5: CreativeGenerator creating suggestions")
    creatives = creative.generate(summary)
    logger.info("Generated %d creative ideas", len(creatives))

    # Save outputs
    os.makedirs("reports", exist_ok=True)
    logger.info("Saving outputs into reports/ directory")

    with open("reports/insights.json", "w", encoding="utf-8") as f:
        json.dump(hypotheses, f, indent=2, ensure_ascii=False)

    with open("reports/validations.json", "w", encoding="utf-8") as f:
        json.dump(validations, f, indent=2, ensure_ascii=False)

    with open("reports/creatives.json", "w", encoding="utf-8") as f:
        json.dump(creatives, f, indent=2, ensure_ascii=False)

    # Create report.md
    report_lines: list[str] = []
    report_lines.append("# Final Report\n")
    report_lines.append("## Hypotheses\n")
    for h in hypotheses:
        report_lines.append(
            f"- **{h.get('hypothesis_id')}**: {h.get('hypothesis')} "
            f"(confidence={h.get('confidence')})"
        )

    report_lines.append("\n## Validations\n")
    for v in validations:
        report_lines.append(
            f"- **{v.get('hypothesis_id')}** → validated: {v.get('validated')}, "
            f"evidence: {v.get('evidence')}"
        )

    report_lines.append("\n## Creative Suggestions Generated\n")
    report_lines.append("See `creatives.json` for full outputs.")

    with open("reports/report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    logger.info("Pipeline finished successfully. Outputs saved in reports/ folder.")


if __name__ == "__main__":
    main()
