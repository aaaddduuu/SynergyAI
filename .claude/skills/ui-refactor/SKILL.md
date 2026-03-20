---
name: "ui-refactor"
description: "UI重构标准化流程技能。用于页面/组件的视觉重构、主题适配、交互优化。当用户请求重构页面、优化UI、修复样式问题时调用。"
---

# UI 重构标准化流程技能

## 1. 重构目标定义

### 1.1 核心目标
- **视觉一致性提升**：确保所有页面遵循统一的设计语言
- **主题适配完善**：支持亮色/暗色主题无缝切换
- **交互体验优化**：提升用户操作的流畅性和反馈感
- **代码可维护性**：使用标准化样式方案，便于后续维护

### 1.2 重构触发条件
- 用户明确请求"重构"某页面/组件
- 发现样式不符合设计规范
- 主题切换时显示异常
- 交互反馈不明确或缺失

---

## 2. 设计规范引用

### 2.1 CSS变量体系

**必须使用的语义化变量：**

```css
/* 背景色 */
--bg-base          /* 页面基础背景 */
--bg-surface       /* 卡片/面板背景 */
--bg-elevated      /* 悬浮元素背景（header、modal） */
--bg-hover         /* 悬停状态背景 */
--bg-secondary     /* 次要背景区域 */
--bg-card          /* 卡片背景（等同于 --bg-surface） */
--bg-header        /* 头部背景 */
--bg-input         /* 输入框背景 */

/* 文字颜色 */
--text-primary     /* 主要文字 */
--text-secondary   /* 次要文字 */
--text-muted       /* 弱化文字（提示、说明） */
--text-placeholder /* 占位符文字 */

/* 边框 */
--border-primary   /* 主要边框 */
--border-secondary /* 次要边框 */

/* 强调色 */
--accent           /* 主强调色 */
--accent-bg        /* 强调色背景 */
--accent-shadow    /* 强调色阴影 */
```

### 2.2 设计令牌

**圆角规范：**
- 小元素（标签、徽章）：`6px - 8px`
- 按钮、输入框：`10px - 12px`
- 卡片、面板：`16px - 20px`
- 弹窗、模态框：`20px - 24px`

**阴影规范：**
- 轻微阴影：`0 2px 8px rgba(0,0,0,0.1)`
- 卡片阴影：`0 4px 16px rgba(0,0,0,0.1)`
- 弹窗阴影：`0 20px 40px rgba(0,0,0,0.15)`
- 强调阴影：`0 4px 14px rgba(99, 102, 241, 0.3)`

**过渡动画：**
- 快速：`transition: all 0.15s ease`
- 标准：`transition: all 0.2s ease`
- 强调：`transition: all 0.3s ease`

### 2.3 颜色渐变规范

**常用渐变组合：**
```css
/* 紫色系（主要操作、AI相关） */
linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)

/* 蓝色系（信息、链接） */
linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%)

/* 绿色系（成功、确认） */
linear-gradient(135deg, #10b981 0%, #059669 100%)

/* 粉色系（创意、图像） */
linear-gradient(135deg, #ec4899 0%, #f43f5e 100%)

/* 橙色系（警告、重要） */
linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)
```

---

## 3. 重构范围界定

### 3.1 页面级别重构
- 整体布局结构
- Header区域
- 内容区域
- 侧边栏/辅助面板

### 3.2 组件级别重构
- 按钮（主要、次要、危险等）
- 输入框（文本、选择、日期等）
- 卡片（列表项、信息卡等）
- 弹窗（确认框、表单弹窗等）
- 导航（菜单、标签页、面包屑等）

### 3.3 功能模块重构
- 表单系统
- 数据表格
- 图表展示
- 文件上传
- 拖拽交互

---

## 4. 技术栈要求

### 4.1 样式方案
- **优先级1**：CSS变量 + 纯内联样式
- **优先级2**：CSS变量 + CSS Modules
- **禁止**：硬编码颜色值（如 `#ffffff`, `rgba(255,255,255,0.5)`）
- **禁止**：Tailwind CSS（本项目不使用）

