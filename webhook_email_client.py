"""
WebhookEmailClient - 通过本地 HTTP 服务接收邮件
配合 email_receiver.py 使用
"""

import requests
import time
from typing import Optional


class WebhookEmailClient:
    """Webhook 邮件客户端 - 从本地服务器读取邮件"""

    def __init__(self, config):
        self.api_url = config.get('api_url', 'http://localhost:5000').rstrip('/')
        self.email_address = config.get('email_address', '')

    def connect(self):
        """测试连接"""
        try:
            resp = requests.get(f'{self.api_url}/status', timeout=5)
            return resp.status_code == 200
        except Exception as e:
            print(f"[Webhook] 连接失败: {e}")
            print(f"[Webhook] 请确保 email_receiver.py 正在运行")
            return False

    def get_latest_emails(self, folder='INBOX', count=5):
        """获取最新邮件"""
        try:
            resp = requests.get(f'{self.api_url}/emails?limit={count}', timeout=10)
            
            if resp.status_code != 200:
                return []

            data = resp.json()
            emails_data = data.get('emails', [])
            
            emails = []
            for item in emails_data:
                # 只返回发送给目标邮箱的邮件
                if self.email_address and item.get('to') != self.email_address:
                    continue
                
                emails.append({
                    'subject': item.get('subject', ''),
                    'content': item.get('html', '') or item.get('text', '')
                })
            
            return emails
            
        except Exception as e:
            print(f"[Webhook] 获取邮件失败: {e}")
            return []
    
    def get_verification_link(self, timeout=60):
        """直接获取验证链接（推荐使用）"""
        try:
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                resp = requests.get(
                    f'{self.api_url}/links',
                    params={'email': self.email_address} if self.email_address else {},
                    timeout=5
                )
                
                if resp.status_code == 200:
                    data = resp.json()
                    
                    if isinstance(data, dict):
                        # 单个邮箱查询
                        if 'link' in data:
                            link = data['link']
                            token = data.get('token')
                            # 获取后清理该链接，避免下次重复使用
                            self._clear_link(self.email_address)
                            return link, token
                        
                        # 多个邮箱，查找最新的
                        if self.email_address and self.email_address in data:
                            link_data = data[self.email_address]
                            link = link_data['link']
                            token = link_data.get('token')
                            # 获取后清理该链接
                            self._clear_link(self.email_address)
                            return link, token
                
                time.sleep(2)
            
            return None, None
            
        except Exception as e:
            print(f"[Webhook] 获取验证链接失败: {e}")
            return None, None
    
    def _clear_link(self, email):
        """清理已使用的链接（避免重复使用）"""
        try:
            requests.post(
                f'{self.api_url}/clear_link',
                json={'email': email},
                timeout=5
            )
        except:
            pass

    def close(self):
        """关闭连接（Webhook 无需关闭）"""
        pass
