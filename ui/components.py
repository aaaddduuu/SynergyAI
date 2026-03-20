"""
AI Coworker Team - UI Components Module

Reusable UI components for the frontend.
"""

# Component registry - maps component names to their HTML templates
COMPONENTS = {}


def register_component(name: str):
    """Decorator to register a component"""
    def decorator(func):
        COMPONENTS[name] = func
        return func
    return decorator


def render_component(name: str, **kwargs) -> str:
    """Render a registered component with given parameters"""
    if name not in COMPONENTS:
        return f"<!-- Component '{name}' not found -->"
    return COMPONENTS[name](**kwargs)


# ==================== Base Button Component ====================
@register_component('button')
def button_component(
    variant: str = 'primary',
    size: str = 'md',
    icon: str = None,
    icon_position: str = 'left',
    disabled: bool = False,
    loading: bool = False,
    onclick: str = None,
    id: str = None,
    class_name: str = '',
    children: str = ''
) -> str:
    """Glass button component with variants"""
    
    base_classes = 'inline-flex items-center justify-center font-semibold transition-all duration-0.3 ease'
    
    variants = {
        'primary': 'bg-gradient-to-r from-[#667aea] to-[#764ba2] text-white shadow-lg shadow-primary/25 hover:shadow-primary/40 hover:-translate-y-0.5',
        'secondary': 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700',
        'ghost': 'bg-transparent text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800',
        'danger': 'bg-red-500 text-white hover:bg-red-600',
    }
    
    sizes = {
        'sm': 'px-3 py-1.5 text-xs rounded-lg gap-1.5',
        'md': 'px-5 py-2.5 text-sm rounded-xl gap-2',
        'lg': 'px-6 py-3 text-base rounded-xl gap-2',
    }
    
    classes = f"{base_classes} {variants.get(variant, variants['primary'])} {sizes.get(size, sizes['md'])} {class_name}"
    
    if disabled or loading:
        classes += ' opacity-50 cursor-not-allowed'
    
    icon_html = ''
    if loading:
        icon_html = '<svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>'
    elif icon:
        icon_html = f'<span class="material-symbols-outlined text-[18px]">{icon}</span>'
    
    content = f"{icon_html}{children}" if icon_position == 'left' else f"{children}{icon_html}"
    
    onclick_attr = f" onclick=\"{onclick}\"" if onclick else ""
    id_attr = f" id=\"{id}\"" if id else ""
    
    return f'<button class="{classes}"{onclick_attr}{id_attr}>{content}</button>'


# ==================== Card Component ====================
@register_component('card')
def card_component(
    title: str = None,
    subtitle: str = None,
    padding: str = 'md',
    hover: bool = False,
    class_name: str = '',
    children: str = '',
    footer: str = None,
    header_action: str = None
) -> str:
    """Glass card component"""
    
    paddings = {
        'none': '',
        'sm': 'p-4',
        'md': 'p-6',
        'lg': 'p-8',
    }
    
    hover_class = 'hover:shadow-lg transition-shadow duration-0.3' if hover else ''
    
    header_html = ''
    if title or subtitle or header_action:
        header_html = f'''
        <div class="flex items-center justify-between mb-4">
            <div>
                {f'<h3 class="text-lg font-bold text-slate-900 dark:text-white">{title}</h3>' if title else ''}
                {f'<p class="text-sm text-slate-500 dark:text-slate-400 mt-1">{subtitle}</p>' if subtitle else ''}
            </div>
            {header_action if header_action else ''}
        </div>
        '''
    
    footer_html = f'<div class="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">{footer}</div>' if footer else ''
    
    return f'''
    <div class="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 {paddings.get(padding, paddings['md'])} {hover_class} {class_name}">
        {header_html}
        {children}
        {footer_html}
    </div>
    '''