### 4.2 React规范
```tsx
// 正确：使用CSS变量
<div style={{
  background: 'var(--bg-surface)',
  color: 'var(--text-primary)',
  border: '1px solid var(--border-primary)'
}}>

// 错误：硬编码颜色
<div style={{
  background: '#1e293b',
  color: 'white',
  border: '1px solid rgba(255,255,255,0.1)'
}}>
```

### 4.3 交互状态管理
```tsx
// 使用useState管理悬停状态
const [isHovered, setIsHovered] = useState(false);

<div
  style={{
    background: isHovered ? 'var(--bg-hover)' : 'var(--bg-surface)',
    transform: isHovered ? 'translateY(-2px)' : 'translateY(0)',
    transition: 'all 0.2s ease'
  }}
  onMouseEnter={() => setIsHovered(true)}
  onMouseLeave={() => setIsHovered(false)}
>
```

### 4.4 禁止事项
- ❌ 在 `map` 循环中使用 `useState`
- ❌ 直接修改DOM样式（使用React状态管理）
- ❌ 使用 `!important` 覆盖样式
- ❌ 内联复杂的动画逻辑

---

## 5. 质量验收标准

### 5.1 视觉验收
- [ ] 亮色模式下所有元素清晰可见
- [ ] 暗色模式下所有元素清晰可见
- [ ] 主题切换无闪烁、无延迟
- [ ] 颜色对比度符合WCAG 2.1 AA标准

### 5.2 交互验收
- [ ] 悬停状态有明显视觉反馈
- [ ] 点击状态有明显视觉反馈
- [ ] 禁用状态清晰可辨
- [ ] 焦点状态可见（键盘导航）

### 5.3 性能验收
- [ ] 无不必要的重渲染
- [ ] 动画帧率 ≥ 60fps
- [ ] 首屏渲染无阻塞

### 5.4 代码验收
- [ ] 无TypeScript类型错误
- [ ] 无console警告/错误
- [ ] 无硬编码颜色值
- [ ] 无废弃的组件引用

---

## 6. 实施步骤

### 步骤1：分析评估
```
1. 读取目标文件，理解当前结构
2. 识别硬编码颜色值
3. 识别旧组件依赖（Card、Button等）
4. 评估交互状态管理方式
5. 检查主题适配问题
```

### 步骤2：方案设计
```
1. 确定页面主题色（参考功能类型）
2. 规划组件层级结构
3. 设计交互状态变化
4. 确定需要提取的公共样式
```

### 步骤3：代码实现
```
1. 替换硬编码颜色为CSS变量
2. 移除旧组件依赖
3. 实现纯内联样式
4. 添加悬停/点击交互状态
5. 确保主题切换兼容
```

### 步骤4：测试验证
```
1. 运行 TypeScript 类型检查
2. 在亮色模式下验证
3. 在暗色模式下验证
4. 测试交互反馈
5. 检查响应式布局
```

---

## 7. 重构模板

### 7.1 页面基础结构模板
```tsx
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

export default function PageTemplate() {
  const [backHover, setBackHover] = useState(false);

  return (
    <div style={{
      minHeight: '100vh',
      background: 'var(--bg-base)',
      display: 'flex',
      flexDirection: 'column',
    }}>
      {/* Header */}
      <header style={{
        height: '72px',
        borderBottom: '1px solid var(--border-primary)',
        background: 'var(--bg-elevated)',
        backdropFilter: 'blur(20px)',
        padding: '0 32px',
        display: 'flex',
        alignItems: 'center',
      }}>
        <Link to="/back" style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: '40px',
          height: '40px',
          borderRadius: '10px',
          textDecoration: 'none',
          color: backHover ? '#fff' : 'var(--text-muted)',
          background: backHover ? 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)' : 'var(--bg-hover)',
          border: '1px solid var(--border-primary)',
          transition: 'all 0.2s ease',
        }}
        onMouseEnter={() => setBackHover(true)}
        onMouseLeave={() => setBackHover(false)}
        >
          <ArrowLeft style={{ width: '18px', height: '18px' }} />
        </Link>
        <h1 style={{
          fontSize: '22px',
          fontWeight: '700',
          color: 'var(--text-primary)',
          margin: '0 0 0 20px',
        }}>页面标题</h1>
      </header>

      {/* Content */}
      <div style={{
        flex: 1,
        padding: '28px 32px',
        overflow: 'auto',
      }}>
        {/* 内容区域 */}
      </div>
    </div>
  );
}
```

