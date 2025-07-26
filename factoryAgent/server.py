import asyncio
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

# 从您现有的 agent.py 文件中导入 factory_agent
from .agent import factory_agent

# 配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# 使用内存会话服务来管理会话状态
session_service = InMemorySessionService()

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """处理 WebSocket 连接并运行 ADK Agent."""
    await websocket.accept()
    logger.info(f"WebSocket connection accepted for session: {session_id}")

    # 为这个连接创建一个唯一的会话和 Runner
    try:
        session = await session_service.create_session(
            app_name="factory_ws_app",
            user_id="websocket_user",
            session_id=session_id,
            state={"initial": True}
        )
        logger.info(f"Session created: {session.id}")

        runner = Runner(
            agent=factory_agent,
            app_name="factory_ws_app",
            session_service=session_service
        )
        logger.info("Runner initialized.")

        # 1. 等待客户端发送第一条消息作为启动指令
        initial_prompt = await websocket.receive_text()
        logger.info(f"Received initial prompt: {initial_prompt}")

        # 将用户输入包装成 ADK 需要的格式
        content = types.Content(role='user', parts=[types.Part(text=initial_prompt)])

        # 2. 启动 agent 执行并流式传输事件
        logger.info("Starting agent run...")
        async for event in runner.run_async(
            user_id="websocket_user",
            session_id=session_id,
            new_message=content
        ):
            # 将每个 event 对象转换为 JSON 并通过 WebSocket 发送
            event_json = event.model_dump_json(exclude_none=True)
            await websocket.send_text(event_json)

        logger.info("Agent run finished.")
        await websocket.send_text('{"status": "Agent run finished."}')

    except WebSocketDisconnect:
        logger.info(f"Client for session {session_id} disconnected.")
    except Exception as e:
        logger.error(f"An error occurred in session {session_id}: {e}", exc_info=True)
        # 向客户端发送错误信息
        await websocket.send_text(f'{{"error": "{str(e)}"}}')
    finally:
        # 确保在结束时关闭连接
        if websocket.client_state.name != 'DISCONNECTED':
             await websocket.close()
        logger.info(f"WebSocket connection closed for session: {session_id}") 