# ==================== Input Component ====================
@register_component('input')
def input_component(
    type: str = 'text',
    name: str = None,
    id: str = None,
    placeholder: str = '',
    value: str = '',
    label: str = None,
    error: str = None,
    icon_left: str = None,
    icon_right: str = None,
    disabled: bool = False,
    required: bool = False,
    class_name: str = '',
    onchange: str = None,
    onkeypress: str = None
) -> str:
    """Glass input component"""
    
    label_html = f'<label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">{label}</label>' if label else ''
    
    icon_left_html = f'<span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">{icon_left}</span>' if icon_left else ''
    icon_right_html = f'<span class="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-slate-400">{icon_right}</span>' if icon_right else ''
    
    padding_left = 'pl-10' if icon_left else 'pl-4'
    padding_right = 'pr-10' if icon_right else 'pr-4'
    
    error_class = 'border-red-500 focus:ring-red-500/20' if error else 'focus:ring-primary/20 focus:border-primary'
    
    disabled_attr = 'disabled' if disabled else ''
    required_attr = 'required' if required else ''
    onchange_attr = f' onchange="{onchange}"' if onchange else ''
    onkeypress_attr = f' onkeypress="{onkeypress}"' if onkeypress else ''
    
    input_html = f'''
    <div class="relative">
        {icon_left_html}
        <input 
            type="{type}" 
            name="{name}" 
            id="{id}"
            placeholder="{placeholder}" 
            value="{value}"
            class="w-full h-12 {padding_left} {padding_right} rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white appearance-none focus:ring-2 {error_class} outline-none transition-all disabled:opacity-50 disabled:cursor-not-allowed {class_name}"
            {disabled_attr}
            {required_attr}
            {onchange_attr}
            {onkeypress_attr}
        />
        {icon_right_html}
    </div>
    '''
    
    error_html = f'<p class="mt-1 text-xs text-red-500">{error}</p>' if error else ''
    
    return f'{label_html}{input_html}{error_html}'


# ==================== Select Component ====================
@register_component('select')
def select_component(
    name: str = None,
    id: str = None,
    label: str = None,
    placeholder: str = '请选择...',
    options: list = None,
    value: str = '',
    disabled: bool = False,
    required: bool = False,
    class_name: str = '',
    onchange: str = None
) -> str:
    """Glass select component"""
    
    options = options or []
    
    label_html = f'<label class="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">{label}</label>' if label else ''
    
    options_html = ''.join([
        f'<option value="{opt.get("value", "")}" {"selected" if opt.get("value") == value else ""}>{opt.get("label", "")}</option>'
        for opt in options
    ])
    
    placeholder_html = f'<option disabled {"selected" if not value else ""} value="">{placeholder}</option>'
    
    disabled_attr = 'disabled' if disabled else ''
    required_attr = 'required' if required else ''
    onchange_attr = f' onchange="{onchange}"' if onchange else ''
    
    return f'''
    {label_html}
    <div class="relative">
        <select 
            name="{name}" 
            id="{id}"
            class="w-full h-12 px-4 pr-10 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white appearance-none focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all {class_name}"
            {disabled_attr}
            {required_attr}
            {onchange_attr}
        >
            {placeholder_html}
            {options_html}
        </select>
        <span class="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none">expand_more</span>
    </div>
    '''


# ==================== Badge Component ====================
@register_component('badge')
def badge_component(
    variant: str = 'default',
    size: str = 'md',
    dot: bool = False,
    pulse: bool = False,
    class_name: str = '',
    children: str = ''
) -> str:
    """Glass badge component"""
    
    variants = {
        'default': 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300',
        'primary': 'bg-primary/10 text-primary border border-primary/20',
        'success': 'bg-emerald-500/10 text-emerald-600 border border-emerald-500/20',
        'warning': 'bg-amber-500/10 text-amber-600 border border-amber-500/20',
        'danger': 'bg-red-500/10 text-red-600 border border-red-500/20',
        'info': 'bg-blue-500/10 text-blue-600 border border-blue-500/20',
    }
    
    sizes = {
        'sm': 'px-2 py-0.5 text-xs',
        'md': 'px-2.5 py-1 text-xs',
        'lg': 'px-3 py-1.5 text-sm',
    }
    
    dot_color = {
        'default': 'bg-slate-500',
        'primary': 'bg-primary',
        'success': 'bg-emerald-500',
        'warning': 'bg-amber-500',
        'danger': 'bg-red-500',
        'info': 'bg-blue-500',
    }
    
    dot_html = f'<span class="w-1.5 h-1.5 rounded-full {dot_color.get(variant, "bg-slate-500")} {("animate-pulse" if pulse else "")} mr-1.5"></span>' if dot else ''
    
    return f'<span class="inline-flex items-center rounded-full font-medium {variants.get(variant, variants["default"])} {sizes.get(size, sizes["md"])} {class_name}">{dot_html}{children}</span>'


