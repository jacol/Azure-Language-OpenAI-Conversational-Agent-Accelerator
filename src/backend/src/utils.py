# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
import os
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.core.credentials import TokenCredential
from azure.core.credentials import AccessToken


class CognitiveServicesCredential(TokenCredential):
    """A credential wrapper that ensures the correct scope for Azure Cognitive Services."""
    
    def __init__(self, credential: TokenCredential):
        self._credential = credential
        
    def get_token(self, *scopes, **kwargs):
        # Always use the Cognitive Services scope for Azure AI services
        cognitive_services_scope = "https://cognitiveservices.azure.com/.default"
        return self._credential.get_token(cognitive_services_scope, **kwargs)


def get_azure_credential():
    use_mi_auth = os.environ.get('USE_MI_AUTH', 'false').lower() == 'true'

    if use_mi_auth:
        mi_client_id = os.environ['MI_CLIENT_ID']
        base_credential = ManagedIdentityCredential(
            client_id=mi_client_id
        )
    else:
        base_credential = DefaultAzureCredential()
    
    return CognitiveServicesCredential(base_credential)
