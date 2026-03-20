<!DOCTYPE html>

<html lang="zh-CN"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<script id="tailwind-config">
        tailwind.config = {
            darkMode: "class",
            theme: {
                extend: {
                    colors: {
                        "primary": "#667aea",
                        "secondary": "#764ba2",
                        "background-light": "#f6f6f8",
                        "background-dark": "#111421",
                    },
                    fontFamily: {
                        "display": ["Inter", "system-ui", "sans-serif"]
                    },
                    borderRadius: { "DEFAULT": "0.25rem", "lg": "0.5rem", "xl": "0.75rem", "full": "9999px" },
                },
            },
        }
    </script>
<style>
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 10px; }
    </style>
</head>
<body class="bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100">
<div class="flex flex-col h-screen overflow-hidden">
<!-- Header -->
<header class="h-[60px] shrink-0 bg-gradient-to-r from-primary to-secondary px-6 flex items-center justify-between shadow-md z-10">
<div class="flex items-center gap-4">
<h1 class="text-white text-xl font-bold tracking-tight">🤖 AI 协作团队</h1>
<div class="h-6 w-[1px] bg-white/20 mx-2"></div>
<div class="flex items-center gap-3">
<span class="text-white/90 text-sm font-medium">对话轮数: 5</span>
<span class="bg-emerald-500/20 text-emerald-100 text-xs px-2 py-1 rounded-full border border-emerald-500/30 flex items-center gap-1">
<span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                        进行中
                    </span>
</div>
</div>
<div class="flex items-center gap-3">
<button class="flex items-center gap-2 px-4 py-1.5 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors text-sm font-medium border border-white/20">
<span class="material-symbols-outlined text-[18px]">settings</span>
                    配置
                </button>
<button class="flex items-center gap-2 px-4 py-1.5 bg-white text-primary hover:bg-white/90 rounded-lg transition-colors text-sm font-bold shadow-sm">
<span class="material-symbols-outlined text-[18px]">add</span>
                    新建项目
                </button>
<div class="ml-2 w-8 h-8 rounded-full bg-white/20 border border-white/30 flex items-center justify-center text-white overflow-hidden">
<img alt="User Avatar" data-alt="Professional user profile placeholder" src="https://lh3.googleusercontent.com/aida-public/AB6AXuB5Tkxoo86NsLFQM-2v6at9_NzdDOMxZ-h4PXcUIz9gs2xj6BZvQS3IgDM7CnDaC1GtKeDtLgR5tTnjoKEaXschUKDtb7sTrhmAMxIvt50I5g-DzIVh1aYFoDcnUTeEjJTDEcrJMOCPwmGlYpfDOJMPiSck3h4uCMm2gY-64XR_Xnvt2L4T9YAoBzm6PxBmCcyqbSh7eb-num3vRJgAmzfPQCDt0IRJUM1GUdO7hil-puKhJuspcRRq5GrD4AOCmdzrls7Pe0jXe9g"/>
</div>
</div>
</header>
<!-- Main Layout -->
<main class="flex flex-1 overflow-hidden">
<!-- Left Sidebar (280px) -->
<aside class="w-[280px] bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col">
<div class="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-6">
<!-- Team Section -->
<section>
<div class="flex items-center justify-between mb-4">
<h2 class="text-sm font-bold text-slate-500 uppercase tracking-wider flex items-center gap-2">
<span class="material-symbols-outlined text-[18px]">group</span>
                                团队成员
                            </h2>
</div>
<div class="grid grid-cols-1 gap-1">
<div class="flex items-center gap-3 p-2 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg cursor-pointer transition-colors">
<div class="w-8 h-8 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center font-bold text-xs border border-rose-200">HR</div>
<span class="text-sm font-medium">招聘专家</span>
</div>
<div class="flex items-center gap-3 p-2 bg-primary/10 rounded-lg cursor-pointer">
<div class="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold text-xs border border-blue-200">PM</div>
<span class="text-sm font-bold text-primary">产品经理</span>
<span class="ml-auto w-2 h-2 rounded-full bg-primary"></span>
</div>
<div class="flex items-center gap-3 p-2 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg cursor-pointer">
<div class="w-8 h-8 rounded-full bg-amber-100 text-amber-600 flex items-center justify-center font-bold text-xs border border-amber-200">BA</div>
<span class="text-sm font-medium">商业分析</span>
</div>
<div class="flex items-center gap-3 p-2 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg cursor-pointer">
<div class="w-8 h-8 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center font-bold text-xs border border-indigo-200">Dev</div>
<span class="text-sm font-medium">核心开发</span>
</div>
<div class="flex items-center gap-3 p-2 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg cursor-pointer">
<div class="w-8 h-8 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center font-bold text-xs border border-emerald-200">QA</div>
<span class="text-sm font-medium">质量保证</span>
</div>
<div class="flex items-center gap-3 p-2 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg cursor-pointer">
<div class="w-8 h-8 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center font-bold text-xs border border-purple-200">Arc</div>
<span class="text-sm font-medium">系统架构</span>
</div>
</div>
</section>
<!-- Task List -->
<section>
<h2 class="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4 flex items-center gap-2">
<span class="material-symbols-outlined text-[18px]">assignment</span>
                            任务列表
                        </h2>
