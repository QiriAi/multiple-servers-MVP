"""
Changed script to include tags in the prompt call.
Gemini
Added tags with llm call
Removed entity --> replaced with spacy
"""
import os
from openai import OpenAI
import re
import json
import spacy
from dotenv import load_dotenv

load_dotenv()

nlp = spacy.load("en_core_web_sm")

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

TAGS = [
    "encyclopedia", "maps", "location", "papers", "research", "books",
    "movies", "music", "games", "art", "code", "ai", "aimodels",
    "datasets", "opinion", "community", "pets", "politics", "news",
    "finance", "health", "education", "career", "shopping", "food", "travel",
    "celebrity", "sports", "technology", "science", "history", "economics",
    "climate", "mental health", "relationships",
    "productivity", "fitness", "fashion", "psychology", "medicine"
]

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bool):
            return bool(obj)
        return super().default(obj)

def strip_code_block(content: str) -> str:
    if content.startswith("```"):
        content = re.sub(r"^```[a-zA-Z]*\n?", "", content)
        content = re.sub(r"\n?```$", "", content)
        content = content.strip()
    return content

# def identify_entities(prompt: str) -> list:
#     try:
#         response = client.chat.completions.create(
#             model="gemini-2.0-flash",
#             messages=[
#                 {"role": "system", "content": "You are an entity recognition expert. Identify and list all important entities (concepts, technical terms, proper nouns, domain-specific terminology) from the given text. Return only a JSON array of strings."},
#                 {"role": "user", "content": prompt}
#             ],
#             response_format={"type": "text"},
#             temperature=0.1,
#             max_tokens=200
#         )
#         content = response.choices[0].message.content.strip()
#         content = strip_code_block(content)
#         if not content:
#             return []
#         try:
#             entities = json.loads(content)
#             if not isinstance(entities, list):
#                 return []
#             return entities
#         except Exception:
#             return []
#     except Exception:
#         return []

def identify_entities(prompt: str) -> list:
    # SpaCy Named Entities
    doc = nlp(prompt)
    spacy_entities = set(ent.text for ent in doc.ents if ent.label_ not in {"DATE", "TIME", "PERCENT", "MONEY", "QUANTITY", "ORDINAL", "CARDINAL"})
    return list(spacy_entities)

# prompts = [
#         "What is the tea with Hailey Bieber and Justin Bieber?",
#         "What is the best time of the year to go Japan?",
#         "How to set up an AWS EC2 instance?"
#     ]
# for prompt in prompts:
#     print(identify_entities(prompt))

def classify_tags(prompt: str) -> list:
    try:
        response = client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=[
                {"role": "system", "content": f"You are a tag classifier. Choose the most relevant high-level categories for the prompt from this list: {TAGS}. Return only a JSON array of 1 to 5 lowercase tags."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "text"},
            temperature=0.3,
            max_tokens=100
        )
        content = response.choices[0].message.content.strip()
        content = strip_code_block(content)
        tags = json.loads(content)
        if isinstance(tags, list):
            return [t for t in tags if t in TAGS]
        return []
    except Exception as e:
        return []

def analyze_prompt_complexity(prompt: str) -> dict:
    complexity_metrics = {
        'character_count': len(prompt),
        'word_count': len(prompt.split()),
        'sentence_count': len([s.strip() for s in prompt.split('.') if s.strip()]),
        'average_word_length': 0,
        'complexity_score': 0,
        'has_code_blocks': '```' in prompt or '<code>' in prompt,
        'has_special_instructions': any(keyword in prompt for keyword in ['if', 'then', 'must', 'should', 'required', 'necessary']),
        'idea_count': 1,
        'entity_count': 0
    }
    words = prompt.split()
    if complexity_metrics['word_count'] > 0:
        total_word_length = sum(len(word) for word in words)
        complexity_metrics['average_word_length'] = total_word_length / complexity_metrics['word_count']
    idea_indicators = ['and', 'or', 'but', 'while', 'whereas', 'including', 'additionally', 'moreover', 'furthermore']
    for indicator in idea_indicators:
        complexity_metrics['idea_count'] += prompt.lower().count(f' {indicator} ')
    entities = identify_entities(prompt)
    complexity_metrics['entity_count'] = len(entities)
    complexity_metrics['identified_entities'] = entities
    score = 0
    score += min(complexity_metrics['word_count'] / 100 * 20, 10)
    score += min(complexity_metrics['average_word_length'] * 8, 15)
    score += min(complexity_metrics['sentence_count'] / 10 * 15, 15)
    score += min(complexity_metrics['idea_count'] * 5, 30)
    score += min(complexity_metrics['entity_count'] * 3, 15)
    score += 10 if complexity_metrics['has_code_blocks'] else 0
    score += 5 if complexity_metrics['has_special_instructions'] else 0
    complexity_metrics['complexity_score'] = round(score, 2)
    return complexity_metrics

