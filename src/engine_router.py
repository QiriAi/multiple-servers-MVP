from openai import OpenAI
from dotenv import load_dotenv
import yaml
import json
from src.llm_prompt_analyser import decompose_prompt

TAGS = [
    "encyclopedia", "maps", "location", "papers", "research", "books",
    "movies", "music", "games", "art", "code", "ai", "aimodels",
    "datasets", "opinion", "community", "pets", "politics", "news",
    "finance", "health", "education", "career", "shopping", "food", "travel",
    "celebrity", "sports", "technology", "science", "history", "economics",
    "climate", "mental health", "relationships",
    "productivity", "fitness", "fashion", "psychology", "medicine"
]

load_dotenv()

def validate_tags(tags, allowed_tags):
    return [tag for tag in tags if tag in allowed_tags]

with open("src/engine_config.yaml", "r") as f:
    ENGINE_TAGS_WEIGHTED = yaml.safe_load(f)

def rank_engines(tags: list[str], top_n=2, min_score_threshold=0.6, debug=False):
    """Rank search engines based on their relevance to the given tags."""
    engine_scores = {}

    def dprint(*args, **kwargs):
        if debug:
            print(*args, **kwargs)

    dprint("\n🔍 Starting engine ranking...")
    dprint(f"📋 Tags to match: {tags}")
    dprint(f"🎯 Minimum score threshold: {min_score_threshold}\n")

    # Calculate scores for each engine
    for engine, weights in ENGINE_TAGS_WEIGHTED.items():
        dprint(f"\n⚙️  Evaluating engine: {engine}")
        dprint(f"   Available weights: {weights}")

        total_score = 0
        relevant_tags = 0
        matched_tags = []

        for tag in tags:
            if tag in weights:
                tag_score = weights[tag]
                total_score += tag_score
                relevant_tags += 1
                matched_tags.append(f"{tag} ({tag_score})")
                dprint(f"   ✓ Matched tag: {tag} with score {tag_score}")
            else:
                dprint(f"   ✗ No weight for tag: {tag}")

        if relevant_tags > 0:
            average_score = total_score / relevant_tags
            dprint(f"   📊 Final score: {average_score:.2f} (total: {total_score} / matches: {relevant_tags})")

            if average_score >= min_score_threshold:
                engine_scores[engine] = average_score
                dprint(f"   ✅ Added to results (above threshold)")
            else:
                dprint(f"   ❌ Skipped (below threshold)")
        else:
            dprint("   ❌ No matching tags found")

    ranked_engines = sorted(engine_scores.items(), key=lambda x: x[1], reverse=True)

    dprint("\n🏆 Final Rankings:")
    for engine, score in ranked_engines:
        dprint(f"   {engine}: {score:.2f}")

    additional_engines = [engine for engine, score in ranked_engines[:top_n]]
    dprint(f"\n📝 Selected engines: {additional_engines}\n")

    return additional_engines

if __name__ == "__main__":
    # query = "What cat should I buy? I like fuzzy cats."
    # query = "What is langchain?"
    # query = "What are the best vietnamese foods?"
    query = "What are similar books to harry potter?"
    result = decompose_prompt(query)
    tags=json.loads(result).get("tags")


    tags = validate_tags(tags,TAGS)
    print(type(tags))
    print(f"Tags: {tags}")

    engines = rank_engines(tags=tags)
    print(f"Selected engines: {engines}")