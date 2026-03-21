# 插件系统使用指南

## 概述

SynergyAI 插件系统允许用户创建自定义智能体（Agent），扩展系统的协作能力。通过插件，您可以定义具有特定角色、技能和行为方式的 AI 智能体。

## 插件结构

每个插件是一个 JSON 文件，包含以下字段：

### 必填字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | 插件名称 |
| `description` | string | 插件功能描述 |
| `role` | string | 角色标识符（只能包含小写字母、数字和下划线） |
| `display_name` | string | 显示名称 |
| `system_prompt` | string | 系统提示词，定义智能体的行为和角色 |
| `capabilities` | array | 能力列表，描述插件能做什么 |

### 可选字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `temperature` | number | 0.7 | 模型温度参数（0-2） |
| `max_tokens` | number | 2000 | 最大生成 token 数 |
| `enabled` | boolean | true | 是否启用 |
| `tags` | array | [] | 标签列表 |
| `author` | string | "" | 作者 |
| `version` | string | "1.0.0" | 版本号 |
| `metadata` | object | {} | 自定义元数据 |

## 创建插件

### 方式一：通过 Web UI 创建

1. 点击右上角用户头像
2. 选择"插件管理"
3. 点击"创建插件"按钮
4. 填写表单并提交

### 方式二：手动创建 JSON 文件

在 `plugins/` 目录下创建 JSON 文件：

```json
{
  "id": "my_custom_agent",
  "name": "我的智能体",
  "description": "这是一个自定义智能体",
  "role": "custom_agent",
  "display_name": "自定义助手",
  "system_prompt": "你是一个专业的助手，擅长...",
  "capabilities": [
    "能力1",
    "能力2"
  ],
  "temperature": 0.7,
  "max_tokens": 2000,
  "enabled": true,
  "tags": ["自定义"],
  "author": "your_name"
}
```

## 插件示例

### 示例 1：代码审查员

```json
{
  "id": "code_reviewer",
  "name": "代码审查员",
  "description": "专注于代码质量和最佳实践的审查专家",
  "role": "code_reviewer",
  "display_name": "代码审查员",
  "system_prompt": "你是一位经验丰富的代码审查员，擅长：\n\n1. 识别代码中的 bug 和潜在问题\n2. 提出代码改进建议\n3. 确保代码符合最佳实践\n4. 检查代码的可读性和可维护性\n\n审查时，请：\n- 具体指出问题位置\n- 解释为什么这是问题\n- 提供改进建议\n- 保持建设性的语气",
  "capabilities": [
    "代码审查",
    "bug 检测",
    "性能优化建议",
    "最佳实践指导"
  ],
  "temperature": 0.5,
  "max_tokens": 2000,
  "enabled": true,
  "tags": ["开发", "代码质量"],
  "author": "system"
}
```

### 示例 2：文档撰写专家

```json
{
  "id": "technical_writer",
  "name": "技术文档专家",
  "description": "专注于技术文档撰写和维护的专家",
  "role": "tech_writer",
  "display_name": "文档专家",
  "system_prompt": "你是一位专业的技术文档撰写专家，擅长：\n\n1. 编写清晰、准确的技术文档\n2. 将复杂的概念简化为易懂的内容\n3. 创建用户指南和 API 文档\n4. 维护文档的更新和一致性\n\n撰写文档时，请：\n- 使用清晰简洁的语言\n- 提供具体的示例\n- 保持结构化和层次化\n- 考虑读者的技术水平",
  "capabilities": [
    "技术文档撰写",
    "用户指南编写",
    "API 文档维护",
    "教程制作"
  ],
  "temperature": 0.6,
  "max_tokens": 2500,
  "enabled": true,
  "tags": ["文档", "写作"],
  "author": "system"
}
```

## 插件管理

### 导出插件

1. 在插件列表中找到要导出的插件
2. 点击导出按钮
3. JSON 文件将自动下载

### 导入插件

1. 在插件管理页面点击"导入"按钮
2. 选择之前导出的 JSON 文件
3. 系统会自动创建插件的副本（ID 会自动生成新的，避免冲突）

### 启用/禁用插件

- 点击插件卡片上的启用/禁用按钮
- 禁用的插件不会在系统中使用

### 删除插件

- 点击插件卡片上的删除按钮
- 确认后插件将被永久删除

## 最佳实践

### 1. 系统提示词设计

好的系统提示词应该：

