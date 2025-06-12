/**
 * 论文模块化生成页面的JavaScript代码
 */

// CSRF Token获取
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

// 全局变量
let isGenerating = false;
let currentOperation = '';
let statusCheckInterval = null;

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化事件监听器
    initEventListeners();
    
    // 初始化富文本编辑器
    initRichTextEditors();
    
    // 初始化提示信息
    initTooltips();
});

// 初始化事件监听器
function initEventListeners() {
    // 生成中文摘要按钮
    document.getElementById('generate-abstract-cn-btn').addEventListener('click', generateAbstractCN);
    
    // 生成中文关键词按钮
    document.getElementById('generate-keywords-cn-btn').addEventListener('click', generateKeywordsCN);
    
    // 生成英文摘要按钮
    document.getElementById('generate-abstract-en-btn').addEventListener('click', generateAbstractEN);
    
    // 生成英文关键词按钮
    document.getElementById('generate-keywords-en-btn').addEventListener('click', generateKeywordsEN);
    
    // 生成论文正文按钮
    document.getElementById('generate-body-btn').addEventListener('click', generateBody);
    
    // 生成参考文献按钮
    document.getElementById('generate-references-btn').addEventListener('click', generateReferences);
    
    // 生成致谢按钮
    document.getElementById('generate-acknowledgement-btn').addEventListener('click', generateAcknowledgement);
    
    // 停止生成按钮
    document.getElementById('stop-generation-btn').addEventListener('click', stopGeneration);
    
    // 解析大纲按钮
    document.getElementById('parse-outline-btn').addEventListener('click', parseOutline);
    
    // 复制内容按钮
    document.querySelectorAll('.copy-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            copyContent(targetId);
        });
    });
    
    // 清空内容按钮
    document.querySelectorAll('.clear-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            clearContent(targetId);
        });
    });
}

// 初始化富文本编辑器
function initRichTextEditors() {
    // 如果页面中有富文本编辑器，初始化它们
    if (typeof ClassicEditor !== 'undefined') {
        const editorElements = document.querySelectorAll('.rich-editor');
        editorElements.forEach(element => {
            ClassicEditor
                .create(element, {
                    toolbar: ['heading', '|', 'bold', 'italic', 'link', 'bulletedList', 'numberedList', 'blockQuote'],
                    placeholder: element.getAttribute('placeholder') || '请输入内容...'
                })
                .catch(error => {
                    console.error('富文本编辑器初始化失败:', error);
                });
        });
    }
}

// 初始化提示信息
function initTooltips() {
    // 如果页面中有Bootstrap提示工具，初始化它们
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

/**
 * 生成中文摘要
 */
async function generateAbstractCN() {
    if (isGenerating) {
        showAlert('warning', '有生成任务正在进行中，请等待完成或点击停止按钮');
        return;
    }
    
    // 获取输入
    const title = document.getElementById('title').value.trim();
    const outline = document.getElementById('outline').value.trim();
    const subject = document.getElementById('subject').value;
    const educationLevel = document.getElementById('education-level').value;
    const customPrompt = document.getElementById('custom-prompt-abstract-cn').value.trim();
    
    // 验证输入
    if (!title) {
        showAlert('danger', '请输入论文标题');
        return;
    }
    
    if (!outline) {
        showAlert('danger', '请输入论文大纲');
        return;
    }
    
    // 开始生成
    setGeneratingState(true, '正在生成中文摘要...');
    
    try {
        // 发送请求
        const response = await fetch('/paper_module/generate_abstract_cn', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                title: title,
                outline: outline,
                subject: subject,
                education_level: educationLevel,
                custom_prompt: customPrompt
            })
        });
        
        // 处理响应
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('abstract-cn').value = data.abstract_cn;
            showAlert('success', '中文摘要生成成功');
        } else {
            showAlert('danger', `生成失败: ${data.message || '未知错误'}`);
        }
    } catch (error) {
        console.error('生成中文摘要出错:', error);
        showAlert('danger', `生成出错: ${error.message || '网络错误'}`);
    } finally {
        setGeneratingState(false);
    }
}