<div class="space-y-2">
<div class="bg-slate-50 dark:bg-slate-800/50 p-3 rounded-lg border-l-4 border-slate-300">
<div class="text-xs font-bold text-slate-400 mb-1">待处理</div>
<p class="text-sm font-medium leading-tight">用户权限模块设计</p>
</div>
<div class="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg border-l-4 border-primary shadow-sm">
<div class="text-xs font-bold text-primary mb-1">进行中</div>
<p class="text-sm font-medium leading-tight">核心架构PRD编写</p>
</div>
<div class="bg-amber-50 dark:bg-amber-900/20 p-3 rounded-lg border-l-4 border-amber-400">
<div class="text-xs font-bold text-amber-600 mb-1">审核中</div>
<p class="text-sm font-medium leading-tight">API 文档评审</p>
</div>
<div class="bg-emerald-50 dark:bg-emerald-900/20 p-3 rounded-lg border-l-4 border-emerald-400 opacity-75">
<div class="text-xs font-bold text-emerald-600 mb-1">已完成</div>
<p class="text-sm font-medium leading-tight line-through">项目启动会议</p>
</div>
</div>
<button class="w-full mt-4 flex items-center justify-center gap-2 p-2 border-2 border-dashed border-slate-200 dark:border-slate-700 rounded-xl text-slate-400 hover:text-primary hover:border-primary transition-all text-sm font-medium">
<span class="material-symbols-outlined text-[18px]">add</span>
                            添加任务
                        </button>
