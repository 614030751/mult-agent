import asyncio
import websockets
import json

async def run_test_client():
    """一个简单的 WebSocket 客户端，用于测试 FastAPI 服务器."""
    uri = "ws://localhost:8000/ws/test_session_123"
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Connected to {uri}")

            # 1. 发送初始指令
            prompt = "生产100辆新能源汽车"
            print(f"▶️ Sending prompt: '{prompt}'")
            await websocket.send(prompt)
            print("--------------------------------------------------")

            # 2. 循环接收服务器发来的事件流
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)

                    # 美化打印 JSON
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                    print("--------------------------------------------------")
                    
                    # 检查是否是结束信号
                    if data.get("status") == "Agent run finished.":
                        print("🏁 Agent run finished.")
                        break
                    if "error" in data:
                        print(f"❌ Received error: {data['error']}")
                        break

                except websockets.ConnectionClosed:
                    print("🛑 Connection closed by server.")
                    break

    except Exception as e:
        print(f"🔥 An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(run_test_client()) 