from google.adk.agents import LlmAgent, SequentialAgent, BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.events import Event
from pydantic import BaseModel, Field
from typing import AsyncGenerator  
from typing_extensions import override
import logging
import requests
class ChainAgent(BaseAgent):
    """
        自定义Agent，实现链上操作。
        下发多个agent共同完成任务：
        1.生成钱包地址并创建DDO文档Agent
        2.VC证书创建Agent
        3.VC证书验证Agent
        4.交易Agent
    """
    wallet_agent: LlmAgent
    vccreate_agent: LlmAgent
    verify_agent: LlmAgent
    trans_agent: LlmAgent
    sequential_agent: SequentialAgent

    def __init__(self, name: str, wallet_agent: LlmAgent, vccreate_agent: LlmAgent, verify_agent: LlmAgent, trans_agent: LlmAgent):
        """
        初始化ChainAgent

        Args：
            name: Agent名称
            wallet_agent: 创建钱包的agent
            vcreate_agent：VC证书创建Agent
            veify_agent:VC证书验证Agent
            trans_agent:交易Agent
        """
        sequential_agent = SequentialAgent(
            name="ChainOperationSequenceAgent",
            sub_agents=[wallet_agent]
        )

        sub_agent_list = [
            sequential_agent
        ]

        super().__init__(
            name=name,
            wallet_agent=wallet_agent,
            vccreate_agent=vccreate_agent,
            veify_agent=verify_agent,
            trans_agent=trans_agent,
            sequential_agent=sequential_agent,
            sub_agents=sub_agent_list
        )

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        实现了链上操作的的自定义编排逻辑
        """
        logging.Logger.info("开始链上操作的自定义编排")

        # 1.初始化ChainOperationSequenceAgent
        logging.Logger.info(f"[{self.name}] 运行 ChainOperationSequenceAgent...")
        async for event in self.sequential_agent.run_async(ctx):
            logging.logger.info(f"[{self.name}] Event from ChainOperationSequenceAgent: {event.model_dump_json(indent=2, exclude_none=True)}")
            yield event


def createwallet():
    response = requests.post(url="http://192.168.2.19:9090/agent-chain/chain/createWalletAndDDO")
    print("正在调用createwallet")
    if response.status_code == 200:
        try:
            response_data = response.json()
            wallet_address = response_data["data"]["walletAddress"]
            return wallet_address
        except KeyError:
                    print("响应结构异常：未找到walletAddress字段")
        except requests.exceptions.JSONDecodeError:
                    print("响应非JSON格式")
        else:
                    print(f"请求失败，状态码：{response.status_code}")

        return f"请求失败，状态码：{response.status_code}"


# ---定义个体的LLM agents ---
wallet_agent = LlmAgent(
    name="wallet_agent",
    model="gemini-2.5-flash",
    description="用来创建钱包，并且实现DDO文档的创建",
    instruction="""
        你是一个链上钱包创建助手，专门处理API调用任务,每次调用createwallet工具，实现链上钱包创建和DDO文档的创建,生成的钱包可以给vccreate_agent来创建vc证书。请严格遵循以下步骤：  
        1. **请求方法**：使用HTTP POST方法调用指定API接口。  
        2. **数据传递**：  
            - 没有请求体。  
        3. **返回处理**：  
            - **禁止**解析、过滤或转换响应数据。  
            - 无论返回的是JSON、二进制流、纯文本还是XML，均以原始格式直接输出。  
        4. **异常处理**：  
            - 若HTTP状态码非2xx（如404/500），返回完整错误信息（含状态码和响应体）。  
            - 若网络中断，明确提示“网络请求失败”并附错误详情。  

        **用户输入示例**：
          {
            "url": "http://192.168.2.19:9090/agent-chain/doc.html",
            "headers": {
                        "connection": "keep-alive",
                        "Content-Type": "application/json",
                        "date": "Mon, 21 Jul 2025 06:57:05 GMT",
                        "keep": "timeout=5",
                        "transfer-encoding": "chunked",
                        "vary": "Origin, Access-Control-Request-Method, Access-Control-Request-Headers",
                        },
          }
        
        **输出实例**：
          {
            "msg": "success",
            "code": 0,
            "data": {
                      "walletAddress": "did:bid:ef2AzoFH4h1FfbBgyzyfxNrfKNSeXuZsd",
                      "privateKey": "priSPKmQPUN7Uj1iHWWSfJhxeseXvzmGYRRQAqsQLpoAU3dpww",
                      "publicKey": "b065668005529933bfa9d194b232243d11d210d61d7383fa97f8b9a58dc8dd64913a54",
                      "ddoHash": "7a961476188cc723034a2d386286f06dd9b6861b0097109aced3043bf1d51561",
                      "permitRequestNo": "916a143d-ca93-4727-9b00-fa1106f27cd0",
                      "createTime": "2025-07-21T15:41:32.019",
                      "message": "钱包地址生成成功，DDO文档创建成功，备案申请已提交"
                    },
        }
