"""
异常处理模块
定义系统中使用的各种异常类型
"""

class BaseError(Exception):
    """基础异常类"""
    def __init__(self, message="发生错误"):
        self.message = message
        super().__init__(self.message)


class ValidationError(BaseError):
    """输入验证错误"""
    def __init__(self, message="输入验证失败"):
        super().__init__(message)


class AuthenticationError(BaseError):
    """认证错误"""
    def __init__(self, message="认证失败"):
        super().__init__(message)


class AuthorizationError(BaseError):
    """授权错误"""
    def __init__(self, message="没有权限执行此操作"):
        super().__init__(message)


class APIError(BaseError):
    """API调用错误"""
    def __init__(self, message="API调用失败", status_code=None):
        self.status_code = status_code
        super().__init__(message)


class GenerationError(BaseError):
    """内容生成错误"""
    def __init__(self, message="内容生成失败"):
        super().__init__(message)


class ResourceError(BaseError):
    """资源错误"""
    def __init__(self, message="资源访问失败"):
        super().__init__(message)


class ConfigError(BaseError):
    """配置错误"""
    def __init__(self, message="配置错误"):
        super().__init__(message)


class DatabaseError(BaseError):
    """数据库错误"""
    def __init__(self, message="数据库操作失败"):
        super().__init__(message)


class TimeoutError(BaseError):
    """超时错误"""
    def __init__(self, message="操作超时"):
        super().__init__(message)


class ResourceNotFoundError(BaseError):
    """资源未找到错误"""
    def __init__(self, message: str = "请求的资源不存在", details: dict = None):
        super().__init__(message)


class NetworkError(BaseError):
    """网络连接错误"""
    def __init__(self, message: str = "网络连接失败", details: dict = None):
        super().__init__(message)


class FileOperationError(BaseError):
    """文件操作错误"""
    def __init__(self, message: str = "文件操作失败", details: dict = None):
        super().__init__(message)


class QuotaExceededError(BaseError):
    """额度超限错误"""
    def __init__(self, message: str = "使用额度已超限", details: dict = None):
        super().__init__(message)


def format_exception(exception: Exception) -> dict:
    """格式化异常，转换为用户友好的错误信息
    
    Args:
        exception: 捕获的异常
        
    Returns:
        格式化后的错误信息字典
    """
    # 如果是自定义异常，直接使用其to_dict方法
    if isinstance(exception, BaseError):
        return exception.to_dict()
    
    # 转换常见的Python内置异常
    if isinstance(exception, ValueError):
        return ValidationError(str(exception))
    elif isinstance(exception, FileNotFoundError):
        return ResourceNotFoundError(str(exception))
    elif isinstance(exception, PermissionError):
        return AuthorizationError(str(exception))
    elif isinstance(exception, ConnectionError):
        return NetworkError(str(exception))
    
    # 其他未知异常，作为通用系统错误处理
    return BaseError(str(exception))

def validate_response(response):
    """验证API响应"""
    try:
        # 验证响应状态码
        if not response.ok:
            raise APIError(f"API请求失败: {response.status_code}")
        
        # 解析并验证响应数据
        data = response.json()
        if not data:
            raise ValidationError("API返回空数据")
        
        return data
        
    except ValidationError as e:
        # 处理数据验证错误
        raise ValidationError(f"数据验证失败: {str(e)}")
    
    except Exception as e:
        # 处理其他所有错误
        raise APIError(f"API调用出错: {str(e)}")