</section>
</div>
</aside>
<!-- Center Chat Area -->
<section class="flex-1 flex flex-col bg-slate-50 dark:bg-slate-950">
<!-- Messages container -->
<div class="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-6">
<!-- AI Message -->
<div class="flex items-start gap-4 max-w-[85%]">
<div class="w-10 h-10 rounded-full bg-blue-100 flex-shrink-0 flex items-center justify-center border border-blue-200 shadow-sm">
<span class="material-symbols-outlined text-blue-600">smart_toy</span>
</div>
<div class="flex flex-col gap-1">
<span class="text-xs font-bold text-slate-400 ml-1">PM助理</span>
<div class="bg-white dark:bg-slate-800 p-4 rounded-2xl rounded-tl-none shadow-sm border border-slate-200 dark:border-slate-700">
<p class="text-sm leading-relaxed">你好！根据当前的架构设计，我建议我们先完成核心数据模型。我已经将初步的Schema发给Dev成员审核了。你需要我协助起草API文档吗？</p>
</div>
</div>
</div>
<!-- System Message -->
<div class="flex justify-center my-4">
<div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800/50 px-6 py-2 rounded-full flex items-center gap-2">
<span class="material-symbols-outlined text-amber-500 text-[18px]">warning</span>
<span class="text-xs text-amber-700 dark:text-amber-400 font-medium">注意：架构师正在重构核心组件，请暂缓合并代码</span>
</div>
</div>
<!-- User Message -->
<div class="flex flex-row-reverse items-start gap-4 max-w-[85%] ml-auto">
<div class="w-10 h-10 rounded-full bg-primary/20 flex-shrink-0 flex items-center justify-center border border-primary/30 shadow-sm overflow-hidden">
<img alt="User" data-alt="User profile avatar circle" src="https://lh3.googleusercontent.com/aida-public/AB6AXuBceRYjRvh71YvJhs1YXtA_pgAA46cFwUAxnd7v496urRW5yKvldEc5s_X2cDEUVIbPqcbccKbVOfb8zYlnwVCfnnfcdtA40tuQ6zMnAPoUVlWfasw5S55thPNz4vtygotQcJhE6-ue8W_ugoSs3ApE1z5mtpvQEWQZAk0qfzrCvi9fwhyKapokHtDK7NZxaWoAn-0v3dLol62qWobAc_CaqYy6x9Itkwm4FAAlHgQndRgnT0SWD-rgjUlLzIkMQqRUNxvdFvA4Dfw"/>
</div>
<div class="flex flex-col items-end gap-1">
<span class="text-xs font-bold text-slate-400 mr-1">我</span>
<div class="bg-gradient-to-br from-primary to-secondary p-4 rounded-2xl rounded-tr-none shadow-md">
<p class="text-sm text-white leading-relaxed font-medium">好的，没问题。请先生成一个Swagger规格草案，然后交给QA进行测试用例编写。同时请关注架构师的重构进度。</p>
</div>
</div>
</div>
<!-- AI Message (BA) -->
<div class="flex items-start gap-4 max-w-[85%]">
<div class="w-10 h-10 rounded-full bg-amber-100 flex-shrink-0 flex items-center justify-center border border-amber-200 shadow-sm">
<span class="material-symbols-outlined text-amber-600">analytics</span>
</div>
<div class="flex flex-col gap-1">
<span class="text-xs font-bold text-slate-400 ml-1">BA专家</span>
<div class="bg-white dark:bg-slate-800 p-4 rounded-2xl rounded-tl-none shadow-sm border border-slate-200 dark:border-slate-700">
<p class="text-sm leading-relaxed">我已经分析了竞品的数据流动方案。如果采用混合加密方案，在满足性能要求的同时，安全性可以提升30%。正在更新需求规格说明书。</p>
</div>
</div>
</div>
</div>
<!-- Bottom Input Area -->
<div class="h-[80px] bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 px-6 flex items-center gap-4">
<button class="text-slate-400 hover:text-primary transition-colors">
<span class="material-symbols-outlined">attach_file</span>
</button>
<div class="flex-1 relative">
<input class="w-full h-11 bg-slate-100 dark:bg-slate-800 border-none rounded-xl px-4 text-sm focus:ring-2 focus:ring-primary/50 transition-all" placeholder="输入消息，与团队进行协作..." type="text"/>
<div class="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2">
<span class="material-symbols-outlined text-slate-400 text-[20px] cursor-pointer hover:text-primary">mood</span>
<span class="material-symbols-outlined text-slate-400 text-[20px] cursor-pointer hover:text-primary">mic</span>
</div>
</div>
<button class="bg-primary hover:bg-primary/90 text-white px-6 h-11 rounded-xl font-bold text-sm shadow-md transition-all flex items-center gap-2 active:scale-95">
<span class="material-symbols-outlined text-[20px]">send</span>
                        发送
                    </button>
</div>
</section>
<!-- Right Sidebar (Action Items / Stats) - Placeholder for 3rd Column -->
<aside class="w-[300px] bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-slate-800 hidden xl:flex flex-col p-6 overflow-y-auto custom-scrollbar">
<h2 class="text-sm font-bold text-slate-500 uppercase tracking-wider mb-6 flex items-center gap-2">
<span class="material-symbols-outlined text-[18px]">insights</span>
                    项目洞察
                </h2>
<div class="space-y-6">
<div class="bg-slate-50 dark:bg-slate-800/50 rounded-xl p-4 border border-slate-100 dark:border-slate-800">
<p class="text-xs text-slate-400 font-bold mb-2">开发进度</p>
<div class="w-full bg-slate-200 dark:bg-slate-700 h-2 rounded-full overflow-hidden">
<div class="bg-primary h-full w-[65%] rounded-full"></div>
</div>
<div class="flex justify-between mt-2">
<span class="text-[10px] font-bold text-primary">65% 完成</span>
<span class="text-[10px] text-slate-400">预计 3 天后交付</span>
</div>
</div>
<div class="space-y-3">
<p class="text-xs text-slate-400 font-bold">最近活动</p>
<div class="flex gap-3 relative">
<div class="w-2 h-2 rounded-full bg-primary mt-1.5 shrink-0 z-10"></div>
<div class="absolute left-[3px] top-4 w-[1px] h-full bg-slate-200 dark:bg-slate-700"></div>
<div>
<p class="text-xs font-bold">Dev 提交了核心 API 代码</p>
<p class="text-[10px] text-slate-400">10 分钟前</p>
</div>
</div>
<div class="flex gap-3 relative">
<div class="w-2 h-2 rounded-full bg-amber-400 mt-1.5 shrink-0 z-10"></div>
<div class="absolute left-[3px] top-4 w-[1px] h-full bg-slate-200 dark:bg-slate-700"></div>
<div>
<p class="text-xs font-bold">QA 开始编写自动化脚本</p>
<p class="text-[10px] text-slate-400">45 分钟前</p>
</div>
</div>
<div class="flex gap-3 relative">
<div class="w-2 h-2 rounded-full bg-emerald-400 mt-1.5 shrink-0 z-10"></div>
<div>
<p class="text-xs font-bold">项目需求文档通过初审</p>
<p class="text-[10px] text-slate-400">2 小时前</p>
</div>
</div>
</div>
<div class="p-4 bg-primary/5 rounded-xl border border-primary/10">
<p class="text-xs font-bold text-primary mb-2 flex items-center gap-1">
<span class="material-symbols-outlined text-[14px]">auto_awesome</span>
                            AI 建议
                        </p>
