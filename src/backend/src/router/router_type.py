# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
from enum import Enum


class RouterType(Enum):
    """
    Router implementation type.
    """
    # No routing (e.g. fallback only):
    BYPASS = "BYPASS"

    # CLU only:
    CLU = "CLU"

    # CQA only:
    CQA = "CQA"

    # Orchestration to decide CLU or CQA:
    ORCHESTRATION = "ORCHESTRATION"

    # GPT function-calling to decide CLU or CQA:
    FUNCTION_CALLING = "FUNCTION_CALLING"

    # Triage agent to decide CLU or CQA:
    TRIAGE_AGENT = "TRIAGE_AGENT"
