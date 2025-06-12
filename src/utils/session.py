from typing import Optional, Dict
from datetime import datetime, timedelta
import jwt
from .exceptions import AuthenticationError
from config.settings import JWT_SECRET_KEY, JWT_EXPIRATION_HOURS

class SessionManager:
    def __init__(self):
        self.current_user: Optional[Dict] = None
        
    def create_token(self, user_data: Dict) -> str:
        """创建JWT令牌"""
        try:
            payload = {
                'user_id': user_data['id'],
                'username': user_data['username'],
                'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
            }
            return jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
        except Exception as e:
            raise AuthenticationError(f"创建令牌失败: {str(e)}")
    
    def verify_token(self, token: str) -> Dict:
        """验证JWT令牌"""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("会话已过期，请重新登录")
        except jwt.InvalidTokenError:
            raise AuthenticationError("无效的认证令牌")
    
    def set_current_user(self, user_data: Dict):
        """设置当前用户"""
        self.current_user = user_data
    
    def get_current_user(self) -> Optional[Dict]:
        """获取当前用户"""
        return self.current_user
    
    def clear_session(self):
        """清除会话"""
        self.current_user = None