<p class="text-[11px] leading-relaxed text-slate-600 dark:text-slate-400">
                            当前开发环节与测试环节存在 4 小时的滞后，建议提前分配 QA 资源进入 API 开发阶段。
                        </p>
</div>
</div>
</aside>
</main>
</div>
</body></html>



<!DOCTYPE html>

<html lang="zh-CN"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<script id="tailwind-config">
        tailwind.config = {
            darkMode: "class",
            theme: {
                extend: {
                    colors: {
                        "primary": "#667aea",
                        "background-light": "#f6f6f8",
                        "background-dark": "#111421",
                    },
                    fontFamily: {
                        "display": ["Inter"]
                    },
                    borderRadius: {
                        "DEFAULT": "0.25rem",
                        "lg": "0.5rem",
                        "xl": "0.75rem",
                        "full": "9999px"
                    },
                },
            },
        }
    </script>
<title>AI Collaborative Team - LLM Configuration</title>
</head>
<body class="font-display bg-background-light dark:bg-background-dark text-slate-900 dark:text-slate-100 min-h-screen">
<div class="relative flex min-h-screen w-full flex-col overflow-x-hidden">
<div class="layout-container flex h-full grow flex-col">
<header class="flex items-center justify-between border-b border-primary/10 bg-white/80 dark:bg-background-dark/80 backdrop-blur-md px-6 md:px-10 py-4 sticky top-0 z-10">
<div class="flex items-center gap-4">
<div class="size-8 text-primary">
<svg fill="currentColor" viewbox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
<path clip-rule="evenodd" d="M24 4H42V17.3333V30.6667H24V44H6V30.6667V17.3333H24V4Z" fill-rule="evenodd"></path>
</svg>
</div>
<h2 class="text-xl font-bold tracking-tight">AI Collaborative Team</h2>
</div>
<div class="flex items-center gap-3">
<button class="flex items-center justify-center rounded-lg h-10 w-10 bg-primary/10 text-primary hover:bg-primary/20 transition-colors">
<span class="material-symbols-outlined">notifications</span>
</button>
<button class="flex items-center justify-center rounded-lg h-10 w-10 bg-primary/10 text-primary hover:bg-primary/20 transition-colors">
<span class="material-symbols-outlined">account_circle</span>
</button>
</div>
</header>
<main class="flex-1 p-6 md:p-10 max-w-7xl mx-auto w-full">
<div class="flex flex-col gap-6">
<div class="flex flex-wrap justify-between items-end gap-4">
<h1 class="text-3xl font-extrabold tracking-tight">Dashboard</h1>
<nav class="flex gap-2">
<span class="text-slate-500">Settings</span>
<span class="text-slate-400">/</span>
<span class="text-primary font-medium">LLM Config</span>
</nav>
</div>
<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
<div class="bg-white dark:bg-slate-800/50 p-6 rounded-xl border border-primary/5 shadow-sm">
<div class="text-primary mb-2"><span class="material-symbols-outlined">memory</span></div>
<div class="text-sm text-slate-500">Active Model</div>
<div class="text-xl font-bold">GPT-4 Turbo</div>
</div>
<div class="bg-white dark:bg-slate-800/50 p-6 rounded-xl border border-primary/5 shadow-sm">
<div class="text-primary mb-2"><span class="material-symbols-outlined">api</span></div>
<div class="text-sm text-slate-500">API Status</div>
<div class="text-xl font-bold text-green-500 flex items-center gap-2">
<span class="size-2 rounded-full bg-green-500"></span>
                                Connected
                            </div>
