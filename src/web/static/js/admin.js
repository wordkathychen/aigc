/**
 * AI文本生成器 - 管理后台JavaScript
 */

$(document).ready(function() {
    
    // 侧边栏切换
    $('#sidebarCollapse').on('click', function() {
        $('.sidebar').toggleClass('active');
        $('.content').toggleClass('active');
    });
    
    // 用户下拉菜单
    $('.user-dropdown .dropdown-toggle').on('click', function(e) {
        e.preventDefault();
        $('.user-dropdown .dropdown-menu').toggleClass('show');
    });
    
    // 点击页面其他地方关闭下拉菜单
    $(document).on('click', function(e) {
        if (!$(e.target).closest('.user-dropdown').length) {
            $('.user-dropdown .dropdown-menu').removeClass('show');
        }
    });
    
    // 表格中的开关控件
    $('.switch input').on('change', function() {
        const id = $(this).data('id');
        const type = $(this).data('type');
        const status = $(this).is(':checked');
        
        // 发送AJAX请求更新状态
        $.ajax({
            url: '/api/toggle_status',
            type: 'POST',
            data: {
                id: id,
                type: type,
                status: status
            },
            success: function(response) {
                if (response.success) {
                    showToast('状态已更新', 'success');
                } else {
                    showToast('更新失败: ' + response.message, 'error');
                    // 恢复开关状态
                    $(this).prop('checked', !status);
                }
            },
            error: function() {
                showToast('服务器错误，请稍后重试', 'error');
                // 恢复开关状态
                $(this).prop('checked', !status);
            }
        });
    });
    
    // 删除确认
    $('.btn-delete').on('click', function(e) {
        e.preventDefault();
        const url = $(this).attr('href');
        
        if (confirm('确定要删除吗？此操作不可撤销。')) {
            window.location.href = url;
        }
    });
    
    // 表单验证
    $('form.needs-validation').on('submit', function(e) {
        if (this.checkValidity() === false) {
            e.preventDefault();
            e.stopPropagation();
        }
        $(this).addClass('was-validated');
    });
    
    // 初始化提示框
    initTooltips();
    
    // 初始化数据表格
    initDataTables();
    
    // 初始化图表
    initCharts();
    
    // 敏感词管理
    initSensitiveWords();
    
    // API密钥管理
    initApiKeys();
    
    // 自动隐藏提示消息
    setTimeout(function() {
        $('.alert-dismissible').alert('close');
    }, 5000);
});

/**
 * 初始化提示框
 */
function initTooltips() {
    $('[data-toggle="tooltip"]').tooltip();
}

/**
 * 初始化数据表格
 */
function initDataTables() {
    if ($.fn.DataTable) {
        $('.data-table').DataTable({
            "language": {
                "lengthMenu": "每页显示 _MENU_ 条记录",
                "zeroRecords": "没有找到记录",
                "info": "第 _PAGE_ 页 ( 总共 _PAGES_ 页 )",
                "infoEmpty": "无记录",
                "infoFiltered": "(从 _MAX_ 条记录过滤)",
                "search": "搜索:",
                "paginate": {
                    "first": "首页",
                    "last": "末页",
                    "next": "下一页",
                    "previous": "上一页"
                }
            },
            "responsive": true
        });
    }
}

/**
 * 初始化图表
 */
function initCharts() {
    // 访问量趋势图
    if ($('#visitChart').length && window.Chart) {
        const ctx = document.getElementById('visitChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: '访问量',
                    data: chartData.visits,
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1,
                    tension: 0.4
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
    
    // 销售额趋势图
    if ($('#salesChart').length && window.Chart) {
        const ctx = document.getElementById('salesChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: '销售额',
                    data: chartData.sales,
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1,
                    tension: 0.4
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
}

/**
 * 敏感词管理
 */
function initSensitiveWords() {
    // 添加敏感词
    $('#addSensitiveWordForm').on('submit', function(e) {
        e.preventDefault();
        
        const word = $('#newSensitiveWord').val().trim();
        if (!word) return;
        
        $.ajax({
            url: '/admin/sensitive_words/add',
            type: 'POST',
            data: { word: word },
            success: function(response) {
                if (response.success) {
                    $('#newSensitiveWord').val('');
                    // 刷新页面或添加到列表
                    location.reload();
                } else {
                    showToast('添加失败: ' + response.message, 'error');
                }
            },
            error: function() {
                showToast('服务器错误，请稍后重试', 'error');
            }
        });
    });
    
    // 切换敏感词状态
    $('.toggle-sensitive-word').on('change', function() {
        const id = $(this).data('id');
        const status = $(this).is(':checked');
        
        $.ajax({
            url: '/admin/sensitive_words/toggle',
            type: 'POST',
            data: { id: id, status: status },
            success: function(response) {
                if (response.success) {
                    showToast('状态已更新', 'success');
                } else {
                    showToast('更新失败: ' + response.message, 'error');
                }
            },
            error: function() {
                showToast('服务器错误，请稍后重试', 'error');
            }
        });
    });
}

/**
 * API密钥管理
 */
function initApiKeys() {
    // 生成随机API密钥
    $('#generateApiKey').on('click', function() {
        const length = 32;
        const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
        let key = '';
        
        for (let i = 0; i < length; i++) {
            key += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        
        $('#apiKey').val(key);
    });
    
    // 切换API密钥状态
    $('.toggle-api-key').on('change', function() {
        const id = $(this).data('id');
        const status = $(this).is(':checked');
        
        $.ajax({
            url: '/admin/api_keys/toggle',
            type: 'POST',
            data: { id: id, status: status },
            success: function(response) {
                if (response.success) {
                    showToast('状态已更新', 'success');
                } else {
                    showToast('更新失败: ' + response.message, 'error');
                }
            },
            error: function() {
                showToast('服务器错误，请稍后重试', 'error');
            }
        });
    });
}

/**
 * 显示提示消息
 * @param {string} message - 消息内容
 * @param {string} type - 消息类型 (success, info, warning, error)
 */
function showToast(message, type = 'info') {
    const typeClass = type === 'error' ? 'danger' : type;
    
    const toast = `
        <div class="toast bg-${typeClass} text-white" role="alert" aria-live="assertive" aria-atomic="true" data-delay="5000">
            <div class="toast-header">
                <strong class="mr-auto">系统提示</strong>
                <button type="button" class="ml-2 mb-1 close" data-dismiss="toast" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    const toastContainer = $('#toastContainer');
    if (toastContainer.length === 0) {
        $('body').append('<div id="toastContainer" style="position: fixed; top: 20px; right: 20px; z-index: 9999;"></div>');
    }
    
    $('#toastContainer').append(toast);
    $('.toast').toast('show');
    
    // 5秒后自动移除
    setTimeout(function() {
        $('.toast').toast('hide').on('hidden.bs.toast', function() {
            $(this).remove();
        });
    }, 5000);
} 