# 安全功能文档

本文档描述了 SynergyAI 系统中实现的安全增强功能。

## 目录

1. [CORS 策略](#cors-策略)
2. [CSRF 保护](#csrf-保护)
3. [输入验证](#输入验证)
4. [Rate Limiting](#rate-limiting)
5. [安全日志](#安全日志)
6. [安全测试](#安全测试)

## CORS 策略

### 配置

CORS（跨域资源共享）策略现在通过环境变量配置，而不是硬编码允许所有来源。

**环境变量：**
```bash
CORS_ORIGINS=http://localhost:8000,http://localhost:3000
```

**实现位置：**
- 配置文件：`core/config.py`
- 应用配置：`main.py` (第 371-382 行)

**特性：**
- 支持配置化的允许域名列表
- 暴露安全相关的响应头（X-CSRF-Token, X-RateLimit-*）
- 支持凭证传递

## CSRF 保护

### 实现原理

CSRF（跨站请求伪造）保护通过以下机制实现：

1. **Token 生成**：基于 session_id、时间戳和 secret_key 生成 SHA-256 哈希
2. **Token 验证**：对状态改变请求（POST/PUT/DELETE/PATCH）验证 token
3. **Token 过期**：Token 默认有效期为 1 小时

### API 端点

**获取 CSRF Token：**
```bash
GET /api/auth/csrf-token
```

响应：
```json
{
  "csrf_token": "abc123...",
  "session_id": "xyz789..."
}
```

### 前端使用

```javascript
// 1. 获取 CSRF token
const response = await fetch('/api/auth/csrf-token');
const { csrf_token } = await response.json();

// 2. 在状态改变请求中使用
fetch('/api/tasks', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': csrf_token
  },
  body: JSON.stringify({...})
});
```

### 白名单路径

以下路径不需要 CSRF 验证：
- `/api/health`
- `/api/performance`
- `/api/features`
- `/login`
- `/api/auth/login`
- `/api/auth/register`

**实现位置：** `core/security.py` (SecurityMiddleware 类)

## 输入验证

### 验证类型

系统实现了多层输入验证：

#### 1. SQL 注入检测

检测模式：
- UNION SELECT 攻击
- INSERT/DELETE/DROP 攻击
- 命令执行攻击
- 注释符注入

#### 2. XSS 攻击检测

检测模式：
- `<script>` 标签
- `javascript:` 协议
- 事件处理器注入
- `<iframe>`, `<embed>`, `<object>` 标签

#### 3. 路径遍历检测

检测模式：
- `../`
- `..\\`
- URL 编码的路径遍历

#### 4. 命令注入检测

检测模式：
- 命令分隔符（`;`, `&`, `|`, `` ` ``）
- 命令替换（`$()``, `` `${}``）

### Pydantic 模型验证

所有请求模型都包含 Pydantic 验证器：

**位置：** `core/schemas.py`

示例：
```python
class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    password: str = Field(..., min_length=6, max_length=100)

    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$', v):
            raise ValueError('用户名只能包含字母、数字、下划线和中文')
        return v
```

**实现位置：** `core/security.py` (SecurityValidator 类)

## Rate Limiting

### 配置

**环境变量：**
```bash
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

### 限制策略

系统对不同类型的端点应用不同的限制：

| 类别 | 每分钟限制 | 每小时限制 | 适用路径 |
|------|-----------|-----------|---------|
| 默认 | 60 | 1000 | 所有其他请求 |
| 认证 | 5 | 20 | `/api/auth/*` |
| API | 30 | 500 | `/api/*` |

### 响应头

每个响应都包含 rate limit 信息：

```
X-RateLimit-Limit-Minute: 60
X-RateLimit-Remaining-Minute: 59
X-RateLimit-Limit-Hour: 1000
X-RateLimit-Remaining-Hour: 999
```

### 超限处理

当超过限制时：
- HTTP 状态码：429 Too Many Requests
- 响应：`{"detail": "Rate limit exceeded: X requests per minute"}`

**实现位置：** `core/security.py` (RateLimiter 类)

## 安全日志

### 日志文件

所有安全事件记录到：`logs/security.log`

### 日志级别

| 级别 | 事件类型 | 示例 |
|------|---------|------|
| ERROR | 高危事件 | 认证失败、CSRF 失败 |
| WARNING | 中危事件 | Rate limit 超过、无效输入 |
| INFO | 低危事件 | CSRF token 生成 |

### 记录的事件

1. **认证失败**
   - 用户名/密码错误
   - Token 无效
   - 权限不足

2. **Rate Limit 超过**
   - 客户端 IP
   - 请求路径
   - 超过限制类型

3. **无效输入**
   - 字段名称
   - 输入长度
   - 检测到的攻击类型

4. **CSRF 失败**
   - Token 无效
   - Token 缺失
   - Session 不匹配

**实现位置：** `core/security.py` (SecurityLogger 类)

## 安全测试

### 运行测试

```bash
# 运行所有安全测试
python -m pytest tests/test_security.py -v

# 运行特定测试
python -m pytest tests/test_security.py::TestSecurity::test_sql_injection_detection -v
```

### 测试覆盖

1. **CORS 头测试** - 验证 CORS 响应头正确设置
2. **安全头测试** - 验证安全响应头（X-Frame-Options, X-XSS-Protection 等）
3. **Rate Limiting 测试** - 验证 rate limit 响应头
4. **CSRF Token 测试** - 验证 token 生成和格式
5. **SQL 注入测试** - 验证 SQL 注入检测
6. **XSS 测试** - 验证 XSS 攻击检测
7. **路径遍历测试** - 验证路径遍历检测
8. **命令注入测试** - 验证命令注入检测
9. **输入验证测试** - 验证 Pydantic 模型验证

**测试文件：** `tests/test_security.py`

## 最佳实践

### 生产环境配置

1. **设置强密钥**
```bash
# 生成随机密钥
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
```

2. **配置 CORS**
```bash
# 只允许特定域名
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

3. **启用所有安全功能**
```bash
RATE_LIMIT_ENABLED=true
CSRF_ENABLED=true
ENABLE_INPUT_VALIDATION=true
```

### 监控建议

1. 定期检查 `logs/security.log`
2. 监控 rate limit 超过事件
3. 追踪认证失败模式
4. 设置告警规则

### 更新和维护

1. 定期更新依赖包
2. 审查安全日志模式
3. 更新攻击检测模式
4. 进行安全审计

## 架构

```
core/
├── security.py          # 安全模块（CSRF、Rate Limiting、验证、日志）
├── config.py            # 配置管理
└── schemas.py           # Pydantic 验证模型

main.py                  # 应用主文件（集成安全中间件）

tests/
└── test_security.py     # 安全功能测试

logs/
└── security.log         # 安全日志文件
```

## 参考资源

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CORS 规格](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [CSRF 预防](https://owasp.org/www-community/attacks/csrf)
- [Rate Limiting 最佳实践](https://cloud.google.com/architecture/rate-limiting-strategies-techniques)