</div>
<div class="bg-white dark:bg-slate-800/50 p-6 rounded-xl border border-primary/5 shadow-sm">
<div class="text-primary mb-2"><span class="material-symbols-outlined">bolt</span></div>
<div class="text-sm text-slate-500">Usage Today</div>
<div class="text-xl font-bold">1,240 tokens</div>
</div>
</div>
</div>
</main>
</div>
<div class="fixed inset-0 z-50 flex items-center justify-center p-4">
<div class="absolute inset-0 bg-slate-900/60 backdrop-blur-sm"></div>
<div class="relative w-full max-w-md bg-white dark:bg-slate-900 rounded-xl shadow-2xl border border-primary/20 overflow-hidden">
<div class="p-6 border-b border-primary/10">
<div class="flex items-center justify-between">
<h3 class="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
<span class="material-symbols-outlined text-primary">settings_input_component</span>
                            LLM 配置
                        </h3>
<button class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
<span class="material-symbols-outlined">close</span>
</button>
</div>
</div>
<div class="p-6 space-y-5">
<div class="space-y-2">
<label class="text-sm font-semibold text-slate-700 dark:text-slate-300">模型选择</label>
<div class="relative">
<select class="w-full h-12 pl-4 pr-10 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white appearance-none focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all">
<option value="gpt-4">GPT-4 Turbo (OpenAI)</option>
<option value="gpt-3.5">GPT-3.5 Turbo (OpenAI)</option>
<option value="claude-3">Claude 3 Opus (Anthropic)</option>
<option value="llama-3">Llama 3 (Meta)</option>
</select>
<span class="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none">expand_more</span>
</div>
</div>
<div class="space-y-2">
<label class="text-sm font-semibold text-slate-700 dark:text-slate-300">API Key</label>
<div class="relative">
<input class="w-full h-12 pl-11 pr-4 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all" placeholder="sk-••••••••••••••••" type="password"/>
<span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">vpn_key</span>
</div>
<p class="text-[10px] text-slate-400 italic mt-1">您的 API Key 将被安全地加密存储。</p>
</div>
<div class="space-y-2">
<label class="text-sm font-semibold text-slate-700 dark:text-slate-300">Base URL</label>
<div class="relative">
<input class="w-full h-12 pl-11 pr-4 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all" placeholder="https://api.openai.com/v1" type="text"/>
<span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">link</span>
</div>
</div>
</div>
<div class="p-6 bg-slate-50 dark:bg-slate-800/50 flex gap-3 justify-end">
<button class="px-6 py-2.5 rounded-lg border border-slate-300 dark:border-slate-600 text-slate-600 dark:text-slate-300 font-medium hover:bg-slate-100 dark:hover:bg-slate-700 transition-all text-sm">
                        取消
                    </button>
<button class="px-8 py-2.5 rounded-lg bg-gradient-to-r from-primary to-[#8a99f0] text-white font-bold shadow-lg shadow-primary/25 hover:shadow-primary/40 hover:-translate-y-0.5 transition-all text-sm">
                        保存配置
                    </button>
</div>
</div>
</div>
</div>
</body></html>


<!DOCTYPE html>

<html lang="zh-CN"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<script id="tailwind-config">
        tailwind.config = {
            darkMode: "class",
            theme: {
                extend: {
                    colors: {
                        "primary": "#667aea",
                        "background-light": "#f6f6f8",
                        "background-dark": "#111421",
                    },
                    fontFamily: {
                        "display": ["Inter", "sans-serif"]
                    },
                    borderRadius: {"DEFAULT": "0.25rem", "lg": "0.5rem", "xl": "0.75rem", "full": "9999px"},
                },
            },
        }
    </script>
