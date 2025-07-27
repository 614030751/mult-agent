import logging
import os

import click
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import FactoryAgentExecutor
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MissingAPIKeyError(Exception):
    """Exception for missing API key."""


@click.command()
@click.option("--host", default="0.0.0.0")
@click.option("--port", default=10002)
def main(host, port):
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            raise MissingAPIKeyError("GOOGLE_API_KEY environment variable not set.")

        capabilities = AgentCapabilities(streaming=True)
        skill = AgentSkill(
            id="run_factory_agent",
            name="Run Factory Agent",
            description="Simulates a factory supply chain process including planning, sourcing, and logistics.",
            tags=["factory", "simulation", "supply-chain"],
            examples=["Run a simulation for producing 100 cars."],
        )
        agent_card = AgentCard(
            name="Factory Agent",
            description="This agent simulates a complex factory supply chain.",
            url=f"http://{host}:{port}",
            version="1.0.0",
            capabilities=capabilities,
            skills=[skill],
            defaultInputModes=["text"],
            defaultOutputModes=["text"],
        )
        request_handler = DefaultRequestHandler(
            agent_executor=FactoryAgentExecutor(),
            task_store=InMemoryTaskStore(),
        )
        server = A2AStarletteApplication(
            agent_card=agent_card, http_handler=request_handler
        )
        import uvicorn

        uvicorn.run(server.build(), host=host, port=port)
    except MissingAPIKeyError as e:
        logger.error(f"Error: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"An error occurred during server startup: {e}")
        exit(1)


if __name__ == "__main__":
    main() 