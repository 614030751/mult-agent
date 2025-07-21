# 工业多Agent协作系统

这是一个基于区块链的工业企业多Agent协作系统，集成了任务拆解、Agent身份管理、交易记录和顺序执行链路。

## 系统特性

### 核心功能
1. **任务拆解与分发** - 接收用户指令，智能拆解为子任务
2. **区块链身份管理** - 每个Agent都有唯一的区块链身份
3. **交易记录** - 所有Agent交互都记录在区块链上
4. **顺序执行链路** - 按业务流程顺序执行各个Agent
5. **工业企业专用** - 针对工业场景优化的Agent

### 区块链特性
- **Agent身份注册** - 每个Agent在区块链上注册身份
- **交易签名** - 所有交易都有数字签名
- **交易类型** - 支持任务创建、分配、执行、完成等类型
- **不可篡改** - 所有交易记录不可篡改

## 系统架构

### Agent组成
1. **任务分析Agent** (`task_analyzer`)
   - 分析用户任务并拆解为子任务
   - 使用Gemini 2.5 Flash模型
   - 考虑工业生产的各个环节

2. **设计Agent** (`design_agent`)
   - 负责产品设计和工艺设计
   - CAD建模和技术文档生成
   - 工具：产品设计、CAD建模

3. **采购Agent** (`procurement_agent`)
   - 负责原材料采购和供应商管理
   - 成本分析和合同管理
   - 工具：供应商评估、成本计算

4. **生产Agent** (`production_agent`)
   - 负责生产计划和工艺执行
   - 设备管理和产能优化
   - 工具：生产计划、生产监控

5. **质检Agent** (`quality_agent`)
   - 负责质量检测和控制
   - 质量报告和标准制定
   - 工具：质量检测、质量报告生成

6. **物流Agent** (`logistics_agent`)
   - 负责物流配送和仓储管理
   - 运输优化和库存管理
   - 工具：物流计划、货物跟踪

7. **维护Agent** (`maintenance_agent`)
   - 负责设备维护和故障诊断
   - 预防性维护和维修计划
   - 工具：设备诊断、维护计划

### 执行链路
```
用户输入 → 任务分析 → 产品设计 → 采购计划 → 生产计划 → 质量检测 → 物流配送
```

## 工业企业应用场景

### 通用应用场景
1. **产品开发**
   - 新产品设计
   - 工艺设计优化
   - 技术文档生成
   - CAD模型创建

2. **供应链管理**
   - 供应商评估
   - 采购计划制定
   - 成本分析
   - 合同管理

3. **生产管理**
   - 生产计划制定
   - 工艺执行监控
   - 设备管理
   - 产能优化

4. **质量控制**
   - 质量检测
   - 质量控制
   - 质量报告生成
   - 标准制定

5. **物流配送**
   - 配送计划制定
   - 仓储管理
   - 运输优化
   - 库存管理

6. **设备维护**
   - 设备诊断
   - 预防性维护
   - 故障处理
   - 维护计划制定

### 特定行业场景

#### 汽车工业
- 车身设计
- 发动机工艺
- 零部件采购
- 装配线优化
- 质量检测
- 供应链管理

#### 电子工业
- 电路设计
- PCB制造
- 元器件采购
- SMT工艺
- 功能测试
- 可靠性验证

#### 化工工业
- 工艺设计
- 设备选型
- 安全评估
- 质量控制
- 环保监测
- 供应链管理

#### 食品工业
- 配方设计
- 工艺优化
- 原料采购
- 质量控制
- 包装设计
- 物流配送

#### 制药工业
- 药物设计
- 工艺开发
- 原料采购
- 质量控制
- 合规管理
- 供应链追溯

## 安装和配置

### 环境要求
```bash
Python 3.8+
google-adk-agents
requests
flask (可选，用于API服务器)
```

### 安装依赖
```bash
pip install google-adk-agents requests flask
```

### 配置
编辑配置文件，根据需要修改：
- API配置
- Agent模型配置
- 区块链配置
- 日志配置

## 使用方法

### 基本使用

```python
from industrial_agent_system import IndustrialAgentSystem

# 创建系统实例
system = IndustrialAgentSystem()

# 处理工业任务
result = system.process_industrial_task(
    "我需要开发一个新的工业传感器产品，包括设计、采购、生产、质检和物流配送"
)

print(result)
```

### API接口使用