<title>AI Collaborative Team - Add Task</title>
</head>
<body class="bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100">
<div class="relative flex min-h-screen w-full flex-col overflow-x-hidden">
<!-- Main Dashboard Content (Blurred Background) -->
<div class="layout-container flex h-full grow flex-col blur-sm grayscale-[0.2]">
<header class="flex items-center justify-between whitespace-nowrap border-b border-slate-200 dark:border-slate-800 px-10 py-3 bg-white dark:bg-slate-900">
<div class="flex items-center gap-4">
<div class="size-8 bg-primary text-white flex items-center justify-center rounded-lg">
<span class="material-symbols-outlined">hub</span>
</div>
<h2 class="text-slate-900 dark:text-slate-100 text-lg font-bold leading-tight tracking-tight">AI Collaborative Team</h2>
</div>
<div class="flex flex-1 justify-end gap-4">
<div class="hidden md:flex items-center bg-slate-100 dark:bg-slate-800 rounded-lg px-3 py-2 w-64">
<span class="material-symbols-outlined text-slate-500 text-sm">search</span>
<input class="bg-transparent border-none focus:ring-0 text-sm w-full" placeholder="搜索任务..." type="text"/>
</div>
<div class="flex gap-2">
<button class="p-2 bg-slate-100 dark:bg-slate-800 rounded-lg hover:bg-slate-200 transition-colors">
<span class="material-symbols-outlined text-slate-700 dark:text-slate-300">notifications</span>
</button>
<button class="p-2 bg-slate-100 dark:bg-slate-800 rounded-lg hover:bg-slate-200 transition-colors">
<span class="material-symbols-outlined text-slate-700 dark:text-slate-300">settings</span>
</button>
</div>
<div class="size-10 rounded-full bg-primary/20 border-2 border-primary/30 overflow-hidden" data-alt="User profile avatar placeholder">
<img alt="Avatar" class="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuD-17IvxquaaXH8kzzPxbLkz2Yr-lx95P9Dck_OWe5QtSF7v7tr0lskhmC3m_ElBqeHbPmGxL-pgbF2aYGGRwoUIpzpe8M-q50QBA6lgfhiskH3S1j1SyoNPuilZJ5u12KZsluyhbB8V4EhDX3dTaiMH151WutgUAcf-NOqRhIFXS2vks6wIfOIiJAKno-WONoi2etgWz1VnnsxZltNv3ILZ_AL9biTV2NKpG7iU-f2djjQgfvL-TAb_reryg8TogcGnIApEuYGZeU"/>
</div>
</div>
</header>
<main class="p-10 max-w-7xl mx-auto w-full">
<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
<div class="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
<h3 class="text-slate-500 dark:text-slate-400 text-sm font-medium mb-1">待处理</h3>
<p class="text-3xl font-bold">12</p>
</div>
<div class="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
<h3 class="text-slate-500 dark:text-slate-400 text-sm font-medium mb-1">进行中</h3>
<p class="text-3xl font-bold">5</p>
</div>
<div class="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800">
<h3 class="text-slate-500 dark:text-slate-400 text-sm font-medium mb-1">已完成</h3>
<p class="text-3xl font-bold text-primary">28</p>
</div>
</div>
</main>
</div>
<!-- Modal Backdrop -->
<div class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4">
<!-- Modal Container -->
<div class="bg-white dark:bg-slate-900 w-full max-w-[560px] rounded-xl shadow-2xl overflow-hidden border border-slate-200 dark:border-slate-800">
<!-- Modal Header -->
<div class="px-8 py-6 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
<div>
<h2 class="text-2xl font-bold text-slate-900 dark:text-slate-100">添加新任务</h2>
<p class="text-slate-500 dark:text-slate-400 text-sm mt-1">为团队协作创建新的任务条目</p>
</div>
<button class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors">
<span class="material-symbols-outlined">close</span>
</button>
</div>
<!-- Modal Body (Form) -->
<div class="p-8 space-y-6">
<!-- Task Title -->
<div class="flex flex-col gap-2">
<label class="text-sm font-semibold text-slate-700 dark:text-slate-300">任务标题</label>
<input class="w-full px-4 py-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all placeholder:text-slate-400" placeholder="请输入任务名称" type="text"/>
</div>
<!-- Task Description -->
<div class="flex flex-col gap-2">
<label class="text-sm font-semibold text-slate-700 dark:text-slate-300">任务描述</label>
<textarea class="w-full px-4 py-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all placeholder:text-slate-400 resize-none" placeholder="详细说明任务要求..." rows="4"></textarea>
</div>
<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
<!-- Assignee -->
<div class="flex flex-col gap-2">
<label class="text-sm font-semibold text-slate-700 dark:text-slate-300">负责人</label>
<div class="relative">
<select class="w-full appearance-none px-4 py-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all pr-10">
<option disabled="" selected="" value="">选择团队角色</option>
<option value="frontend">前端开发 (AI)</option>
<option value="backend">后端开发 (AI)</option>
<option value="designer">UI 设计师</option>
<option value="pm">产品经理</option>
</select>
<span class="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400">expand_more</span>
</div>
</div>
<!-- Priority -->
<div class="flex flex-col gap-2">
<label class="text-sm font-semibold text-slate-700 dark:text-slate-300">优先级</label>
<div class="flex gap-2">
<label class="flex-1 cursor-pointer group">
<input class="peer hidden" name="priority" type="radio" value="low"/>
<div class="flex items-center justify-center py-2 px-3 border border-slate-200 dark:border-slate-700 rounded-lg text-sm bg-slate-50 dark:bg-slate-800 peer-checked:bg-primary/10 peer-checked:border-primary peer-checked:text-primary transition-all">
                                        低
                                    </div>