/**
 * 生成中文关键词
 */
async function generateKeywordsCN() {
    if (isGenerating) {
        showAlert('warning', '有生成任务正在进行中，请等待完成或点击停止按钮');
        return;
    }
    
    // 获取输入
    const title = document.getElementById('title').value.trim();
    const abstractCN = document.getElementById('abstract-cn').value.trim();
    const subject = document.getElementById('subject').value;
    const educationLevel = document.getElementById('education-level').value;
    const customPrompt = document.getElementById('custom-prompt-keywords-cn').value.trim();
    
    // 验证输入
    if (!title) {
        showAlert('danger', '请输入论文标题');
        return;
    }
    
    if (!abstractCN) {
        showAlert('danger', '请先生成或输入中文摘要');
        return;
    }
    
    // 开始生成
    setGeneratingState(true, '正在生成中文关键词...');
    
    try {
        // 发送请求
        const response = await fetch('/paper_module/generate_keywords_cn', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                title: title,
                abstract_cn: abstractCN,
                subject: subject,
                education_level: educationLevel,
                custom_prompt: customPrompt
            })
        });
        
        // 处理响应
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('keywords-cn').value = data.keywords_cn;
            showAlert('success', '中文关键词生成成功');
        } else {
            showAlert('danger', `生成失败: ${data.message || '未知错误'}`);
        }
    } catch (error) {
        console.error('生成中文关键词出错:', error);
        showAlert('danger', `生成出错: ${error.message || '网络错误'}`);
    } finally {
        setGeneratingState(false);
    }
}

/**
 * 生成英文摘要
 */
async function generateAbstractEN() {
    if (isGenerating) {
        showAlert('warning', '有生成任务正在进行中，请等待完成或点击停止按钮');
        return;
    }
    
    // 获取输入
    const title = document.getElementById('title').value.trim();
    const abstractCN = document.getElementById('abstract-cn').value.trim();
    const subject = document.getElementById('subject').value;
    const educationLevel = document.getElementById('education-level').value;
    const customPrompt = document.getElementById('custom-prompt-abstract-en').value.trim();
    
    // 验证输入
    if (!title) {
        showAlert('danger', '请输入论文标题');
        return;
    }
    
    if (!abstractCN) {
        showAlert('danger', '请先生成或输入中文摘要');
        return;
    }
    
    // 开始生成
    setGeneratingState(true, '正在生成英文摘要...');
    
    try {
        // 发送请求
        const response = await fetch('/paper_module/generate_abstract_en', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                title: title,
                abstract_cn: abstractCN,
                subject: subject,
                education_level: educationLevel,
                custom_prompt: customPrompt
            })
        });
        
        // 处理响应
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('abstract-en').value = data.abstract_en;
            showAlert('success', '英文摘要生成成功');
        } else {
            showAlert('danger', `生成失败: ${data.message || '未知错误'}`);
        }
    } catch (error) {
        console.error('生成英文摘要出错:', error);
        showAlert('danger', `生成出错: ${error.message || '网络错误'}`);
    } finally {
        setGeneratingState(false);
    }
}

/**
 * 生成英文关键词
 */