```python
from industrial_api_interface import IndustrialMultiAgentAPI

# 创建API实例
api = IndustrialMultiAgentAPI()

# 处理产品开发任务
result = api.handle_industrial_request({
    "input": "我需要开发一个新的工业传感器产品",
    "type": "product_development",
    "use_blockchain": True
})

print(result)
```

### 启动API服务器

```python
from industrial_api_interface import create_industrial_api_server

app = create_industrial_api_server()
app.run(host='0.0.0.0', port=5001, debug=True)
```

## API端点

### 工业Agent API
- `POST /api/industrial/process` - 处理工业请求
- `GET /api/industrial/info` - 获取工业系统信息
- `GET /api/industrial/agents` - 获取工业Agent信息
- `GET /api/industrial/chain/<task_id>` - 获取执行链路
- `GET /api/industrial/blockchain/transactions` - 获取区块链交易

### Agent Chain API集成
- 支持与外部Agent Chain API通信
- 可配置的API端点
- 错误处理和重试机制

## 区块链功能

### 交易类型
1. **TASK_CREATION** - 任务创建
2. **TASK_ASSIGNMENT** - 任务分配
3. **TASK_EXECUTION** - 任务执行
4. **TASK_COMPLETION** - 任务完成
5. **AGENT_REGISTRATION** - Agent注册
6. **AGENT_AUTHENTICATION** - Agent认证

### Agent身份管理
```python
# 注册Agent身份
agent_identity = AgentIdentity(
    agent_id="design_agent",
    agent_name="设计专家",
    agent_type="design",
    capabilities=["产品设计", "工艺设计", "CAD建模"],
    public_key="pub_key_design_agent",
    registration_timestamp=time.time()
)

# 注册到区块链
transaction = blockchain_manager.register_agent(agent_identity)
```

### 交易记录
```python
# 创建交易
transaction = blockchain_manager.create_transaction(
    TransactionType.TASK_EXECUTION,
    "design_agent",
    "production_agent",
    {"task_data": "设计完成，开始生产"}
)
```

## 执行链路示例

### 产品开发流程
```
1. 任务分析Agent: 分析产品开发需求
   ↓
2. 设计Agent: 产品设计和CAD建模
   ↓
3. 采购Agent: 原材料采购和供应商评估
   ↓
4. 生产Agent: 生产计划和工艺执行
   ↓
5. 质检Agent: 质量检测和报告生成
   ↓
6. 物流Agent: 物流配送和仓储管理
```

### 设备维护流程
```
1. 任务分析Agent: 分析设备故障情况
   ↓
2. 维护Agent: 设备诊断和故障分析
   ↓
3. 采购Agent: 备件采购和供应商联系
   ↓
4. 维护Agent: 制定维护计划和执行维护
   ↓
5. 质检Agent: 维护质量验证
   ↓
6. 生产Agent: 设备重新投入生产
```

## 扩展开发

### 添加新的Agent
1. 在 `industrial_agent_system.py` 中定义新的Agent
2. 添加相应的工具函数
3. 在区块链上注册Agent身份
4. 更新执行链路

### 添加新的工具函数
1. 定义工具函数
2. 在相应的Agent中注册工具
3. 更新系统配置

### 自定义区块链功能
1. 扩展交易类型
2. 添加新的区块链操作
3. 实现更复杂的身份管理

## 故障排除

### 常见问题
1. **Agent执行失败**
   - 检查Agent身份是否已注册
   - 验证区块链交易记录
   - 查看执行日志

2. **区块链连接问题**
   - 检查网络连接
   - 验证区块链配置
   - 查看交易状态

3. **API集成问题**
   - 检查API端点配置
   - 验证请求格式
   - 查看错误日志

## 性能优化

### 并发处理
- 支持多个任务并行处理
- 智能任务调度
- 资源优化分配

### 缓存机制
- Agent结果缓存
- 区块链交易缓存
- 执行链路缓存

### 监控和日志
- 实时性能监控
- 详细执行日志
- 区块链交易日志

## 安全特性

### 身份验证
- 每个Agent都有唯一身份
- 区块链身份验证
- 数字签名验证

### 数据安全
- 交易数据加密
- 敏感信息保护
- 访问权限控制

### 审计追踪
- 完整的执行链路记录
- 区块链交易审计
- 操作日志追踪

## 许可证

本项目基于MIT许可证开源。

## 贡献

欢迎提交Issue和Pull Request来改进这个工业多Agent系统。 