from google.adk.agents import LlmAgent
from google.adk.agents import SequentialAgent;
import requests


def createWallet(wallet_name: str, wallet_type: str, wallet_address: str, wallet_private_key: str) -> dict:
    """Create a new wallet"""
    return {
        "status": "success",
        "message": "Wallet created successfully"
    }

code_writer_agent = LlmAgent(
    name="WalletAgent",
    model="gemini-2.5-flash",
    description="Writes inital Python code based on a specification",
    output_key="generated_code",
    tools=[]
)