async function generateKeywordsEN() {
    if (isGenerating) {
        showAlert('warning', '有生成任务正在进行中，请等待完成或点击停止按钮');
        return;
    }
    
    // 获取输入
    const title = document.getElementById('title').value.trim();
    const keywordsCN = document.getElementById('keywords-cn').value.trim();
    const subject = document.getElementById('subject').value;
    const educationLevel = document.getElementById('education-level').value;
    const customPrompt = document.getElementById('custom-prompt-keywords-en').value.trim();
    
    // 验证输入
    if (!title) {
        showAlert('danger', '请输入论文标题');
        return;
    }
    
    if (!keywordsCN) {
        showAlert('danger', '请先生成或输入中文关键词');
        return;
    }
    
    // 开始生成
    setGeneratingState(true, '正在生成英文关键词...');
    
    try {
        // 发送请求
        const response = await fetch('/paper_module/generate_keywords_en', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                title: title,
                keywords_cn: keywordsCN,
                subject: subject,
                education_level: educationLevel,
                custom_prompt: customPrompt
            })
        });
        
        // 处理响应
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('keywords-en').value = data.keywords_en;
            showAlert('success', '英文关键词生成成功');
        } else {
            showAlert('danger', `生成失败: ${data.message || '未知错误'}`);
        }
    } catch (error) {
        console.error('生成英文关键词出错:', error);
        showAlert('danger', `生成出错: ${error.message || '网络错误'}`);
    } finally {
        setGeneratingState(false);
    }
}

/**
 * 生成论文正文
 */
async function generateBody() {
    if (isGenerating) {
        showAlert('warning', '有生成任务正在进行中，请等待完成或点击停止按钮');
        return;
    }
    
    // 获取输入
    const title = document.getElementById('title').value.trim();
    const outline = document.getElementById('outline').value.trim();
    const wordCount = parseInt(document.getElementById('word-count').value) || 3000;
    const subject = document.getElementById('subject').value;
    const educationLevel = document.getElementById('education-level').value;
    const customPrompt = document.getElementById('custom-prompt-body').value.trim();
    
    // 验证输入
    if (!title) {
        showAlert('danger', '请输入论文标题');
        return;
    }
    
    if (!outline) {
        showAlert('danger', '请输入论文大纲');
        return;
    }
    
    if (wordCount < 1000 || wordCount > 20000) {
        showAlert('warning', '字数应在1000-20000之间，已自动调整');
    }
    
    // 开始生成
    setGeneratingState(true, '正在生成论文正文...');
    
    // 显示进度条
    const progressBar = document.getElementById('generation-progress-bar');
    const progressSection = document.getElementById('generation-section');
    progressBar.style.width = '0%';
    progressBar.setAttribute('aria-valuenow', 0);
    progressBar.textContent = '0%';
    document.getElementById('generation-progress-container').style.display = 'block';
    
    try {
        // 发送请求
        const response = await fetch('/paper_module/generate_paper_body', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                title: title,
                outline: outline,
                word_count: wordCount,
                subject: subject,
                education_level: educationLevel,
                custom_prompt: customPrompt
            })
        });
        
        // 处理响应
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('body').value = data.body;
            showAlert('success', '论文正文生成成功');
        } else {
            showAlert('danger', `生成失败: ${data.message || '未知错误'}`);
        }
        
        // 开始轮询状态
        startStatusPolling();
    } catch (error) {
        console.error('生成论文正文出错:', error);
        showAlert('danger', `生成出错: ${error.message || '网络错误'}`);
        setGeneratingState(false);
    }
}

/**
 * 开始轮询生成状态
 */
function startStatusPolling() {
    // 清除可能存在的旧定时器
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
    }
    
    // 设置新的定时器，每秒检查一次状态
    statusCheckInterval = setInterval(async function() {
        try {
            const response = await fetch('/paper_module/status');
            const data = await response.json();
            
            // 更新进度条
            const progressBar = document.getElementById('generation-progress-bar');
            const progressSection = document.getElementById('generation-section');
            const progressPercentage = Math.round(data.progress * 100);
            
            progressBar.style.width = `${progressPercentage}%`;
            progressBar.setAttribute('aria-valuenow', progressPercentage);
            progressBar.textContent = `${progressPercentage}%`;
            progressSection.textContent = data.current_section;
            
            // 如果有内容，更新预览区域
            if (data.content) {
                document.getElementById('body-preview').innerHTML = data.content;
            }
            
            // 如果生成完成或出错，停止轮询
            if (!data.in_progress) {
                clearInterval(statusCheckInterval);
                setGeneratingState(false);
                
                // 如果有内容，更新文本区域
                if (data.content && !document.getElementById('body').value) {
                    document.getElementById('body').value = data.content;
                }
            }
        } catch (error) {
            console.error('获取生成状态出错:', error);
            clearInterval(statusCheckInterval);
            setGeneratingState(false);
        }
    }, 1000);
}

