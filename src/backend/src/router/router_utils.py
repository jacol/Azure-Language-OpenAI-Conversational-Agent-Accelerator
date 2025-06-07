# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
from typing import Callable
from router.router_type import RouterType
from router.clu_router import create_clu_router
from router.cqa_router import create_cqa_router
from router.function_calling_router import create_function_calling_router
from router.orchestration_router import create_orchestration_router
from router.triage_agent_router import create_triage_agent_router


def create_router(
    router_type: RouterType
) -> Callable[[str, str, str], dict]:
    """
    Create router based on settings.
    """
    if router_type == RouterType.BYPASS:
        return lambda x, y, z: None
    if router_type == RouterType.CLU:
        return create_clu_router()
    elif router_type == RouterType.CQA:
        return create_cqa_router()
    elif router_type == RouterType.ORCHESTRATION:
        return create_orchestration_router()
    elif router_type == RouterType.FUNCTION_CALLING:
        return create_function_calling_router()
    elif router_type == RouterType.TRIAGE_AGENT:
        return create_triage_agent_router()
    raise ValueError("Unsupported router type")
