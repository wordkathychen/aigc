import sqlite3
from typing import Optional, Dict, Any, Tuple
import hashlib
import logging
import os
import sys
from datetime import datetime
from .exceptions import DatabaseError
from .logger import setup_logger

logger = setup_logger(__name__)

def get_app_path() -> str:
    """获取应用程序根目录路径，兼容PyInstaller打包"""
    if getattr(sys, 'frozen', False):
        # 如果是PyInstaller打包的应用
        return os.path.dirname(sys.executable)
    else:
        # 如果是直接运行的脚本
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Database:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # 使用应用程序根目录下的data文件夹
            app_path = get_app_path()
            data_dir = os.path.join(app_path, "data")
            os.makedirs(data_dir, exist_ok=True)
            self.db_path = os.path.join(data_dir, "user_data.db")
        else:
            self.db_path = db_path
            
        logger.info(f"使用数据库路径: {self.db_path}")
        self.init_database()
        
    def init_database(self):
        """初始化数据库表"""
        try:
            # 确保数据库目录存在
            db_dir = os.path.dirname(self.db_path)
            if not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
                
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 创建用户表
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    email TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    status INTEGER DEFAULT 1
                )
                """)
                
                # 创建用户配置表
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_settings (
                    user_id INTEGER PRIMARY KEY,
                    theme TEXT DEFAULT 'dark',
                    font_size INTEGER DEFAULT 12,
                    language TEXT DEFAULT 'zh-CN',
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
                """)
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"数据库初始化失败: {str(e)}")
            raise DatabaseError(f"无法初始化数据库: {str(e)}")
    
    def add_user(self, username: str, password: str, email: Optional[str] = None) -> int:
        """添加新用户"""
        try:
            hashed_password = self._hash_password(password)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                    (username, hashed_password, email)
                )
                user_id = cursor.lastrowid
                
                # 创建用户默认设置
                cursor.execute(
                    "INSERT INTO user_settings (user_id) VALUES (?)",
                    (user_id,)
                )
                
                conn.commit()
                return user_id
                
        except sqlite3.IntegrityError:
            raise DatabaseError("用户名或邮箱已存在")
        except Exception as e:
            logger.error(f"添加用户失败: {str(e)}")
            raise DatabaseError(f"无法添加用户: {str(e)}")
    
    def verify_user(self, username: str, password: str) -> Tuple[bool, Optional[Dict]]:
        """验证用户身份"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, password, email, status FROM users WHERE username = ?",
                    (username,)
                )
                result = cursor.fetchone()
                
                if not result:
                    return False, None
                    
                user_id, stored_password, email, status = result
                
                if status != 1:
                    raise DatabaseError("账号已被禁用")
                
                if self._verify_password(password, stored_password):
                    # 更新最后登录时间
                    cursor.execute(
                        "UPDATE users SET last_login = ? WHERE id = ?",
                        (datetime.now(), user_id)
                    )
                    conn.commit()
                    
                    return True, {
                        "id": user_id,
                        "username": username,
                        "email": email
                    }
                
                return False, None
                
        except Exception as e:
            logger.error(f"验证用户失败: {str(e)}")
            raise DatabaseError(f"无法验证用户: {str(e)}")
    
    def get_user_settings(self, user_id: int) -> Dict[str, Any]:
        """获取用户设置"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT theme, font_size, language FROM user_settings WHERE user_id = ?",
                    (user_id,)
                )
                result = cursor.fetchone()
                
                if result:
                    return {
                        "theme": result[0],
                        "font_size": result[1],
                        "language": result[2]
                    }
                return {}
                
        except Exception as e:
            logger.error(f"获取用户设置失败: {str(e)}")
            raise DatabaseError(f"无法获取用户设置: {str(e)}")
    
    def update_user_settings(self, user_id: int, settings: Dict[str, Any]) -> None:
        """更新用户设置"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                updates = []
                values = []
                for key, value in settings.items():
                    updates.append(f"{key} = ?")
                    values.append(value)
                values.append(user_id)
                
                query = f"UPDATE user_settings SET {', '.join(updates)} WHERE user_id = ?"
                cursor.execute(query, values)
                conn.commit()
                
        except Exception as e:
            logger.error(f"更新用户设置失败: {str(e)}")
            raise DatabaseError(f"无法更新用户设置: {str(e)}")
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def _verify_password(password: str, hashed: str) -> bool:
        """验证密码"""
        return hashlib.sha256(password.encode()).hexdigest() == hashed