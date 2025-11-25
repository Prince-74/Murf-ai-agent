import json
from livekit.agents import function_tool, RunContext

CONTENT_PATH = "shared-data/day4_tutor_content.json"   # BEST OPTION


def _load_content_raw():
    with open(CONTENT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@function_tool
def get_concepts(ctx: RunContext):
    """Return list of available concepts."""
    data = _load_content_raw()
    return data["concepts"]


@function_tool
def get_concept(ctx: RunContext, concept_id: str):
    """Return details for a specific concept."""
    data = _load_content_raw()
    for item in data["concepts"]:
        if item["id"] == concept_id:
            return item
    return None


@function_tool
def evaluate_teach_back(ctx: RunContext, concept_summary: str, user_explanation: str):
    """Basic qualitative evaluation of user's explanation."""
    score = 50

    summary_words = concept_summary.lower().split()[:4]
    if any(word in user_explanation.lower() for word in summary_words):
        score = 80

    feedback = (
        "Good explanation with some alignment to the concept summary."
        if score > 60 else
        "Your explanation is a bit unclear. Try referencing the core idea more directly."
    )

    return {"score": score, "feedback": feedback}