</label>
<label class="flex-1 cursor-pointer group">
<input checked="" class="peer hidden" name="priority" type="radio" value="medium"/>
<div class="flex items-center justify-center py-2 px-3 border border-slate-200 dark:border-slate-700 rounded-lg text-sm bg-slate-50 dark:bg-slate-800 peer-checked:bg-primary/10 peer-checked:border-primary peer-checked:text-primary transition-all">
                                        中
                                    </div>
</label>
<label class="flex-1 cursor-pointer group">
<input class="peer hidden" name="priority" type="radio" value="high"/>
<div class="flex items-center justify-center py-2 px-3 border border-slate-200 dark:border-slate-700 rounded-lg text-sm bg-slate-50 dark:bg-slate-800 peer-checked:bg-primary/10 peer-checked:border-primary peer-checked:text-primary transition-all">
                                        高
                                    </div>
</label>
</div>
</div>
</div>
</div>
<!-- Modal Footer -->
<div class="px-8 py-6 bg-slate-50 dark:bg-slate-800/50 flex justify-end gap-4">
<button class="px-6 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 font-semibold text-sm hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                        取消
                    </button>
<button class="px-6 py-2.5 rounded-lg bg-primary hover:bg-primary/90 text-white font-semibold text-sm shadow-lg shadow-primary/20 transition-all flex items-center gap-2">
<span class="material-symbols-outlined text-[20px]">add</span>
                        添加任务
                    </button>
</div>
</div>
</div>
</div>
</body></html>

<html lang="zh-CN"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<script id="tailwind-config">
        tailwind.config = {
            darkMode: "class",
            theme: {
                extend: {
                    colors: {
                        "primary": "#667aea",
                        "background-light": "#f6f6f8",
                        "background-dark": "#111421",
                    },
                    fontFamily: {
                        "display": ["Inter"]
                    },
                    borderRadius: {"DEFAULT": "0.25rem", "lg": "0.5rem", "xl": "0.75rem", "full": "9999px"},
                },
            },
        }
    </script>
<style>
        body { font-family: 'Inter', sans-serif; }
        .material-symbols-outlined { font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24; }
    </style>
</head>
<body class="bg-background-light dark:bg-background-dark text-slate-900 dark:text-slate-100 font-display">
<div class="relative flex h-screen w-full flex-col overflow-hidden">
<!-- Top Navigation Bar -->
<header class="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-6 py-3 z-10">
<div class="flex items-center gap-3">
<div class="bg-primary p-1.5 rounded-lg text-white">
<span class="material-symbols-outlined text-2xl">hub</span>
</div>
<h2 class="text-lg font-bold tracking-tight">AI Collaborative Team</h2>
</div>
<div class="flex flex-1 justify-center max-w-2xl px-8">
<div class="relative w-full">
<span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">search</span>
<input class="w-full bg-slate-100 dark:bg-slate-800 border-none rounded-lg py-2 pl-10 pr-4 focus:ring-2 focus:ring-primary text-sm" placeholder="搜索项目、任务或代理..." type="text"/>
</div>
</div>
<div class="flex items-center gap-3">
<button class="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400">
<span class="material-symbols-outlined">notifications</span>
</button>
<button class="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400">
<span class="material-symbols-outlined">settings</span>
</button>
<div class="h-8 w-8 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center overflow-hidden">
<img alt="User Profile Avatar" class="h-full w-full object-cover" data-alt="Minimalist user profile avatar circle" src="https://lh3.googleusercontent.com/aida-public/AB6AXuA28gdQiXeAGlqhfdWRY9Li-R2nCTpRh5rY0B4i7FiqG77lYsC6FBvajgz8ANoXEOdYRQdfF0Bt7KchIkvVQCaxUPed-hmAYxzjJUUyrV1RvloRsT3wgJC44eh6bGJtIvM5s-1L3BgrYVe9hmbwnKhv7fh5YZRphyect24YJ3kOy6u29O9NQO38Dk51ysLA6-IwRjPypnUuZolxaYbye-Bb2blM-PIJeHsp8fxyVtq53POHlskJvURdzDC1myrOr5uhvta9Rv2whlI"/>
</div>
</div>
</header>
<div class="flex flex-1 overflow-hidden">
<!-- Left Sidebar -->
<aside class="w-64 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col">
<nav class="flex-1 p-4 space-y-1">
<div class="flex items-center gap-3 px-3 py-2 rounded-lg bg-primary/10 text-primary">
<span class="material-symbols-outlined">dashboard</span>
<span class="text-sm font-semibold">控制台</span>
</div>
<div class="flex items-center gap-3 px-3 py-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors cursor-pointer">
<span class="material-symbols-outlined">folder</span>
<span class="text-sm font-medium">项目库</span>
</div>
<div class="flex items-center gap-3 px-3 py-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors cursor-pointer">
<span class="material-symbols-outlined">group</span>
<span class="text-sm font-medium">团队成员</span>
</div>
<div class="flex items-center gap-3 px-3 py-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors cursor-pointer">
<span class="material-symbols-outlined">smart_toy</span>
<span class="text-sm font-medium">AI 代理</span>
</div>
</nav>
<div class="p-4 border-t border-slate-200 dark:border-slate-800">
<h3 class="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-4 px-3">当前任务</h3>
<!-- Empty State Task Section -->
<div class="flex flex-col items-center justify-center py-8 px-3 rounded-xl border-2 border-dashed border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/20">
<span class="material-symbols-outlined text-slate-300 dark:text-slate-700 text-3xl mb-2">task_alt</span>
<p class="text-slate-900 dark:text-slate-100 text-sm font-semibold">暂无任务</p>
<p class="text-slate-400 dark:text-slate-500 text-xs text-center mt-1">你的任务列表目前为空</p>
<button class="mt-4 w-full py-1.5 text-xs font-bold bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg hover:shadow-sm transition-all text-primary">
                            + 添加任务
                        </button>
