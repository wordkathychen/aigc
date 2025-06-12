/**
 * AI文本生成器 - 主JavaScript文件
 */

// 文档加载完成后执行
$(document).ready(function() {
    
    // 侧边栏切换
    $('#sidebarCollapse').on('click', function() {
        $('.sidebar').toggleClass('active');
    });
    
    // 提示词模板表单验证
    if ($('#templateForm').length) {
        $('#templateForm').on('submit', function(e) {
            let valid = true;
            
            // 验证模板名称
            if ($('#name').val().trim() === '') {
                $('#name').addClass('is-invalid');
                valid = false;
            } else {
                $('#name').removeClass('is-invalid').addClass('is-valid');
            }
            
            // 验证模板类型
            if ($('#template_type').val() === '') {
                $('#template_type').addClass('is-invalid');
                valid = false;
            } else {
                $('#template_type').removeClass('is-invalid').addClass('is-valid');
            }
            
            // 验证模板内容
            if ($('#content').val().trim() === '') {
                $('#content').addClass('is-invalid');
                valid = false;
            } else {
                $('#content').removeClass('is-invalid').addClass('is-valid');
            }
            
            // 验证变量JSON格式
            let variables = $('#variables').val().trim();
            if (variables !== '') {
                try {
                    JSON.parse(variables);
                    $('#variables').removeClass('is-invalid').addClass('is-valid');
                } catch (e) {
                    $('#variables').addClass('is-invalid');
                    valid = false;
                }
            }
            
            if (!valid) {
                e.preventDefault();
                showAlert('请检查表单填写是否正确', 'danger');
            }
        });
        
        // 实时验证JSON格式
        $('#variables').on('blur', function() {
            let value = $(this).val().trim();
            if (value !== '') {
                try {
                    JSON.parse(value);
                    $(this).removeClass('is-invalid').addClass('is-valid');
                } catch (e) {
                    $(this).removeClass('is-valid').addClass('is-invalid');
                    showAlert('变量定义不是有效的JSON格式', 'warning');
                }
            }
        });
    }
    
    // 高亮显示提示词模板中的变量
    if ($('.template-content').length) {
        $('.template-content').each(function() {
            let content = $(this).html();
            content = content.replace(/\{([^}]+)\}/g, '<span class="variable-highlight">{$1}</span>');
            $(this).html(content);
        });
    }
    
    // 确认删除
    $('.delete-confirm').on('click', function(e) {
        if (!confirm('确定要删除吗？此操作不可撤销。')) {
            e.preventDefault();
        }
    });
    
    // 自动隐藏提示消息
    setTimeout(function() {
        $('.alert-dismissible').alert('close');
    }, 5000);
});

/**
 * 显示提示消息
 * @param {string} message - 消息内容
 * @param {string} type - 消息类型 (success, info, warning, danger)
 */
function showAlert(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
        </div>
    `;
    
    $('#alertContainer').html(alertHtml);
    
    // 5秒后自动隐藏
    setTimeout(function() {
        $('.alert-dismissible').alert('close');
    }, 5000);
} 