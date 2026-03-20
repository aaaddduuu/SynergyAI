git只能提交和commit，不允许回退。

# UI 设计规范

所有前端 UI 开发必须遵循 `.claude/rules/ui_design_rules.md` 中的规范。
所有文件不得超过两百行。
不允许有hardcode。
需要严格按照solid原则的ui设计规范进行开发。
所以代码必须统一风格，比如前后端都用snake_case。

# CSRF 安全规则

任何涉及认证、CORS、CSRF 中间件的修改必须遵循 `.claude/rules/csrf_security_rules.md` 中的规范。
修改后必须测试登录流程，确保 CSRF token 正常工作。

**关键检查点：**
- CORS 配置必须包含 `exposedHeaders: ['X-CSRF-Token']`
- CSRF 中间件必须使用白名单机制，不处理健康检查等路径
- 前端 `getCsrfToken()` 必须防止并发请求