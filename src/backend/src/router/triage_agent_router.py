# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
import os
import json
import logging
import pii_redacter
from typing import Callable
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import ListSortOrder
from router.clu_router import parse_response as parse_clu_response
from router.cqa_router import parse_response as parse_cqa_response
from utils import get_azure_credential

_logger = logging.getLogger(__name__)

PII_ENABLED = os.environ.get("PII_ENABLED", "false").lower() == "true"

def create_triage_agent_router() -> Callable[[str, str, str], dict]:
    """
    Create triage agent router.
    """
    project_endpoint = os.environ.get("AGENTS_PROJECT_ENDPOINT")
    credential = get_azure_credential()
    agents_client = AgentsClient(
        endpoint=project_endpoint,
        credential=credential,
        api_version="2025-05-15-preview"
    )
    agent_id = os.environ.get("TRIAGE_AGENT_ID")
    agent = agents_client.get_agent(agent_id=agent_id)

    def triage_agent_router(
        utterance: str,
        language: str,
        id: str
    ) -> dict:
        """
        Triage agent router function.
        """

        # Create thread for communication
        thread = agents_client.threads.create()
        print(f"Created thread, ID: {thread.id}")

        # Create and add user message to thread
        message = agents_client.messages.create(
            thread_id=thread.id,
            role="user",
            content=utterance,
        )
        print(f"Created message: {message['id']}")
        
        # Process the agent run and handle retries
        max_retries = int(os.environ.get("MAX_AGENT_RETRY", 3))
        for attempt in range(1, max_retries + 1):
            run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
            print(f"Run attempt {attempt} finished with status: {run.status}")

            if run.status == "completed":
                # Fetch and log all messages if successful run
                messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
                for msg in messages:
                    if msg.text_messages:
                        last_text = msg.text_messages[-1]
                        print(f"{msg.role}: {last_text.text.value}")

                        # Load the agent response into a JSON
                        if msg.role == "assistant" :
                            try:
                                # Attempt to parse the agent response as JSON
                                data = json.loads(last_text.text.value)
                                parsed_result = parse_response(data)
                                return parsed_result
                            except json.JSONDecodeError as e:
                                print(f"Error decoding JSON on attempt {attempt}: {e}")
                                print(f"Raw JSON string: {last_text.text.value}")

                                # If JSON parsing fails, handle retries or raise an error if max retries reached
                                if attempt == max_retries:
                                    raise RuntimeError(f"JSON parsing failed after {max_retries} attempts.")
                                else:
                                    # Exit the inner loop to retry agent run
                                    print(f"Retrying agent run due to JSON parsing error... Attempt {attempt + 1}/{max_retries}")
                                    break
        
            # If run fails, handle retries or raise an error if max retries reached
            elif attempt == max_retries:
                print(f"Run failed after {max_retries} attempts: {run.last_error}")
                raise RuntimeError()
            else:
                print(f"Run failed on attempt {attempt}: {run.last_error}. Retrying...")


    return triage_agent_router

def parse_response(
    response: dict
) -> dict:
    """
    Parse Triage Agent Message response.
    """
    # Check tool kind used by the agent
    kind = response["type"]
    error = None
    parsed_result = {}

    # Parse the response based on tool used
    if kind == "clu_result":
        parsed_result = parse_clu_response(
            response=response["response"]
        )
    elif kind == "cqa_result":
        parsed_result = parse_cqa_response(
            response=response["response"]
        )
    else:
        error = f"Unexpected agent intent kind: {kind}"

    if error is not None:
        parsed_result["error"] = error
    parsed_result["api_response"] = response["response"]

    return parsed_result
