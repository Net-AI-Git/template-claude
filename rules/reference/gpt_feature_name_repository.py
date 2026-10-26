# Canonical GPT repository. Copy to src/repositories/gpt_<feature_name>_repository.py and rename.
# Imports are written relative to that destination, not to this directory.
#
# --- task_data keys this method reads ---
# task_data["items_list_text"] (str):  "1. Code: 10 | Name: <ITEM_NAME> | Definition: <what this item means>\n2. Code: 20 | Name: ..."
# task_data["source_text"] (str):      "<the free-text input the model classifies against the provided items>"
#
# --- GPT Output (response.choices[0].message.parsed) ---
# FeatureNameResponse(matched_items=[MatchedItem(code=10, name="<exact name from list>", score=4), MatchedItem(code=20, name="...", score=5)])
# Empty when no match: FeatureNameResponse(matched_items=[])

import os

import httpx
from dotenv import load_dotenv
from openai import AzureOpenAI

from .splunk_repository import SplunkRepository
from ..schemas.gpt_responses import FeatureNameResponse

load_dotenv()


class GptFeatureNameRepository:

    client = AzureOpenAI(api_key=os.getenv("AZURE_OPENAI_API_KEY"), api_version=os.getenv("AZURE_OPENAI_API_VERSION"), azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), http_client=httpx.Client(verify=False))

    @staticmethod
    def run_feature(task_data, flow_id):
        SplunkRepository.log_event(status="STARTING", content=task_data, flow_id=flow_id, level="INFO")
        feature_result = None
        try:
            response = GptFeatureNameRepository.client.beta.chat.completions.parse(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                seed=151,
                top_p=1,
                response_format=FeatureNameResponse,
                messages=[
                    {"role": "system",
                     "content": [
                         {
                             "type": "text",
                             "text":
                                 """
                                [INSTRUCTIONS]

                               [DEFINITIONS]
                               - SOURCE: The free-text input provided to the model.
                               - ITEM: A single candidate entry (code, name, definition) the model may select.
                               - PROVIDED_ITEMS: The full list of ITEMS the model must choose from.
                               [/DEFINITIONS]

                              ROLE: You are a strict classifier that selects matching ITEMS from a provided list.

                              TASK:
                              You will be given two inputs: SOURCE - the free text to analyze, PROVIDED_ITEMS - a list of ITEMS each with a numeric code, name, and definition.
                              Your task is to select ALL ITEMS in PROVIDED_ITEMS that are supported by the SOURCE.

                              RULES:
                              - Match ITEMS based on the definition, not the name alone.
                              - You MUST select ONLY from the PROVIDED_ITEMS list. Do NOT invent new ITEMS.
                              - An ITEM MUST be actively supported by the SOURCE, not merely plausible.
                              - There is NO limit on the number of ITEMS you may return — return every ITEM that applies.

                              CONFIDENCE SCORE (integer 1–5):
                                5 = Certain — explicitly and clearly present in the SOURCE
                                4 = High confidence — strong evidence supports this
                                3 = Moderate — some evidence but ambiguous
                                2 = Low — weak or indirect evidence
                                1 = Very low — barely mentioned, speculative

                              RESPONSE FORMAT:
                              - Return ONLY a valid JSON object. No text before or after.
                              - Do NOT wrap the response in markdown code blocks (no ```json or ```).
                              - Exact structure: {"matched_items": [{"code": <integer from list>, "name": "<exact name from list>", "score": <integer 1-5>}]}
                              - If no ITEM applies, return an empty list: {"matched_items": []}

                              [EXAMPLE 01]
                              SOURCE: "<a source text where item 10 is clearly and explicitly supported>"
                              Answer: {"matched_items": [{"code": 10, "name": "<ITEM_NAME_10>", "score": 5}]}
                              [/EXAMPLE_01]

                              [EXAMPLE 02]
                              SOURCE: "<a source text where items 20 and 30 have strong but not certain support>"
                              Answer: {"matched_items": [{"code": 20, "name": "<ITEM_NAME_20>", "score": 4}, {"code": 30, "name": "<ITEM_NAME_30>", "score": 4}]}
                              [/EXAMPLE_02]

                              [EXAMPLE 03]
                              SOURCE: "<a source text mixing one clear item and one only weakly-hinted item>"
                              Answer: {"matched_items": [{"code": 10, "name": "<ITEM_NAME_10>", "score": 5}, {"code": 40, "name": "<ITEM_NAME_40>", "score": 2}]}
                              [/EXAMPLE_03]

                              [EXAMPLE 04]
                              SOURCE: "<a source text where no provided item applies>"
                              Answer: {"matched_items": []}
                              [/EXAMPLE_04]

                              [/INSTRUCTIONS]
                                """
                         }
                     ]
                     },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"SOURCE: {task_data['source_text']}"
                            },
                            {
                                "type": "text",
                                "text": f"PROVIDED_ITEMS: {task_data['items_list_text']}"
                            }
                        ]
                    }
                ]
            )
            feature_result = response.choices[0].message.parsed
        except Exception as err:
            SplunkRepository.log_event(status="ERROR", content={"error": repr(err), "task_data": task_data}, flow_id=flow_id, level="ERROR")
        SplunkRepository.log_event(status="FINISHED", content=task_data, flow_id=flow_id, level="INFO")
        return feature_result
