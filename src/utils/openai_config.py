"""
Configuration module for Gemini API via LiteLLM
This module handles Gemini authentication and model configuration
"""

import os
from typing import Optional
from dotenv import load_dotenv
import logging

from .logger_config import setup_logger
load_dotenv()

setup_logger()

# Load the .env file
load_dotenv()

# Replace with your Key Vault URL
key_vault_url = os.getenv('KEY_VAULT_URL')

# Try to use Key Vault if configured, otherwise fall back to environment variables
if key_vault_url:
    try:
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.secrets import SecretClient
        
        credential = DefaultAzureCredential()
        vault_client = SecretClient(vault_url=key_vault_url, credential=credential)
        
        # Environment variables from Key Vault
        GEMINI_API_KEY = vault_client.get_secret("GEMINI-API-KEY").value
    except Exception as e:
        logging.warning(f"Key Vault access failed, falling back to environment variables: {e}")
        # Fall back to environment variables
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
else:
    # Use environment variables directly (bypass Key Vault)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Set LiteLLM-compatible environment variable for Gemini
if GEMINI_API_KEY and not os.getenv("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

# Default Gemini model name
DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini/gemini-1.5-pro")

# Check if API key is available
GEMINI_AVAILABLE = bool(GEMINI_API_KEY)

# For backward compatibility, keep OPENAI_AVAILABLE as alias
OPENAI_AVAILABLE = GEMINI_AVAILABLE
USE_AZURE = False  # No longer using Azure

# Legacy variables for backward compatibility (set to empty/None)
OPENAI_API_KEY = ""
AZURE_OPENAI_API_KEY = ""
AZURE_OPENAI_ENDPOINT = ""
AZURE_OPENAI_API_VERSION = ""
AZURE_GPT_DEPLOYMENT_NAME = ""

def get_openai_client() -> Optional[None]:
    """
    Legacy function for backward compatibility.
    Returns None as we no longer use OpenAI clients directly.
    All LLM calls should go through LiteLLM with Gemini.
    
    Returns:
        None (kept for backward compatibility)
    """
    return None

def get_chat_model_name() -> str:
    """
    Get the Gemini model name for chat completions via LiteLLM
    
    Returns:
        Model name for Gemini (e.g., "gemini/gemini-1.5-pro")
    """
    return DEFAULT_GEMINI_MODEL
