from typing import Dict, Optional
from datetime import datetime, timedelta
import jwt
from config.settings import LICENSE_TYPES
from utils.exceptions import LicenseError
from utils.logger import setup_logger

logger = setup_logger(__name__)

class LicenseManager:
    def __init__(self):
        self.licenses = {}
        
    def create_license(self, 
                      license_key: str,
                      license_type: str,
                      limit: int = None,
                      duration: timedelta = None) -> str:
        """创建新的许可证"""
        if license_type not in LICENSE_TYPES:
            raise LicenseError(f"不支持的许可证类型: {license_type}")
            
        license_data = {
            'key': license_key,
            'type': license_type,
            'created_at': datetime.utcnow(),
            'status': 'active'
        }
        
        if license_type == 'count_limited':
            license_data['limit'] = limit
            license_data['used'] = 0
        else:  # time_limited
            license_data['expires_at'] = datetime.utcnow() + duration
            
        self.licenses[license_key] = license_data
        return license_key
        
    def verify_license(self, license_key: str) -> bool:
        """验证许可证"""
        if license_key not in self.licenses:
            return False
            
        license_data = self.licenses[license_key]
        
        # 检查状态
        if license_data['status'] != 'active':
            return False
            
        # 根据类型验证
        if license_data['type'] == 'count_limited':
            return license_data['used'] < license_data['limit']
        else:  # time_limited
            return datetime.utcnow() < license_data['expires_at']
            
    def use_license(self, license_key: str) -> None:
        """使用许可证一次"""
        if not self.verify_license(license_key):
            raise LicenseError("许可证无效或已过期")
            
        license_data = self.licenses[license_key]
        
        if license_data['type'] == 'count_limited':
            license_data['used'] += 1
            
            # 如果达到使用限制，设置为失效
            if license_data['used'] >= license_data['limit']:
                license_data['status'] = 'expired'