### 7.2 卡片组件模板
```tsx
function Card({ title, children }) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div style={{
      background: 'var(--bg-surface)',
      border: '1px solid var(--border-primary)',
      borderRadius: '20px',
      padding: '28px',
      transition: 'all 0.2s ease',
      transform: isHovered ? 'translateY(-2px)' : 'translateY(0)',
      boxShadow: isHovered ? '0 8px 24px rgba(0,0,0,0.1)' : 'none',
    }}
    onMouseEnter={() => setIsHovered(true)}
    onMouseLeave={() => setIsHovered(false)}
    >
      {title && (
        <h2 style={{
          fontSize: '17px',
          fontWeight: '600',
          color: 'var(--text-primary)',
          margin: '0 0 16px 0',
        }}>{title}</h2>
      )}
      {children}
    </div>
  );
}
```

### 7.3 按钮组件模板
```tsx
function Button({ variant = 'primary', children, onClick }) {
  const [isHovered, setIsHovered] = useState(false);

  const styles = {
    primary: {
      background: isHovered 
        ? 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)'
        : 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
      color: '#fff',
      border: 'none',
      boxShadow: isHovered ? '0 8px 24px rgba(99, 102, 241, 0.4)' : '0 4px 14px rgba(99, 102, 241, 0.3)',
    },
    secondary: {
      background: isHovered ? 'var(--bg-hover)' : 'var(--bg-surface)',
      color: 'var(--text-primary)',
      border: '1px solid var(--border-primary)',
      boxShadow: 'none',
    },
    danger: {
      background: isHovered 
        ? 'linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)'
        : 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
      color: '#fff',
      border: 'none',
      boxShadow: isHovered ? '0 8px 24px rgba(239, 68, 68, 0.4)' : '0 4px 14px rgba(239, 68, 68, 0.3)',
    },
  };

  return (
    <button
      onClick={onClick}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '8px',
        padding: '10px 18px',
        borderRadius: '10px',
        fontSize: '14px',
        fontWeight: '500',
        cursor: 'pointer',
        transition: 'all 0.2s ease',
        transform: isHovered ? 'translateY(-1px)' : 'translateY(0)',
        ...styles[variant],
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {children}
    </button>
  );
}
```

---

## 8. 常见问题处理

### 8.1 主题切换不生效
**原因**：使用了硬编码颜色值
**解决**：替换为对应的CSS变量

### 8.2 悬停状态闪烁
**原因**：在map循环中使用useState
**解决**：将悬停状态提升到父组件，使用id或索引管理

### 8.3 边框在暗色模式不可见
**原因**：使用了 `rgba(255,255,255,0.1)` 等硬编码值
**解决**：使用 `var(--border-primary)`

### 8.4 文字在暗色模式不可见
**原因**：使用了硬编码的深色文字
**解决**：使用 `var(--text-primary)` 或 `var(--text-secondary)`

---

## 9. 执行检查清单

重构完成后，按以下清单逐项检查：

```
□ 所有颜色值已替换为CSS变量
□ 移除了旧组件依赖（Card、Button等）
□ 实现了悬停交互状态
□ 亮色模式验证通过
□ 暗色模式验证通过
□ TypeScript无类型错误
□ 无console警告/错误
□ 动画过渡流畅
□ 响应式布局正常
```
