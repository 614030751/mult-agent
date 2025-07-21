# 多Agent系统

这是一个基于Google ADK Agents的多Agent系统，集成了代码生成、代码审查、测试生成、文档生成、天气查询等功能。

## 系统特性

### 核心Agent
1. **代码生成Agent** (`code_writer_agent`)
   - 根据需求生成Python代码
   - 使用Gemini 2.5 Flash模型
   - 遵循PEP 8规范

2. **代码审查Agent** (`code_reviewer_agent`)
   - 分析代码质量和潜在问题
   - 提供改进建议
   - 识别代码中的TODO/FIXME标记

3. **测试生成Agent** (`test_generator_agent`)
   - 为代码生成测试用例
   - 包括单元测试和集成测试
   - 测试边界条件和异常情况

4. **文档生成Agent** (`documentation_agent`)
   - 为代码生成文档
   - 包括API文档和使用示例
   - 生成函数和类的文档字符串

5. **天气时间Agent** (`weather_time_agent`)
   - 查询城市天气信息
   - 获取指定城市的当前时间
   - 支持多个城市的时区信息

6. **主控制器Agent** (`main_controller`)
   - 协调各个专门Agent的工作
   - 根据用户需求选择合适的Agent
   - 管理Agent之间的协作

### Agent链
- **代码开发链** (`code_development_chain`)
  - 完整的代码开发流程
  - 顺序执行：生成代码 → 审查代码 → 生成测试 → 生成文档

## 安装和配置

### 1. 环境要求
```bash
Python 3.8+
google-adk-agents
requests
flask (可选，用于API服务器)
```

### 2. 安装依赖
```bash
pip install google-adk-agents requests flask
```

### 3. 配置
编辑 `config.py` 文件，根据需要修改配置参数：
- API配置
- Agent模型配置
- 工具函数配置
- 日志配置

## 使用方法

### 基本使用

```python
from multi_agent_system import MultiAgentSystem

# 创建系统实例
system = MultiAgentSystem()

# 代码生成
result = system.process_request("请生成一个计算斐波那契数列的函数")
print(result)

# 天气查询
result = system.process_request("纽约的天气怎么样？")
print(result)

# 时间查询
result = system.process_request("纽约现在几点了？")
print(result)
```

### API接口使用

```python
from api_interface import MultiAgentAPI

# 创建API实例
api = MultiAgentAPI()

# 本地处理
result = api.handle_request({
    "input": "请生成一个排序算法",
    "type": "local"
})

# 使用Agent Chain API
result = api.handle_request({
    "input": "请审查这段代码",
    "type": "agent_chain"
})
```

### 启动API服务器

```python
from api_interface import create_api_server

app = create_api_server()
app.run(host='0.0.0.0', port=5000, debug=True)
```

## API端点

### 本地API服务器
- `POST /api/process` - 处理用户请求
- `GET /api/info` - 获取系统信息
- `GET /api/agents` - 获取所有Agent信息

### Agent Chain API集成
- 支持与外部Agent Chain API通信
- 可配置的API端点
- 错误处理和重试机制

## 示例

### 代码生成示例
```python
# 生成斐波那契函数
result = system.process_request("请生成一个计算斐波那契数列的函数")
# 返回生成的代码和相关信息
```

### 代码审查示例
```python
# 审查代码
result = system.process_request("请审查这段代码的质量")
# 返回审查结果和改进建议
```

### 天气查询示例
```python
# 查询天气
result = system.process_request("纽约的天气怎么样？")
# 返回天气信息
```

## 系统架构

```
MultiAgentSystem
├── main_controller (主控制器)
├── code_development_chain (代码开发链)
│   ├── code_writer_agent (代码生成)
│   ├── code_reviewer_agent (代码审查)
│   ├── test_generator_agent (测试生成)
│   └── documentation_agent (文档生成)
├── weather_time_agent (天气时间)
└── 工具函数
    ├── get_weather()
    ├── get_current_time()
    ├── analyze_code()
    ├── generate_tests()
    └── generate_documentation()
```

## 配置说明

### API配置
- `agent_chain_base_url`: Agent Chain API的基础URL
- `timeout`: 请求超时时间
- `retry_count`: 重试次数

### Agent模型配置
- 为每个Agent指定使用的模型
- 支持不同的Gemini模型版本

### 工具函数配置
- 支持的天气查询城市
- 时区映射配置

## 扩展开发

### 添加新的Agent
1. 在 `multi_agent_system.py` 中定义新的Agent
2. 添加相应的工具函数
3. 在 `MultiAgentSystem` 类中注册新Agent
4. 更新配置文件和文档

### 添加新的工具函数
1. 定义工具函数
2. 在相应的Agent中注册工具
3. 更新系统配置

## 故障排除

### 常见问题
1. **API连接失败**
   - 检查网络连接
   - 验证API端点配置
   - 检查防火墙设置

2. **Agent执行失败**
   - 检查模型配置
   - 验证工具函数
   - 查看日志文件

3. **内存使用过高**
   - 调整并发请求数量
   - 启用缓存机制
   - 优化Agent配置

## 日志

系统日志保存在 `multi_agent_system.log` 文件中，包含：
- 请求处理信息
- 错误和异常
- 性能统计
- API调用记录

## 许可证

本项目基于MIT许可证开源。

## 贡献

欢迎提交Issue和Pull Request来改进这个多Agent系统。 