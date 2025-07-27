from google.adk.agents import LlmAgent,BaseAgent,SequentialAgent,ParallelAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from typing import AsyncGenerator
from typing_extensions import override
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

count_number = 1000000000
tire_number = 10000
battery_number = 40000
frame_number = 10000


class FactoryChain(BaseAgent):

    plan_agent: LlmAgent
    tire_supply_agent: LlmAgent
    batter_supply_agent: LlmAgent  # 保持与构造函数参数一致
    frame_supply_agent: LlmAgent
    transport_agent: LlmAgent
    trade_agent: LlmAgent

    para_agent: ParallelAgent

    seq_tire_agent: SequentialAgent
    seq_battery_agent: SequentialAgent
    seq_frame_agent: SequentialAgent


    model_config = {"arbitrary_types_allowed": True}


    def __init__(
            self,
            name:str,
            plan_agent:LlmAgent,
            tire_supply_agent: LlmAgent,
            batter_supply_agent: LlmAgent,
            frame_supply_agent: LlmAgent,
            transport_agent: LlmAgent,
            trade_agent: LlmAgent,
    ):
        """
            初始化FactoryChain
            plan_agent: 一个拆分任务并且给子agent分发任务的agent
            tire_supply_agent: 轮胎供应商agent
            batter_supply_agent: 电池供应商agent
            frame_agent: 车架供应商agent
            transport_agent: 运输agent，规划最近的运输路线
            trade_agent:交易agent实现向供应商打款
        """
        # 为每个序列创建独立的、指令定制化的transport和trade agent实例

        # --- 轮胎供应链 Agents ---
        tire_transport_instruction = f"""
        你是一个专业的物流运输专家，负责轮胎的运输。请严格遵循以下步骤：
        1. 分析从{{tire_result}}获取的轮胎运输需求。
        2. 规划最短、最经济的运输路线。
        3. 安排合适的运输工具（标准货车），预计运输时间2天。
        4. 提供运输成本估算和时间安排。
        输出格式：
        - 运输方案：轮胎的具体运输安排
        - 运输成本：预估总费用
        - 时间安排：预计到达时间
        """
        tire_transport_agent = LlmAgent(
            name="tire_transport_agent",
            model="gemini-2.5-flash",
            description="轮胎专用物流运输Agent",
            instruction=tire_transport_instruction,
            output_key="tire_transport_result"
        )
        
        tire_trade_instruction = f"""
        你是一个财务交易专家，负责处理轮胎供应商的付款。请严格遵循以下步骤：
        1. 从{{tire_result}}获取订单金额，从{{tire_transport_result}}获取运输费用。
        2. 计算应付款项（轮胎单价：500元/个，物流费按实际计算）。
        3. 执行付款流程并更新财务记录。
        输出格式：
        - 付款明细：轮胎供应商和物流商的付款金额
        - 付款状态：已付款
        - 财务记录：交易流水号
        """
        tire_trade_agent = LlmAgent(
            name="tire_trade", 
            model="gemini-2.5-flash",
            description="轮胎交易结算Agent",
            instruction=tire_trade_instruction,
            output_key="tire_trade_result"
        )

        # --- 电池供应链 Agents ---
        battery_transport_instruction = f"""
        你是一个专业的物流运输专家，负责电池包的运输。请严格遵循以下步骤：
        1. 分析从{{battery_result}}获取的电池包运输需求。
        2. 规划最短、最经济的运输路线，并考虑防震要求。
        3. 安排合适的运输工具（防震专用车），预计运输时间3天。
        4. 提供运输成本估算和时间安排。
        输出格式：
        - 运输方案：电池包的具体运输安排
        - 运输成本：预估总费用
        - 时间安排：预计到达时间
        """
        battery_transport_agent = LlmAgent(
            name="battery_transport_agent",
            model="gemini-2.5-flash", 
            description="电池包专用物流运输Agent",
            instruction=battery_transport_instruction,
            output_key="battery_transport_result"
        )
        
        battery_trade_instruction = f"""
        你是一个财务交易专家，负责处理电池包供应商的付款。请严格遵循以下步骤：
        1. 从{{battery_result}}获取订单金额，从{{battery_transport_result}}获取运输费用。
        2. 计算应付款项（电池包单价：5000元/个，物流费按实际计算）。
        3. 执行付款流程并更新财务记录。
        输出格式：
        - 付款明细：电池包供应商和物流商的付款金额
        - 付款状态：已付款
        - 财务记录：交易流水号
        """
        battery_trade_agent = LlmAgent(
            name="battery_trade_agent",
            model="gemini-2.5-flash",
            description="电池包交易结算Agent", 
            instruction=battery_trade_instruction,
            output_key="battery_trade_result"
        )

        # --- 车架供应链 Agents ---
        frame_transport_instruction = f"""
        你是一个专业的物流运输专家，负责车架的运输。请严格遵循以下步骤：
        1. 分析从{{frame_result}}获取的车架运输需求。
        2. 规划最短、最经济的运输路线，并考虑防锈要求。
        3. 安排合适的运输工具（大型货车），预计运输时间2天。
        4. 提供运输成本估算和时间安排。
        输出格式：
        - 运输方案：车架的具体运输安排
        - 运输成本：预估总费用
        - 时间安排：预计到达时间
        """
        frame_transport_agent = LlmAgent(
            name="frame_transport_agent",
            model="gemini-2.5-flash",
            description="车架专用物流运输Agent",
            instruction=frame_transport_instruction,
            output_key="frame_transport_result"
        )
        
        frame_trade_instruction = f"""
        你是一个财务交易专家，负责处理车架供应商的付款。请严格遵循以下步骤：
        1. 从{{frame_result}}获取订单金额，从{{frame_transport_result}}获取运输费用。
        2. 计算应付款项（车架单价：3000元/个，物流费按实际计算）。
        3. 执行付款流程并更新财务记录。
        输出格式：
        - 付款明细：车架供应商和物流商的付款金额
        - 付款状态：已付款
        - 财务记录：交易流水号
        """
        frame_trade_agent = LlmAgent(
            name="frame_trade_agent",
            model="gemini-2.5-flash", 
            description="车架交易结算Agent",
            instruction=frame_trade_instruction,
            output_key="frame_trade_result"
        )

        seq_tire_agent = SequentialAgent(
            name="seq_tire_agent",
            description="轮胎供应链完整流程管理：从订单确认→物流配送→财务结算，确保轮胎按时按质交付并完成全流程闭环管理",
            sub_agents=[tire_supply_agent, tire_transport_agent, tire_trade_agent]
        )

        seq_battery_agent = SequentialAgent(
            name="seq_battery_agent",
            description="新能源电池包全链路管理：专业处理BATT-PACK-MODEL-X电池包的技术确认→安全运输→资金结算，严格执行新能源汽车电池安全标准",
            sub_agents=[batter_supply_agent, battery_transport_agent, battery_trade_agent]
        )

        seq_frame_agent = SequentialAgent(
            name="seq_frame_agent",
            description="汽车车架制造交付流程：高强度钢车架从生产质检→专业运输→付款结算的完整供应链管理，确保车架结构安全和交付质量",
            sub_agents=[frame_supply_agent, frame_transport_agent, frame_trade_agent]
        )

        para_agent = ParallelAgent(
            name="all_supply_agent", 
            description="汽车制造核心供应链协调中枢：统一协调轮胎、电池包、车架三大核心零部件的并行采购、生产和交付，实现供应链效率最大化和成本优化，确保整车生产的零部件同步到位",
            sub_agents=[seq_tire_agent, seq_battery_agent, seq_frame_agent]
        )

        # 调用父类构造函数，传入所有必需的字段
        super().__init__(
            name=name,
            sub_agents=[plan_agent, para_agent],
            plan_agent=plan_agent,
            tire_supply_agent=tire_supply_agent,
            batter_supply_agent=batter_supply_agent,
            frame_supply_agent=frame_supply_agent,
            transport_agent=transport_agent,
            trade_agent=trade_agent,
            para_agent=para_agent,
            seq_tire_agent=seq_tire_agent,
            seq_battery_agent=seq_battery_agent,
            seq_frame_agent=seq_frame_agent
        )

    

    """
    一个实现订单生成、任务分配、下单、入库和出库的Agent工作流。
    这个Agent向子agent分配任务，并且实现向子agent下订单，每一个Agent就是一个供应商，并且实现各个配件的出库和入库。

    """

  
    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        实现工厂供应链的自定义编排逻辑
        
        执行流程：
        1. 首先运行计划Agent (plan_agent) 进行任务拆解和计划制定
        2. 然后运行并行Agent (para_agent) 协调所有供应商同时工作：
           - seq_tire_agent: 轮胎供应 → 运输 → 交易
           - seq_battery_agent: 电池供应 → 运输 → 交易  
           - seq_frame_agent: 车架供应 → 运输 → 交易
        3. 收集和转发所有子Agent的执行事件
        4. 记录整个供应链的执行状态和结果
        
        Args:
            ctx: Agent执行上下文，包含输入数据和执行环境
            
        Yields:
            Event: 各个子Agent执行过程中产生的事件流
        """
        async for event in self.plan_agent.run_async(ctx):
             yield event
        
        if "plan_result" not in ctx.session.state or not ctx.session.state["plan_result"]:
            return
        
        async for event in self.para_agent.run_async(ctx):
            yield event
        


plan_agent = LlmAgent(
    name="plan_agent",
    model="gemini-2.5-flash",
    description="将生产计划进行拆分，让不同的agent进行任务的执行",
    instruction="""
        你是一个生产计划制定专家，负责将用户的生产需求拆解为详细的采购和生产任务。请严格遵循以下步骤：
        
        1. 分析用户输入的生产需求（如：生产多少辆车）
        2. 计算各个零部件的需求量：
           - 轮胎需求：车辆数量 × 4个/辆
           - 电池包需求：车辆数量 × 1个/辆  
           - 车架需求：车辆数量 × 1个/辆
           
        3. 制定生产时间安排：
           - 分析生产周期和交付时间要求
           - 考虑各供应商的生产能力
           - 制定合理的采购和生产计划
           
        4. 输出详细的生产计划，包括：
           - 总生产目标：需要生产XX辆车
           - 零部件需求明细：轮胎XX个，电池包XX个，车架XX个
           - 时间安排：预计总生产周期XX天
           - 质量要求：所有零部件必须通过质检
           
        示例输出格式：
        "生产计划：本次需要生产100辆新能源汽车。
        零部件需求：轮胎400个，电池包100个（型号BATT-PACK-MODEL-X），车架100个。
        预计生产周期：15天，要求所有零部件在第10天前到位。
        质量标准：符合国家新能源汽车标准。"
    """,
    output_key="plan_result"
)

tire_supply_agent = LlmAgent(
    name="tire_supply",
    model="gemini-2.5-flash",
    description=f"这是一个轮胎供应商Agent，Agent维护了一个轮胎数量{tire_number},每次plan_agent下发订单的时候就{tire_number}减去相对应的数量。",
    instruction=f"""
        你是一个轮胎供应商，专门处理来自plan_agent的下单请求,实现下单。请严格遵循以下步骤：
        
        1. 分析{{plan_result}},查看下了多少量订单的车，根据每辆车的数量 * 4获得要下单的轮胎数量，然后用当前库存 {tire_number}
        2. 计算所需轮胎总数 = 车辆数量 × 4
        3. 检查库存是否充足：当前库存{tire_number}个轮胎
        4. 如果库存够用，确认订单并更新库存
        5. 如果库存不足，提示需要补货多少个轮胎
    """,
    output_key="tire_result"
)

batter_supply_agent = LlmAgent(
    name="battery_supply_agent",
    model="gemini-2.5-flash",
    description="电池包供应商Agent，负责电池包的采购、库存管理和出库配送",
    instruction=f"""
        你是一个电池包供应商，专门处理电池包的订单请求。请严格遵循以下步骤：
        
        1. 分析{{plan_result}}中的生产计划，确定需要的电池包数量
        2. 每辆车需要1个电池包，计算总需求量
        3. 检查当前库存状态（假设库存充足）
        4. 确认电池包规格：BATT-PACK-MODEL-X
        5. 安排电池包的质检、包装和出库
        6. 预估交付时间并确认订单
        
        输出格式：
        - 订单确认：已接受XX个电池包的订单
        - 库存状态：当前库存充足/需要补货
        - 预计交付时间：X天内完成出库
        - 质量保证：所有电池包均通过质检
    """,
    output_key="battery_result"
)

frame_supply_agent = LlmAgent(
    name="frame_supply_agent",
    model="gemini-2.5-flash", 
    description="车架供应商Agent，负责车架的生产、质检和出库配送",
    instruction=f"""
        你是一个车架供应商，专门处理车架的订单请求。请严格遵循以下步骤：
        
        1. 分析{{plan_result}}中的生产计划，确定需要的车架数量
        2. 每辆车需要1个车架，计算总需求量
        
        3. 检查车架生产能力和库存状态
        4. 确认车架规格和材质要求
        5. 安排车架的焊接、质检和表面处理
        6. 准备车架的包装和出库
        
        输出格式：
        - 订单确认：已接受XX个车架的订单
        - 生产状态：正在生产/库存现货
        - 质检结果：所有车架通过强度测试
        - 预计交付：X天内完成生产和出库
    """,
    output_key="frame_result"
)

transport_agent = LlmAgent(
    name="transport_agent",
    model="gemini-2.5-flash",
    description="物流运输Agent，负责规划最优运输路线、车辆调度和货物跟踪",
    instruction=f"""
        你是一个专业的物流运输专家，负责协调各供应商的货物运输。请严格遵循以下步骤：
        
        1. 分析需要运输的货物类型和数量：
           - 从{{tire_result}}获取轮胎运输需求
           - 从{{battery_result}}获取电池包运输需求  
           - 从{{frame_result}}获取车架运输需求
        
        2. 制定综合运输方案：
           - 规划最短、最经济的运输路线
           - 考虑货物的特殊要求（电池包需要防震、车架需要防锈）
           - 安排合适的运输工具（卡车/专用运输车）
           
        3. 运输执行计划：
           - 轮胎运输：标准货车，预计运输时间2天
           - 电池包运输：防震专用车，预计运输时间3天
           - 车架运输：大型货车，预计运输时间2天
           
        4. 提供运输成本估算和时间安排
        
        输出格式：
        - 运输方案：各类货物的具体运输安排
        - 运输成本：预估总费用
        - 时间安排：各货物的预计到达时间
        - 跟踪服务：提供货物在途跟踪
    """,
    output_key="transport_result"
)

trade_agent = LlmAgent(
    name="trade_agent",
    model="gemini-2.5-flash",
    description="财务交易Agent，负责处理供应商付款、结算和财务记录",
    instruction=f"""
        你是一个财务交易专家，负责处理供应商的付款和结算。请严格遵循以下步骤：
        
        1. 收集各供应商的交易信息：
           - 轮胎供应商：从{{tire_result}}获取订单金额
           - 电池包供应商：从{{battery_result}}获取订单金额
           - 车架供应商：从{{frame_result}}获取订单金额
           - 物流服务商：从{{transport_result}}获取运输费用
           
        2. 计算各供应商的应付款项：
           - 轮胎单价：500元/个，按实际数量计算
           - 电池包单价：5000元/个，按实际数量计算
           - 车架单价：3000元/个，按实际数量计算
           - 物流费用：按运输方案计算
           
        3. 执行付款流程：
           - 核实订单和货物接收情况
           - 检查发票和质量验收单
           - 安排银行转账或票据支付
           - 更新财务系统记录
           
        4. 生成财务报告和付款凭证
        
        输出格式：
        - 付款明细：各供应商的具体付款金额
        - 付款状态：已付款/待付款/分期付款
        - 财务记录：交易流水号和凭证号
        - 成本分析：总采购成本和成本构成
    """,
    output_key="trade_result"
)

factory_agent = FactoryChain(
    name = "FactoryFlow_Agent",
    plan_agent = plan_agent,
    tire_supply_agent = tire_supply_agent,
    batter_supply_agent = batter_supply_agent,  # 修正参数名
    frame_supply_agent = frame_supply_agent,
    transport_agent = transport_agent,
    trade_agent = trade_agent)