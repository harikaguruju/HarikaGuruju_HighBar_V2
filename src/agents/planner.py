class Planner:
    """
    Planner Agent:
    Breaks the user query into structured subtasks for other agents.
    """

    def __init__(self, cfg):
        self.cfg = cfg

    def plan(self, query):
        """
        Returns a static but structured plan of tasks.
        """
        tasks = [
            {"id": "load_summary", "agent": "data_agent", "desc": "Load dataset and produce summaries"},
            {"id": "find_drop_periods", "agent": "data_agent", "desc": "Identify periods with ROAS drop"},
            {"id": "generate_hypotheses", "agent": "insight_agent", "desc": "Generate candidate hypotheses"},
            {"id": "validate_hypotheses", "agent": "evaluator", "desc": "Validate hypotheses statistically"},
            {"id": "creative_suggestions", "agent": "creative_generator", "desc": "Suggest new creatives for low-CTR campaigns"}
        ]
        return tasks