</div>
</div>
<div class="p-4 bg-slate-50 dark:bg-slate-800/50 m-4 rounded-xl">
<div class="flex items-center gap-2 mb-2">
<div class="size-2 rounded-full bg-green-500"></div>
<span class="text-xs font-medium text-slate-600 dark:text-slate-400">3 个 AI 代理在线</span>
</div>
<p class="text-[10px] text-slate-400">已准备好协作处理您的下一个需求</p>
</div>
</aside>
<!-- Main Chat Area -->
<main class="flex-1 flex flex-col relative bg-background-light dark:bg-background-dark">
<!-- Large Central Placeholder Empty State -->
<div class="flex-1 flex flex-col items-center justify-center p-8">
<div class="max-w-md w-full flex flex-col items-center text-center">
<div class="relative mb-8">
<div class="absolute -inset-4 bg-primary/10 rounded-full blur-2xl"></div>
<div class="relative bg-white dark:bg-slate-900 size-24 rounded-3xl shadow-xl flex items-center justify-center border border-slate-100 dark:border-slate-800">
<span class="material-symbols-outlined text-primary text-5xl">forum</span>
</div>
</div>
<h1 class="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-3 tracking-tight">开始与AI团队交流</h1>
<p class="text-slate-500 dark:text-slate-400 mb-8 leading-relaxed">
                            欢迎来到您的协作空间。连接您的 AI 代理，开始在您的下一个伟大创意上进行协作。无论是以编码、写作还是数据分析，您的团队都已就绪。
                        </p>
<div class="flex flex-col sm:flex-row gap-3">
<button class="px-8 py-3 bg-primary text-white rounded-xl font-bold shadow-lg shadow-primary/25 hover:scale-[1.02] active:scale-[0.98] transition-all">
                                创建新项目
                            </button>
<button class="px-8 py-3 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-800 rounded-xl font-bold hover:bg-slate-50 dark:hover:bg-slate-800 transition-all">
                                查看教程
                            </button>
</div>
</div>
</div>
<!-- Input Area Bar (Empty Style) -->
<div class="p-6">
<div class="max-w-4xl mx-auto relative">
<div class="absolute inset-0 bg-primary/5 rounded-2xl blur-lg -z-10"></div>
<div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm p-4 flex items-end gap-3 opacity-60 pointer-events-none">
<button class="p-2 text-slate-400">
<span class="material-symbols-outlined">add_circle</span>
</button>
<div class="flex-1 py-2 text-slate-400 text-sm">
                                输入消息与 AI 代理协作...
                            </div>
<button class="size-10 bg-slate-100 dark:bg-slate-800 rounded-xl flex items-center justify-center text-slate-300">
<span class="material-symbols-outlined">send</span>
</button>
</div>
</div>
</div>
<!-- Floating Decorative Gradients -->
<div class="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full blur-3xl -z-10"></div>
<div class="absolute bottom-0 left-0 w-96 h-96 bg-primary/5 rounded-full blur-3xl -z-10"></div>
</main>
</div>
</div>
</body></html>