- **明确角色定位**：清晰定义智能体的角色和职责
- **列出具体能力**：说明智能体能做什么
- **设定行为准则**：规定智能体应该如何行动
- **提供工作流程**：给出完成任务的具体步骤

示例结构：

```
你是一位[角色]，专注于[领域]。

## 核心能力
1. [能力1]
2. [能力2]
3. [能力3]

## 工作原则
- [原则1]
- [原则2]
- [原则3]

## 工作流程
1. [步骤1]
2. [步骤2]
3. [步骤3]

请始终遵循增量工作原则，一次专注完成一个任务。
```

### 2. 角色标识符命名

- 使用小写字母
- 使用下划线分隔单词
- 保持简洁但描述性
- 避免与内置角色冲突（hr, pm, ba, dev, qa, architect）

好的示例：
- `code_reviewer`
- `data_analyst`
- `ux_designer`

不好的示例：
- `CodeReviewer`（大写）
- `code-reviewer`（使用连字符）
- `agent1`（不够描述性）

### 3. 能力列表

- 每个能力应该是简短的动词短语
- 保持能力列表简洁（3-6 个）
- 确保能力与实际功能匹配

### 4. 温度参数选择

| 用途 | 推荐温度 | 说明 |
|------|----------|------|
| 代码生成/审查 | 0.3-0.5 | 需要精确性和一致性 |
| 数据分析 | 0.5-0.7 | 平衡创造性和准确性 |
| 创意写作 | 0.7-1.0 | 需要更多创造性 |
| 头脑风暴 | 1.0-1.5 | 鼓励多样性 |

### 5. 版本管理

建议使用语义化版本号：
- `1.0.0` - 初始版本
- `1.1.0` - 新增功能
- `1.0.1` - Bug 修复
- `2.0.0` - 重大更新

## 插件测试

创建插件后，建议进行以下测试：

1. **功能测试**：创建会话，测试插件是否能正常工作
2. **响应质量**：检查回复是否符合预期
3. **参数调优**：根据需要调整 temperature 和 max_tokens
4. **边界情况**：测试插件在特殊情况下的表现

## 故障排除

### 插件未加载

- 检查 JSON 格式是否正确
- 确认所有必填字段都已填写
- 查看 logs/app.log 了解详细错误

### 插件行为异常

- 检查 system_prompt 是否清晰明确
- 调整 temperature 参数
- 确认 capabilities 与实际功能匹配

### 角色标识符冲突

- role 字段必须唯一
- 使用更具描述性的名称
- 避免使用内置角色名称

## 高级功能

### 元数据

metadata 字段可以存储任意自定义信息：

```json
{
  "metadata": {
    "category": "development",
    "complexity": "advanced",
    "required_models": ["gpt-4", "claude-3"],
    "custom_settings": {
      "timeout": 30,
      "retry_count": 3
    }
  }
}
```

### 标签系统

使用标签组织和分类插件：

```json
{
  "tags": ["开发", "代码质量", "自动化"]
}
```

标签可用于：
- 插件搜索
- 分类显示
- 批量操作

## API 参考

### 获取插件列表

```bash
GET /api/plugins
```

### 创建插件

```bash
POST /api/plugins
Content-Type: application/json

{
  "name": "插件名称",
  "role": "role_identifier",
  ...
}
```

### 更新插件

```bash
PUT /api/plugins/{plugin_id}
```

### 删除插件

```bash
DELETE /api/plugins/{plugin_id}
```

### 导出插件

```bash
GET /api/plugins/{plugin_id}/export
```

### 导入插件

```bash
POST /api/plugins/import
```

## 常见问题

**Q: 插件和内置角色有什么区别？**

A: 内置角色（HR, PM, BA, Dev, QA, Architect）是系统预定义的，而插件是完全自定义的。插件提供了更大的灵活性。

**Q: 可以导出插件分享给其他人吗？**

A: 可以！使用导出功能获取 JSON 文件，其他人可以通过导入功能使用它。

**Q: 插件会影响系统性能吗？**

A: 插件本身很轻量，主要性能消耗在 LLM API 调用上。建议合理设置 max_tokens。

**Q: 如何调试插件？**

A: 查看 logs/app.log 文件，其中包含插件加载和执行的详细日志。

## 更多示例

更多示例插件请参考 `plugins/` 目录。

## 技术支持

如有问题或建议，请访问：
- GitHub Issues: https://github.com/aaaddduuu/SynergyAI/issues
- 文档: https://github.com/aaaddduuu/SynergyAI/blob/main/README.md
