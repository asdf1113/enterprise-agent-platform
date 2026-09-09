
# Customer Brief

## 1. Customer Background

### Customer Profile

本项目模拟一家中型 B2B 制造企业，该企业拥有多个业务部门，包括销售、售后、产品、运营和管理部门。

企业规模：

- 员工规模：约 800 - 1500 人
- 业务范围：工业设备及相关解决方案销售
- IT环境：已有 CRM、ERP 和内部数据库系统
- 数据环境：
  - 企业知识文档
  - 产品资料
  - 销售数据
  - 客户信息
  - 售后工单数据


企业已经积累大量业务数据和知识资产，但由于数据分散在不同系统中，员工仍主要依靠人工查询和经验完成日常工作。


---

# 2. Current Workflow and Challenges

## 2.1 Knowledge Retrieval Problem

### Current Process

员工需要查询企业知识时：

1. 登录内部文档系统
2. 搜索关键词
3. 浏览多个文档
4. 手动确认答案


例如：

> "X200设备的保修期限是多少？"

员工需要：

- 找产品手册
- 找售后政策
- 确认版本


### Existing Problems

- 文档数量增长导致搜索效率下降
- 关键词搜索无法理解自然语言问题
- 信息分散，需要人工判断
- 新员工学习成本较高


---

## 2.2 Business Data Analysis Problem

### Current Process

业务人员需要分析数据时：

1. 联系数据团队
2. 提出分析需求
3. 等待SQL查询
4. 获取Excel结果
5. 人工分析


例如：

> "华南区域Q2销售额最高的产品是什么？"


需要：

- 数据人员查询数据库
- 导出结果
- 生成分析报告


### Existing Problems

- 数据分析依赖技术人员
- 响应周期长
- 非技术人员无法直接使用业务数据


---

## 2.3 Cross-System Decision Problem

### Current Process

复杂业务分析需要人工整合：

- 数据库信息
- 企业制度
- 产品知识
- 销售策略


例如：

> "分析华南区域Q2销售下降原因，并结合营销政策提出改进建议"


当前流程：
```
销售数据查询
    +
政策文档查询
    +
人工分析
    +
生成报告
```


### Existing Problems

- 多系统之间缺少连接
- 分析过程依赖个人经验
- 工作流程重复且低效


---

# 3. Business Requirements

企业希望建设一个智能化工作平台，使员工能够通过自然语言完成：

1. 企业知识查询
2. 业务数据分析
3. 跨系统信息整合
4. 部分业务操作自动化


目标：

> 将人工驱动的信息查询和分析流程转变为 AI Agent 驱动的智能工作流。


---

# 4. Expected Solution

建设 Enterprise Agent Platform：

通过 Agent Runtime 连接：

- 企业知识库
- 业务数据库
- 企业系统接口


实现：
```
Natural Language Request
      |
  Agent Runtime
      |
Knowledge / Data / Business Tools
      |
  Final Answer
  or Action
```


---

# 5. Success Criteria

系统成功标准：

## Efficiency

减少员工完成信息查询和分析任务的时间。


## Accuracy

回答需要：

- 基于企业真实数据
- 提供来源引用
- 避免无依据生成


## Usability

非技术人员能够通过自然语言完成任务。


## Security

保证：

- 企业数据权限控制
- 工具调用安全
- 敏感操作人工确认


---

# 6. Project Scope

## In Scope

本PoC实现：

- Enterprise Knowledge Agent
- Business Data Agent
- Multi-step Analysis Workflow
- Tool Calling
- Human Approval Workflow
- Evaluation Framework


## Out of Scope

本阶段不实现：

- 大规模多租户SaaS平台
- 自研基础模型
- Kubernetes生产集群
- 完整CRM系统
- 自动化业务决策替代人工


---

# 7. Key User Scenarios

## Scenario 1: Knowledge Assistant

用户：

> X200设备售后政策是什么？

系统：

- 检索知识库
- 返回答案
- 提供引用


---

## Scenario 2: Data Assistant

用户：

> 查询华南区域Q2销售额。


系统：

- 调用数据工具
- 查询数据库
- 返回统计结果


---

## Scenario 3: Business Analysis Agent

用户：

> 分析华南区域销售下降原因。


系统：

- 查询销售数据
- 检索营销政策
- 综合分析
- 输出报告


---

## Scenario 4: Business Operation Agent

用户：

> 创建客户售后跟进任务。


系统：

- 生成操作计划
- 请求人工确认
- 调用CRM接口