""",
        tools=[createwallet],
        output_key="wallet_address"
)


def createvc(subjectBid: str, subjectType: str = "Agent"):
    url = "http://192.168.2.19:9090/agent-chain/chain/vc/issue"  # 修正URL路径
    headers = {"Content-Type": "application/json"}  # 显式声明JSON格式
    payload = {
        "subjectType": subjectType,  # 使用函数参数
        "subjectBid": subjectBid
    }
    
    try:
        # 使用 json 参数传递数据（自动设置Content-Type）
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        response.raise_for_status()  # 自动检查HTTP状态码（非2xx抛异常）
        return response.json().get("result", {}).get("vcContent", "")  # 安全获取字段
    except requests.exceptions.RequestException as e:
        logging.error(f"VC创建请求失败: {e}")
        return f"错误: {str(e)}"
    except KeyError:
        logging.error("响应结构异常，未找到vcContent字段")
        return "错误: 响应结构异常"
      
      
      

vccreate_agent = LlmAgent(
      name="vccreate_agent",
      model="gemini-2.5-flash",
      instruction="""
        你是一个链上颁发VC证书助手，专门处理API调用任务,每次调用createvc工具，实现VC证书的颁发。请严格遵循以下步骤：
        1. **请求方法**：使用HTTP POST方法调用指定API接口。
        2. **数据传递**：传递两个参数 
            1.`subjectBid`: 钱包地址
            2.`subjectType`: agent 默认参数为agent
        3. **返回处理**：  
            - **禁止**解析、过滤或转换响应数据。  
            - 无论返回的是JSON、二进制流、纯文本还是XML，均以原始格式直接输出。  
        4. **异常处理**：  
            - 若HTTP状态码非2xx（如404/500），返回完整错误信息（含状态码和响应体）。  
            - 若网络中断，明确提示“网络请求失败”并附错误详情。  
        **用户输入示例**：
          {
            "url": "http://192.168.2.19:9090/agent-chain/chain/vc/issue",
            "headers": {
                        "connection": "keep-alive",
                        "Content-Type": "application/json",
                        "date": "Mon, 21 Jul 2025 06:57:05 GMT",
                        "keep-alive": "timeout=5",
                        "transfer-encoding": "chunked",
                        "vary": "Origin, Access-Control-Request-Method, Access-Control-Request-Headers",
                        },
            "body": {
                        "subjectBid": "{wallet_address}",
                        "subjectType": "agent"
            }
          }
        **输出实例**：
        {
            "msg": "success",
            "result": {
                "success": true,
                "vcContent": "eyJ0eXAiOiJKV1QiLCJhbGciOiJTTTIifQ.eyJjb250ZXh0IjpbImh0dHBzOi8vd3d3LnczLm9yZy8yMDE4L2NyZWRlbnRpYWxzL3YxIiwiaHR0cHM6Ly94aW5naHVvLmNhaWN0LmFjLmNuL3ZjL3YxIl0sImlkIjoidmM6YmlkOjAyNjVlN2VhLTBiNzgtNDI3Yy1hNzMyLTNmYWRlMzY1NzY0MyIsInR5cGUiOlsiVmVyaWZpYWJsZUNyZWRlbnRpYWwiLCJJZGVudGl0eUNyZWRlbnRpYWwiXSwiaXNzdWVyIjoiZGlkOmJpZDplZjI4dGNoMTVqdzRyWGhWaDlNYWhuVldqMThHS2J2emUiLCJpc3N1YW5jZURhdGUiOiIyMDI1LTA3LTIxVDE2OjMwOjM3LjQ4MyswODowMFtBc2lhL1NoYW5naGFpXSIsInZhbGlkQmVmb3JlIjoiMjAyNi0wNy0yMVQxNjozMDozNy40ODMrMDg6MDBbQXNpYS9TaGFuZ2hhaV0iLCJjcmVkZW50aWFsU3ViamVjdCI6eyJpc3N1ZWRCeSI6IuaYn-eBq-mTvue9kVZD6K-B5Lmm6aKB5Y-R5py65p6EIiwibmFtZSI6Ium7mOiupOS7o-eQhiIsImRlc2NyaXB0aW9uIjoi5Z-65LqO5pif54Gr6ZO-572R55qE5Luj55CG6Lqr5Lu96K6k6K-B6K-B5LmmIiwiaWQiOiJkaWQ6YmlkOmVmbzVIUnVGUlJBRFRWVUFwUHV4RkZrUDlvcUFQZXRyIiwidHlwZSI6IkFnZW50In19.4rORVQKmzXecVIy5MwaFO1Lx8VuQk_9nqF1BYLKn95A",
                "credential": {
                    "context": [
                        "https://www.w3.org/2018/credentials/v1",
                        "https://xinghuo.caict.ac.cn/vc/v1"
                            ],
                    "id": "vc:bid:0265e7ea-0b78-427c-a732-3fade3657643",
                    "type": [
                    "VerifiableCredential",
                    "IdentityCredential"
                        ],
                "issuer": "did:bid:ef28tch15jw4rXhVh9MahnVWj18GKbvze",
                "issuanceDate": "2025-07-21T16:30:37.483+08:00[Asia/Shanghai]",
                "validBefore": "2026-07-21T16:30:37.483+08:00[Asia/Shanghai]",
                "credentialSubject": {
                "issuedBy": "星火链网VC证书颁发机构",
                "name": "默认代理",
                "description": "基于星火链网的代理身份认证证书",
                "id": "did:bid:efo5HRuFRRADTVUApPuxFFkP9oqAPetr",
                "type": "Agent"
                },
            "proof": null,
            "templateId": null,
            "selectiveDisclosure": nullzhengsh
        },
            "verified": null,
            "errorMessage": null,
            "status": "issued",
            "timestamp": 1753086637483
  },
       "code": 0,
       "message": "VC证书颁发成功"
    } 
    """,
    description="通过钱包地址来创建VC证书的Agent",
    tools=[createvc]
)




root_agent = LlmAgent(
       name="create_wallet_vc",
       model="gemini-2.5-flash",
        instruction="创建钱包使用wallet_agent,vc认证调用vccreate_agent，且需要有钱包地址wallet_address,如果没有可以用wallet_agent创建，然后再创建vc证书",
       sub_agents=[wallet_agent,vccreate_agent]
)