def decompose_prompt(prompt):
    try:
        complexity = analyze_prompt_complexity(prompt)
        generated_tags = classify_tags(prompt)
        template = {
            "instructions": "Decompose the user query into multiple sub-queries if necessary. Each sub-query must include an 'engine' field set to 'all'.",
            "examples": [
                {
                    "user_prompt": "Analyze the impact of climate change on agriculture, including water availability, crop yield, and pest patterns.",
                    "tags": ["climate", "agriculture", "environment"],
                    "sub_queries": [
                        {"sub_query": "What is the impact of climate change on water availability in agriculture?", "intent": "Understand", "entities": ["climate change", "water availability", "agriculture"], "engine": "all"},
                        {"sub_query": "How does climate change affect crop yield in agriculture?", "intent": "Assess", "entities": ["climate change", "crop yield", "agriculture"], "engine": "all"},
                        {"sub_query": "What are the effects of climate change on pest patterns in agriculture?", "intent": "Evaluate", "entities": ["climate change", "pest patterns", "agriculture"], "engine": "all"}
                    ]
                }
            ]
        }

        if complexity['complexity_score'] > 70:
            template["instructions"] += " Break down into focused sub-queries."
            max_tokens = 4096
            temperature = 0.2
        elif complexity['complexity_score'] > 40:
            template["instructions"] += " Maintain moderate granularity."
            max_tokens = 3072
            temperature = 0.3
        else:
            template["instructions"] += " Keep it simple and direct."
            max_tokens = 2048
            temperature = 0.4

        template["query"] = prompt
        template["tags"] = generated_tags
        template["entities"] = complexity["identified_entities"]
        template["query_complexity"] = {
            "score": complexity['complexity_score'],
            "has_code_blocks": complexity['has_code_blocks'],
            "has_special_instructions": complexity['has_special_instructions']
        }

        response = client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=[
                {"role": "system", "content": "You are an AI assistant that processes user queries into structured sub-queries. Return output as valid JSON."},
                {"role": "user", "content": json.dumps(template)}
            ],
            response_format={"type": "text"},
            max_tokens=max_tokens,
            temperature=temperature
        )

        decomposition = response.choices[0].message.content.strip()
        decomposition = strip_code_block(decomposition)
        parsed_response = json.loads(decomposition)

        if isinstance(parsed_response, list):
            parsed_response = {"sub_queries": parsed_response}

        parsed_response["tags"] = generated_tags
        parsed_response["entities"] = complexity["identified_entities"]
        parsed_response["complexity_analysis"] = {
            "complexity_score": complexity['complexity_score'],
            "metrics": {
                "character_count": complexity['character_count'],
                "word_count": complexity['word_count'],
                "sentence_count": complexity['sentence_count'],
                "average_word_length": complexity['average_word_length'],
                "has_code_blocks": 'True' if bool(complexity['has_code_blocks']) else 'False',
                "has_special_instructions": 'True' if bool(complexity['has_special_instructions']) else 'False'
            }
        }

        usage = response.usage
        parsed_response["token_usage"] = {
            "total_tokens": usage.total_tokens,
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens
        }

        return json.dumps(parsed_response, indent=4, cls=CustomJSONEncoder)

    except Exception as e:
        return json.dumps({"error": str(e), "success": False}, indent=4, cls=CustomJSONEncoder)

if __name__ == "__main__":
    test_prompts = [
        "Who is Justin Bieber and what is the tea with Hailey Bieber?",
        "Why am I feeling so tired all the time. My doctor said it's because I have low blood sugar I'm so confused."
    ]
    for prompt in test_prompts:
        print(decompose_prompt(prompt))
