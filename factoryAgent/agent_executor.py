import json

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    DataPart,
    Part,
    Task,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import new_agent_parts_message, new_task
from a2a.utils.errors import ServerError

# ADK imports for running the existing agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

# Import the existing agent from agent.py
from agent import factory_agent


class FactoryAgentExecutor(AgentExecutor):
    """Executor for the Factory Agent."""

    def __init__(self):
        self.session_service = InMemorySessionService()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        query = context.get_user_input()
        task = context.current_task

        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)

        updater = TaskUpdater(event_queue, task.id, task.context_id)

        try:
            session_id = task.context_id
            user_id = "a2a_user"
            app_name = "factory_a2a_app"

            session = await self.session_service.get_session(
                app_name, user_id, session_id
            )
            if not session:
                session = await self.session_service.create_session(
                    app_name=app_name,
                    user_id=user_id,
                    session_id=session_id,
                    state={"initial": True},
                )

            runner = Runner(
                agent=factory_agent,
                app_name=app_name,
                session_service=self.session_service,
            )

            content = genai_types.Content(
                role="user", parts=[genai_types.Part(text=query)]
            )

            await updater.update_status(TaskState.working)

            async for event in runner.run_async(
                user_id=user_id, session_id=session_id, new_message=content
            ):
                event_data = json.loads(event.model_dump_json(exclude_none=True))
                
                message_with_event = new_agent_parts_message(
                    [Part(root=DataPart(data=event_data))],
                    task.context_id,
                    task.id,
                )
                await updater.update_status(TaskState.working, message_with_event)

            await updater.complete()

        except Exception as e:
            error_message = f"An error occurred: {e}"
            await updater.update_status(
                TaskState.failed,
                new_agent_parts_message(
                    [Part(root=TextPart(text=error_message))],
                    task.context_id,
                    task.id,
                ),
                final=True,
            )

    async def cancel(
        self, request: RequestContext, event_queue: EventQueue
    ) -> Task | None:
        raise ServerError(error=UnsupportedOperationError()) 