# ==================== Modal Component ====================
@register_component('modal')
def modal_component(
    id: str,
    title: str = None,
    size: str = 'md',
    show_close: bool = True,
    close_on_overlay: bool = True,
    children: str = '',
    footer: str = None,
    onclose: str = None
) -> str:
    """Glass modal component"""
    
    sizes = {
        'sm': 'max-w-sm',
        'md': 'max-w-md',
        'lg': 'max-w-2xl',
        'xl': 'max-w-4xl',
    }
    
    overlay_click = f"onclick=\"{onclose if onclose else f'hideModal(\"{id}\")'}\"" if close_on_overlay else ''
    
    close_button = f'''
    <button onclick="{onclose if onclose else f'hideModal(\"{id}\")'}" class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors">
        <span class="material-symbols-outlined">close</span>
    </button>
    ''' if show_close else ''
    
    header_html = f'''
    <div class="px-6 py-4 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between">
        <h3 class="text-xl font-bold text-slate-900 dark:text-white">{title}</h3>
        {close_button}
    </div>
    ''' if title or show_close else ''
    
    footer_html = f'<div class="px-6 py-4 bg-slate-50 dark:bg-slate-800/50 flex justify-end gap-3">{footer}</div>' if footer else ''
    
    return f'''
    <div id="{id}" class="fixed inset-0 z-50 hidden">
        <div class="absolute inset-0 bg-slate-900/60 backdrop-blur-sm" {overlay_click}></div>
        <div class="relative flex items-center justify-center min-h-screen p-4">
            <div class="w-full {sizes.get(size, sizes['md'])} bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden">
                {header_html}
                <div class="p-6">{children}</div>
                {footer_html}
            </div>
        </div>
    </div>
    '''


# ==================== Avatar Component ====================
@register_component('avatar')
def avatar_component(
    src: str = None,
    alt: str = None,
    size: str = 'md',
    status: str = None,
    class_name: str = ''
) -> str:
    """Avatar component with status indicator"""
    
    sizes = {
        'xs': 'w-6 h-6 text-xs',
        'sm': 'w-8 h-8 text-sm',
        'md': 'w-10 h-10 text-base',
        'lg': 'w-12 h-12 text-lg',
        'xl': 'w-16 h-16 text-xl',
    }
    
    status_colors = {
        'online': 'bg-emerald-500',
        'offline': 'bg-slate-400',
        'busy': 'bg-red-500',
        'away': 'bg-amber-500',
    }
    
    status_html = f'<span class="absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-white dark:border-slate-900 {status_colors.get(status, "")}"></span>' if status else ''
    
    if src:
        img_html = f'<img src="{src}" alt="{alt or "Avatar"}" class="w-full h-full object-cover" />'
    else:
        img_html = f'<span class="material-symbols-outlined">person</span>'
    
    return f'''
    <div class="relative inline-block {sizes.get(size, sizes['md'])} {class_name}">
        <div class="w-full h-full rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center overflow-hidden">
            {img_html}
        </div>
        {status_html}
    </div>
    '''


# ==================== Progress Bar Component ====================
@register_component('progress')
def progress_component(
    value: int = 0,
    max: int = 100,
    show_label: bool = True,
    size: str = 'md',
    color: str = 'primary',
    striped: bool = False,
    animated: bool = False,
    class_name: str = ''
) -> str:
    """Progress bar component"""
    
    percentage = min(100, max(0, (value / max) * 100))
    
    sizes = {
        'sm': 'h-1',
        'md': 'h-2',
        'lg': 'h-3',
    }
    
    colors = {
        'primary': 'bg-gradient-to-r from-[#667aea] to-[#764ba2]',
        'success': 'bg-emerald-500',
        'warning': 'bg-amber-500',
        'danger': 'bg-red-500',
        'info': 'bg-blue-500',
    }
    
    striped_class = 'bg-stripes' if striped else ''
    animate_class = 'animate-pulse' if animated else ''
    
    return f'''
    <div class="w-full {class_name}">
        {f'<div class="flex justify-between mb-1"><span class="text-xs font-medium text-slate-700 dark:text-slate-300">完成进度</span><span class="text-xs font-medium text-slate-500">{percentage:.0f}%</span></div>' if show_label else ''}
        <div class="w-full bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden {sizes.get(size, sizes['md'])}">
            <div class="h-full rounded-full {colors.get(color, colors['primary'])} {striped_class} {animate_class} transition-all duration-500" style="width: {percentage}%"></div>
        </div>
    </div>
    '''


# ==================== Empty State Component ====================
@register_component('empty')
def empty_state_component(
    icon: str = 'inbox',
    title: str = '暂无数据',
    description: str = None,
    action: str = None,
    class_name: str = ''
) -> str:
    """Empty state component"""
    
    desc_html = f'<p class="text-slate-500 dark:text-slate-400 text-sm mt-2">{description}</p>' if description else ''
    action_html = f'<div class="mt-4">{action}</div>' if action else ''
    
    return f'''
    <div class="flex flex-col items-center justify-center py-12 text-center {class_name}">
        <div class="w-16 h-16 rounded-2xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center mb-4">
            <span class="material-symbols-outlined text-3xl text-slate-400">{icon}</span>
        </div>
        <h3 class="text-lg font-semibold text-slate-900 dark:text-white">{title}</h3>
        {desc_html}
        {action_html}
    </div>
    '''