/**
 * 生成参考文献
 */
async function generateReferences() {
    if (isGenerating) {
        showAlert('warning', '有生成任务正在进行中，请等待完成或点击停止按钮');
        return;
    }
    
    // 获取输入
    const title = document.getElementById('title').value.trim();
    const subject = document.getElementById('subject').value;
    const educationLevel = document.getElementById('education-level').value;
    const customPrompt = document.getElementById('custom-prompt-references').value.trim();
    
    // 验证输入
    if (!title) {
        showAlert('danger', '请输入论文标题');
        return;
    }
    
    // 开始生成
    setGeneratingState(true, '正在生成参考文献...');
    
    try {
        // 发送请求
        const response = await fetch('/paper_module/generate_references', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                title: title,
                subject: subject,
                education_level: educationLevel,
                custom_prompt: customPrompt
            })
        });
        
        // 处理响应
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('references').value = data.references;
            showAlert('success', '参考文献生成成功');
        } else {
            showAlert('danger', `生成失败: ${data.message || '未知错误'}`);
        }
    } catch (error) {
        console.error('生成参考文献出错:', error);
        showAlert('danger', `生成出错: ${error.message || '网络错误'}`);
    } finally {
        setGeneratingState(false);
    }
}

/**
 * 生成致谢
 */
async function generateAcknowledgement() {
    if (isGenerating) {
        showAlert('warning', '有生成任务正在进行中，请等待完成或点击停止按钮');
        return;
    }
    
    // 获取输入
    const title = document.getElementById('title').value.trim();
    const subject = document.getElementById('subject').value;
    const educationLevel = document.getElementById('education-level').value;
    const customPrompt = document.getElementById('custom-prompt-acknowledgement').value.trim();
    
    // 验证输入
    if (!title) {
        showAlert('danger', '请输入论文标题');
        return;
    }
    
    // 开始生成
    setGeneratingState(true, '正在生成致谢...');
    
    try {
        // 发送请求
        const response = await fetch('/paper_module/generate_acknowledgement', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                title: title,
                subject: subject,
                education_level: educationLevel,
                custom_prompt: customPrompt
            })
        });
        
        // 处理响应
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('acknowledgement').value = data.acknowledgement;
            showAlert('success', '致谢生成成功');
        } else {
            showAlert('danger', `生成失败: ${data.message || '未知错误'}`);
        }
    } catch (error) {
        console.error('生成致谢出错:', error);
        showAlert('danger', `生成出错: ${error.message || '网络错误'}`);
    } finally {
        setGeneratingState(false);
    }
}

/**
 * 停止生成
 */
async function stopGeneration() {
    if (!isGenerating) {
        return;
    }
    
    try {
        const response = await fetch('/paper_module/stop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('info', '已停止生成');
        } else {
            showAlert('warning', `停止失败: ${data.message || '未知错误'}`);
        }
    } catch (error) {
        console.error('停止生成出错:', error);
        showAlert('danger', `操作出错: ${error.message || '网络错误'}`);
    } finally {
        setGeneratingState(false);
    }
}

/**
 * 解析大纲
 */
async function parseOutline() {
    const outline = document.getElementById('outline').value.trim();
    
    if (!outline) {
        showAlert('danger', '请输入论文大纲');
        return;
    }
    
    try {
        const response = await fetch('/paper_module/parse_outline', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                outline_text: outline
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 显示解析结果
            const outlineInfo = document.getElementById('outline-info');
            outlineInfo.innerHTML = `
                <div class="alert alert-info">
                    <p><strong>大纲解析结果:</strong></p>
                    <p>共有 ${data.section_count} 个最小级别章节需要生成</p>
                </div>
            `;
            
            // 如果想要显示详细的大纲结构，可以在这里添加代码
            
            showAlert('success', '大纲解析成功');
        } else {
            showAlert('danger', `解析失败: ${data.error || '未知错误'}`);
        }
    } catch (error) {
        console.error('解析大纲出错:', error);
        showAlert('danger', `操作出错: ${error.message || '网络错误'}`);
    }
}