# ==================== Tabs Component ====================
@register_component('tabs')
def tabs_component(
    tabs: list = None,
    active: str = None,
    class_name: str = '',
    onchange: str = None
) -> str:
    """Tabs component"""
    
    tabs = tabs or []
    
    tabs_html = ''.join([
        f'''
        <button 
            data-tab="{tab.get('id')}"
            class="flex-1 py-3 px-4 text-sm font-medium border-b-2 transition-colors {'border-primary text-primary' if active == tab.get('id') else 'border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'}"
            {f' onclick="{onchange}(\'{tab.get("id")}\')"' if onchange else ''}
        >
            {tab.get('icon', '') if tab.get('icon') else ''} {tab.get('label', '')}
        </button>
        ''' for tab in tabs
    ])
    
    return f'''
    <div class="border-b border-slate-200 dark:border-slate-700 {class_name}">
        <div class="flex">{tabs_html}</div>
    </div>
    '''


# ==================== Toast Notification Component ====================
@register_component('toast')
def toast_component(
    id: str,
    type: str = 'info',
    title: str = None,
    message: str,
    duration: int = 5000,
    dismissible: bool = True,
    class_name: str = ''
) -> str:
    """Toast notification component"""
    
    icons = {
        'success': 'check_circle',
        'error': 'error',
        'warning': 'warning',
        'info': 'info',
    }
    
    colors = {
        'success': 'bg-emerald-500/10 border-emerald-500/20 text-emerald-600',
        'error': 'bg-red-500/10 border-red-500/20 text-red-600',
        'warning': 'bg-amber-500/10 border-amber-500/20 text-amber-600',
        'info': 'bg-blue-500/10 border-blue-500/20 text-blue-600',
    }
    
    dismiss_button = f'''
    <button onclick="dismissToast('{id}')" class="ml-auto -mr-2 -mt-2 p-2 rounded-lg hover:bg-black/5 transition-colors">
        <span class="material-symbols-outlined text-sm">close</span>
    </button>
    ''' if dismissible else ''
    
    title_html = f'<p class="font-semibold">{title}</p>' if title else ''
    
    return f'''
    <div id="{id}" class="fixed top-4 right-4 z-[60] hidden animate-slide-in">
        <div class="flex items-start gap-3 p-4 rounded-xl border {colors.get(type, colors['info'])} {class_name}">
            <span class="material-symbols-outlined">{icons.get(type, 'info')}</span>
            <div class="flex-1">
                {title_html}
                <p class="text-sm">{message}</p>
            </div>
            {dismiss_button}
        </div>
    </div>
    <script>
        setTimeout(() => showToast('{id}'), 100);
        {f'setTimeout(() => dismissToast("{id}"), {duration})' if duration > 0 else ''}
    </script>
    '''


# ==================== Spinner Component ====================
@register_component('spinner')
def spinner_component(
    size: str = 'md',
    color: str = 'primary',
    class_name: str = ''
) -> str:
    """Loading spinner component"""
    
    sizes = {
        'sm': 'w-4 h-4',
        'md': 'w-6 h-6',
        'lg': 'w-8 h-8',
        'xl': 'w-12 h-12',
    }
    
    colors = {
        'primary': 'text-[#667aea]',
        'white': 'text-white',
        'current': 'currentColor',
    }
    
    return f'''
    <svg class="animate-spin {sizes.get(size, sizes['md'])} {colors.get(color, colors['primary'])} {class_name}" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
    '''


# ==================== Utility Functions ====================

def render_button(*args, **kwargs):
    """Legacy function for button rendering"""
    return button_component(**kwargs)


def render_card(*args, **kwargs):
    """Legacy function for card rendering"""
    return card_component(**kwargs)


def render_input(*args, **kwargs):
    """Legacy function for input rendering"""
    return input_component(**kwargs)


def render_modal(*args, **kwargs):
    """Legacy function for modal rendering"""
    return modal_component(**kwargs)


def render_badge(*args, **kwargs):
    """Legacy function for badge rendering"""
    return badge_component(**kwargs)


def get_component(name: str):
    """Get component function by name"""
    return COMPONENTS.get(name)