/**
 * 复制内容
 */
function copyContent(targetId) {
    const targetElement = document.getElementById(targetId);
    
    if (!targetElement) {
        return;
    }
    
    // 获取内容
    const content = targetElement.value;
    
    if (!content) {
        showAlert('warning', '没有内容可复制');
        return;
    }
    
    // 复制到剪贴板
    navigator.clipboard.writeText(content)
        .then(() => {
            showAlert('success', '内容已复制到剪贴板');
        })
        .catch(err => {
            console.error('复制失败:', err);
            showAlert('danger', '复制失败，请手动复制');
        });
}

/**
 * 清空内容
 */
function clearContent(targetId) {
    const targetElement = document.getElementById(targetId);
    
    if (!targetElement) {
        return;
    }
    
    // 清空内容
    targetElement.value = '';
    
    // 如果是预览区域，也清空HTML
    const previewElement = document.getElementById(`${targetId}-preview`);
    if (previewElement) {
        previewElement.innerHTML = '';
    }
}

/**
 * 设置生成状态
 */
function setGeneratingState(generating, operation = '') {
    isGenerating = generating;
    currentOperation = operation;
    
    // 更新UI状态
    const generateButtons = document.querySelectorAll('.generate-btn');
    const stopButton = document.getElementById('stop-generation-btn');
    const statusText = document.getElementById('generation-status');
    
    if (generating) {
        // 禁用所有生成按钮
        generateButtons.forEach(btn => {
            btn.disabled = true;
            btn.classList.add('disabled');
        });
        
        // 启用停止按钮
        stopButton.disabled = false;
        stopButton.classList.remove('disabled');
        
        // 显示当前操作
        statusText.textContent = operation;
        statusText.parentElement.style.display = 'block';
    } else {
        // 启用所有生成按钮
        generateButtons.forEach(btn => {
            btn.disabled = false;
            btn.classList.remove('disabled');
        });
        
        // 禁用停止按钮
        stopButton.disabled = true;
        stopButton.classList.add('disabled');
        
        // 隐藏状态文本
        statusText.textContent = '';
        statusText.parentElement.style.display = 'none';
        
        // 隐藏进度条
        document.getElementById('generation-progress-container').style.display = 'none';
    }
}

/**
 * 显示提示信息
 */
function showAlert(type, message, timeout = 5000) {
    // 创建提示元素
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type} alert-dismissible fade show`;
    alertElement.role = 'alert';
    
    // 设置内容
    alertElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="关闭"></button>
    `;
    
    // 添加到页面
    const alertContainer = document.getElementById('alert-container');
    alertContainer.appendChild(alertElement);
    
    // 自动关闭
    if (timeout > 0) {
        setTimeout(() => {
            try {
                // 使用Bootstrap的dismiss方法关闭
                if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
                    const bsAlert = new bootstrap.Alert(alertElement);
                    bsAlert.close();
                } else {
                    // 如果没有Bootstrap，手动移除
                    alertElement.remove();
                }
            } catch (error) {
                // 出错时直接移除元素
                alertElement.remove();
            }
        }, timeout);
    }
}

// 防止XSS攻击的辅助函数
function escapeHTML(str) {
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// 限制输入字数的辅助函数
function limitInputLength(inputElement, maxLength) {
    if (inputElement.value.length > maxLength) {
        inputElement.value = inputElement.value.substring(0, maxLength);
        showAlert('warning', `输入已超过${maxLength}字符限制，已自动截断`);
    }
}

// 添加防抖功能的辅助函数
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}
