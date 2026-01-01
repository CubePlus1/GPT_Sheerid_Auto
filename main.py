"""
SheerID Verification Tool
开源版本 - 支持 ChatGPT Plus 身份验证

作者：dy安心大油条
GitHub: https://github.com/

使用前请阅读 README.md
"""

import json
import random
import time
import re
import os
import hashlib
import imaplib
import email
from email.header import decode_header
from dataclasses import dataclass
from pathlib import Path

try:
    import requests_go
    from requests_go import tls_config as tls_config_module
    HAS_REQUESTS_GO = True
except ImportError:
    import requests
    HAS_REQUESTS_GO = False
    print("[警告] 未安装 requests-go，将使用普通 requests（无 TLS 指纹模拟）")

# 导入 WebhookEmailClient
from webhook_email_client import WebhookEmailClient

# 配置文件路径
BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / 'config.json'
DATA_FILE = BASE_DIR / 'data.txt'
RESULT_FILE = BASE_DIR / 'result.txt'
PROXY_FILE = BASE_DIR / 'proxy.txt'
TLS_JSON_DIR = BASE_DIR / 'tls_json'
USED_FILE = BASE_DIR / 'used.txt'

DEFAULT_PROGRAM_ID = '690415d58971e73ca187d8c9'
DEFAULT_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'

# Branch 映射
BRANCH_ORG_MAP = {
    'Army': {'id': 4070, 'name': 'Army'},
    'Air Force': {'id': 4073, 'name': 'Air Force'},
    'Navy': {'id': 4072, 'name': 'Navy'},
    'Marine Corps': {'id': 4071, 'name': 'Marine Corps'},
    'Coast Guard': {'id': 4074, 'name': 'Coast Guard'},
    'Space Force': {'id': 4544268, 'name': 'Space Force'},
    'Army National Guard': {'id': 4075, 'name': 'Army National Guard'},
    'Army Reserve': {'id': 4076, 'name': 'Army Reserve'},
    'Air National Guard': {'id': 4079, 'name': 'Air National Guard'},
    'Air Force Reserve': {'id': 4080, 'name': 'Air Force Reserve'},
    'Navy Reserve': {'id': 4078, 'name': 'Navy Reserve'},
    'Marine Corps Forces Reserve': {'id': 4077, 'name': 'Marine Corps Forces Reserve'},
    'Coast Guard Reserve': {'id': 4081, 'name': 'Coast Guard Reserve'}
}


@dataclass(frozen=True)
class TlsProfile:
    file: Path
    user_agent: str
    tls_config: object


class EmailClient:
    """邮箱客户端 - 支持 IMAP"""

    def __init__(self, config):
        self.imap_server = config.get('imap_server', '')
        self.imap_port = config.get('imap_port', 993)
        self.email_address = config.get('email_address', '')
        self.email_password = config.get('email_password', '')
        self.use_ssl = config.get('use_ssl', True)
        self.conn = None

    def connect(self):
        """连接邮箱服务器"""
        try:
            if self.use_ssl:
                self.conn = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            else:
                self.conn = imaplib.IMAP4(self.imap_server, self.imap_port)
            self.conn.login(self.email_address, self.email_password)
            return True
        except Exception as e:
            print(f"[邮箱] 连接失败: {e}")
            return False

    def get_latest_emails(self, folder='INBOX', count=5):
        """获取最新邮件"""
        if not self.conn:
            if not self.connect():
                return []

        try:
            self.conn.select(folder)
            _, messages = self.conn.search(None, 'ALL')
            email_ids = messages[0].split()

            if not email_ids:
                return []

            # 获取最新的几封
            latest_ids = email_ids[-count:] if len(email_ids) >= count else email_ids
            latest_ids = latest_ids[::-1]  # 倒序，最新的在前

            emails = []
            for email_id in latest_ids:
                _, msg_data = self.conn.fetch(email_id, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject = self._decode_header(msg['Subject'])
                        content = self._get_email_content(msg)
                        emails.append({
                            'subject': subject,
                            'content': content
                        })
            return emails
        except Exception as e:
            print(f"[邮箱] 获取邮件失败: {e}")
            # 尝试重连
            self.conn = None
            return []

    def _decode_header(self, header):
        """解码邮件头"""
        if not header:
            return ''
        decoded = decode_header(header)
        result = ''
        for content, charset in decoded:
            if isinstance(content, bytes):
                result += content.decode(charset or 'utf-8', errors='ignore')
            else:
                result += content
        return result

    def _get_email_content(self, msg):
        """获取邮件内容"""
        content = ''
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/html':
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or 'utf-8'
                        content = payload.decode(charset, errors='ignore')
                        break
                elif content_type == 'text/plain' and not content:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or 'utf-8'
                        content = payload.decode(charset, errors='ignore')
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or 'utf-8'
                content = payload.decode(charset, errors='ignore')
        return content

    def close(self):
        """关闭连接"""
        if self.conn:
            try:
                self.conn.logout()
            except:
                pass
            self.conn = None


class CloudMailClient:
    """CloudMail API 客户端 - 支持 CloudMail 临时邮箱服务"""

    def __init__(self, config):
        self.api_url = config.get('api_url', '')
        self.admin_email = config.get('admin_email', '')
        self.admin_password = config.get('admin_password', '')
        self.email_address = config.get('email_address', '')
        self.token = None

    def connect(self):
        """获取 API Token"""
        try:
            import requests
            resp = requests.post(f'{self.api_url}/api/public/genToken', json={
                'email': self.admin_email,
                'password': self.admin_password
            }, timeout=10)
            data = resp.json()
            if data.get('code') == 200 and data.get('data', {}).get('token'):
                self.token = data['data']['token']
                # 确保邮箱用户存在
                self._ensure_user()
                return True
            else:
                print(f"[CloudMail] 获取 Token 失败: {data.get('message', '未知错误')}")
                return False
        except Exception as e:
            print(f"[CloudMail] 连接失败: {e}")
            return False

    def _ensure_user(self):
        """确保邮箱用户存在"""
        try:
            import requests
            requests.post(f'{self.api_url}/api/public/addUser',
                headers={'Authorization': self.token},
                json={'list': [{'email': self.email_address}]},
                timeout=10
            )
        except:
            pass

    def get_latest_emails(self, folder='INBOX', count=5):
        """获取最新邮件"""
        if not self.token:
            if not self.connect():
                return []

        try:
            import requests
            resp = requests.post(f'{self.api_url}/api/public/emailList',
                headers={'Authorization': self.token},
                json={
                    'toEmail': self.email_address,
                    'type': 0,
                    'isDel': 0,
                    'num': 1,
                    'size': count,
                    'timeSort': 'desc'
                },
                timeout=10
            )
            data = resp.json()
            if data.get('code') == 200 and data.get('data'):
                emails = []
                for item in data['data']:
                    emails.append({
                        'subject': item.get('subject', ''),
                        'content': item.get('content', '') or item.get('text', '')
                    })
                return emails
            return []
        except Exception as e:
            print(f"[CloudMail] 获取邮件失败: {e}")
            return []

    def close(self):
        """关闭连接（CloudMail 无需关闭）"""
        pass


class MailpitClient:
    """Mailpit API 客户端 - 支持本地 Mailpit 邮件测试服务"""

    def __init__(self, config):
        self.api_url = config.get('api_url', 'http://localhost:8025').rstrip('/')
        self.email_address = config.get('email_address', '')

    def connect(self):
        """测试连接"""
        try:
            import requests
            resp = requests.get(f'{self.api_url}/api/v1/messages', timeout=5)
            return resp.status_code == 200
        except Exception as e:
            print(f"[Mailpit] 连接失败: {e}")
            return False

    def get_latest_emails(self, folder='INBOX', count=5):
        """获取最新邮件"""
        try:
            import requests
            resp = requests.get(f'{self.api_url}/api/v1/messages', timeout=10)
            
            if resp.status_code != 200:
                return []

            data = resp.json()
            messages = data.get('messages', [])
            
            if not messages:
                return []

            emails = []
            # 按时间倒序处理最新邮件
            for message in sorted(messages, key=lambda x: x.get('Created', ''), reverse=True)[:count]:
                # 检查是否发送给目标邮箱
                to_emails = [addr.get('Address', '') for addr in message.get('To', [])]
                
                # 如果指定了邮箱地址，检查收件人
                if self.email_address and self.email_address not in to_emails:
                    continue
                
                # 获取邮件详情
                msg_id = message.get('ID')
                detail_resp = requests.get(f'{self.api_url}/api/v1/message/{msg_id}', timeout=10)
                
                if detail_resp.status_code != 200:
                    continue
                
                detail = detail_resp.json()
                subject = detail.get('Subject', '')
                
                # 优先使用 HTML，其次使用 Text
                content = detail.get('HTML', '') or detail.get('Text', '')
                
                emails.append({
                    'subject': subject,
                    'content': content
                })
            
            return emails
            
        except Exception as e:
            print(f"[Mailpit] 获取邮件失败: {e}")
            return []

    def close(self):
        """关闭连接（Mailpit 无需关闭）"""
        pass


def _extract_chrome_version(user_agent):
    """从 UA 中提取 Chrome 版本号"""
    match = re.search(r'Chrome/(\d+)', user_agent)
    return match.group(1) if match else '131'


def generate_fingerprint():
    """生成设备指纹"""
    import uuid
    screen = random.choice(['1920x1080', '2560x1440', '1366x768', '1536x864', '1440x900'])
    timezone = random.choice(['-480', '-420', '-360', '-300', '-240', '0', '60', '120'])
    plugins = random.randint(3, 8)
    canvas = str(uuid.uuid4())
    webgl = random.choice(['ANGLE (Intel', 'ANGLE (NVIDIA', 'ANGLE (AMD'])
    raw = f"{screen}|{timezone}|{plugins}|{canvas}|{webgl}|{random.random()}"
    return hashlib.md5(raw.encode()).hexdigest()


def generate_newrelic_headers():
    """生成 NewRelic 追踪头"""
    import base64
    import uuid

    trace_id = uuid.uuid4().hex + uuid.uuid4().hex[:8]
    trace_id = trace_id[:32]
    span_id = uuid.uuid4().hex[:16]
    timestamp = int(time.time() * 1000)

    nr_payload = {
        "v": [0, 1],
        "d": {
            "ty": "Browser",
            "ac": "364029",
            "ap": "134291347",
            "id": span_id,
            "tr": trace_id,
            "ti": timestamp
        }
    }

    newrelic = base64.b64encode(json.dumps(nr_payload).encode()).decode()
    traceparent = f"00-{trace_id}-{span_id}-01"
    tracestate = f"364029@nr=0-1-364029-134291347-{span_id}----{timestamp}"

    return {
        'newrelic': newrelic,
        'traceparent': traceparent,
        'tracestate': tracestate
    }


def match_branch(input_str):
    """匹配 branch"""
    normalized = input_str.upper().replace('US ', '').strip()

    for branch in BRANCH_ORG_MAP:
        if branch.upper() == normalized:
            return branch

    if 'MARINE' in normalized and 'RESERVE' not in normalized:
        return 'Marine Corps'
    if 'ARMY' in normalized and 'NATIONAL' in normalized:
        return 'Army National Guard'
    if 'ARMY' in normalized and 'RESERVE' in normalized:
        return 'Army Reserve'
    if 'ARMY' in normalized:
        return 'Army'
    if 'NAVY' in normalized and 'RESERVE' in normalized:
        return 'Navy Reserve'
    if 'NAVY' in normalized:
        return 'Navy'
    if 'AIR' in normalized and 'NATIONAL' in normalized:
        return 'Air National Guard'
    if 'AIR' in normalized and 'RESERVE' in normalized:
        return 'Air Force Reserve'
    if 'AIR' in normalized and 'FORCE' in normalized:
        return 'Air Force'
    if 'COAST' in normalized and 'RESERVE' in normalized:
        return 'Coast Guard Reserve'
    if 'COAST' in normalized:
        return 'Coast Guard'
    if 'SPACE' in normalized:
        return 'Space Force'

    return 'Army'


def load_random_proxy(proxy_file):
    """随机选择一个代理"""
    if not proxy_file.exists():
        print(f"[代理] proxy.txt 不存在，将使用直连")
        return None
    
    try:
        lines = [l.strip() for l in proxy_file.read_text(encoding='utf-8').split('\n') if l.strip() and not l.startswith('#')]
    except Exception as e:
        print(f"[代理] 读取 proxy.txt 失败: {e}")
        return None
    
    if not lines:
        print(f"[代理] proxy.txt 为空，将使用直连")
        return None
    
    line = random.choice(lines)

    # 支持多种格式
    # 格式1: ip:port:user:pass
    # 格式2: ip:port
    # 格式3: socks5://user:pass@ip:port
    # 格式4: http://ip:port 或 https://ip:port
    if line.startswith(('socks5://', 'http://', 'https://')):
        print(f"[代理] 使用代理: {line.split('@')[-1] if '@' in line else line.split('//')[1]}")
        return {'url': line}

    parts = line.split(':')
    if len(parts) == 4:
        print(f"[代理] 使用代理: {parts[0]}:{parts[1]} (认证)")
        return {'ip': parts[0], 'port': parts[1], 'user': parts[2], 'pass': parts[3]}
    elif len(parts) == 2:
        print(f"[代理] 使用代理: {parts[0]}:{parts[1]}")
        return {'ip': parts[0], 'port': parts[1], 'user': None, 'pass': None}
    
    print(f"[代理] 格式错误: {line}")
    return None


def get_proxy_dict(proxy):
    """获取代理字典"""
    if not proxy:
        return None

    if 'url' in proxy:
        return {'http': proxy['url'], 'https': proxy['url']}

    if proxy.get('user') and proxy.get('pass'):
        # 有认证信息，默认使用 SOCKS5
        proxy_url = f"socks5://{proxy['user']}:{proxy['pass']}@{proxy['ip']}:{proxy['port']}"
    else:
        # 无认证，使用 HTTP 代理
        proxy_url = f"http://{proxy['ip']}:{proxy['port']}"
    return {'http': proxy_url, 'https': proxy_url}


def _parse_tls_json_to_config(data: dict):
    """解析 tls_json 格式为 TLSConfig"""
    if not HAS_REQUESTS_GO:
        return None

    tls_data = data.get('tls', {})
    http2_data = data.get('http2', {})

    config = tls_config_module.TLSConfig()

    ja3 = tls_data.get('ja3', '')
    if ja3:
        config.ja3_string = ja3

    if http2_data:
        akamai_fp = http2_data.get('akamai_fingerprint', '')
        if akamai_fp:
            parts = akamai_fp.split('|')
            if len(parts) >= 4:
                settings_str = parts[0]
                h2_settings = {}
                h2_settings_order = []
                for item in settings_str.split(';'):
                    if ':' in item:
                        k, v = item.split(':')
                        k, v = int(k), int(v)
                        h2_settings[k] = v
                        h2_settings_order.append(k)

                if h2_settings:
                    config.h2_settings = h2_settings
                    config.h2_settings_order = h2_settings_order

                if parts[1]:
                    try:
                        config.connection_flow = int(parts[1])
                    except:
                        pass

                if len(parts) > 3 and parts[3]:
                    pseudo_map = {'m': ':method', 'a': ':authority', 's': ':scheme', 'p': ':path'}
                    pseudo_order = [pseudo_map.get(c, c) for c in parts[3].split(',')]
                    config.pseudo_header_order = pseudo_order

    return config


def _extract_user_agent(data: dict):
    """从 TLS JSON 中提取 UA"""
    ua = data.get("user_agent")
    if isinstance(ua, str) and ua.strip():
        return ua.strip()

    http1 = data.get("http1") if isinstance(data.get("http1"), dict) else None
    headers = http1.get("headers") if http1 and isinstance(http1.get("headers"), list) else []
    for line in headers:
        if isinstance(line, str) and line.lower().startswith("user-agent:"):
            return line.split(":", 1)[1].strip() or None

    return None


def load_random_tls_profile(ua_keywords=None):
    """从 tls_json 目录随机选择 TLS 指纹"""
    if not HAS_REQUESTS_GO:
        return None
    if not TLS_JSON_DIR.exists():
        return None

    json_files = list(TLS_JSON_DIR.glob("*.json"))
    if not json_files:
        return None

    random.shuffle(json_files)

    for selected_file in json_files:
        try:
            data = json.loads(selected_file.read_text(encoding="utf-8"))
        except:
            continue

        ua = _extract_user_agent(data)
        if not ua:
            continue
        if ua_keywords and not all(k in ua for k in ua_keywords):
            continue

        try:
            tls_conf = _parse_tls_json_to_config(data)
            if tls_conf:
                tls_conf.user_agent = ua
                return TlsProfile(file=selected_file, user_agent=ua, tls_config=tls_conf)
        except:
            continue

    return None


def create_session(proxy_dict, tls_profile):
    """创建 HTTP 会话"""
    if HAS_REQUESTS_GO:
        session = requests_go.Session()
        if tls_profile and tls_profile.tls_config:
            session.tls_config = tls_profile.tls_config
    else:
        session = requests.Session()

    if proxy_dict:
        session.proxies = proxy_dict

    return session


def sanitize_headers(headers):
    """清理 headers，确保所有值都是 ASCII 兼容的"""
    sanitized = {}
    for key, value in headers.items():
        if isinstance(value, str):
            # 尝试编码为 ASCII，如果失败则使用 latin-1
            try:
                # 先尝试 ASCII
                value.encode('ascii')
            except UnicodeEncodeError:
                # 如果包含非 ASCII 字符，尝试 latin-1
                try:
                    value.encode('latin-1')
                except UnicodeEncodeError:
                    # 如果 latin-1 也不行，使用 utf-8 再转为 latin-1
                    value = value.encode('utf-8').decode('utf-8', errors='ignore')
        sanitized[key] = value
    return sanitized


def extract_verification_link(content):
    """从邮件内容提取验证链接"""
    import html
    
    # 尝试从 href 属性提取
    match = re.search(r'href="(https://services\.sheerid\.com/verify/[^"]+emailToken=[^"]+)"', content)
    if match:
        link = match.group(1)
        # 解码 HTML 实体 (&amp; -> &, &quot; -> ", etc.)
        link = html.unescape(link)
        return link

    # 尝试直接匹配 URL
    match = re.search(r'https://services\.sheerid\.com/verify/[^\s<>"]+emailToken=\d+', content)
    if match:
        link = match.group(0)
        # 解码 HTML 实体
        link = html.unescape(link)
        return link

    return None


def extract_email_token(url):
    """从验证链接提取 emailToken"""
    match = re.search(r'emailToken=(\d+)', url)
    return match.group(1) if match else None


def is_verification_email(content):
    """判断是否是验证邮件"""
    return "You're almost there" in content or "Finish Verifying" in content


def create_verification(session, access_token, program_id, context, user_agent):
    """创建 verification"""
    chrome_ver = _extract_chrome_version(user_agent)
    headers = {
        'host': 'chatgpt.com',
        'sec-ch-ua': f'"Chromium";v="{chrome_ver}", "Google Chrome";v="{chrome_ver}", "Not_A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'user-agent': user_agent,
        'accept': '*/*',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9',
        'authorization': f'Bearer {access_token}',
        'content-type': 'application/json',
        'origin': 'https://chatgpt.com',
        'referer': 'https://chatgpt.com/veterans-claim',
        'oai-device-id': context['device_id'],
        'oai-language': 'en-US',
    }

    resp = session.post(
        'https://chatgpt.com/backend-api/veterans/create_verification',
        headers=sanitize_headers(headers),
        json={'program_id': program_id}
    )

    if resp.status_code != 200:
        print(f"    -> 创建验证失败: status={resp.status_code}, response={resp.text[:200]}")
        raise Exception(f"创建 verification 失败: {resp.status_code}")
    
    result = resp.json()
    verification_id = result.get('verification_id')
    
    # 检查是否返回了新的 ID
    if not verification_id:
        print(f"    -> 警告: 未获取到 verificationId")
        print(f"    -> 响应内容: {result}")
        raise Exception("未获取到 verification_id")
    
    print(f"    -> 创建成功: verificationId={verification_id}")
    print(f"    -> 验证 URL: https://services.sheerid.com/verify/{program_id}/?verificationId={verification_id}")
    
    # 输出完整响应供调试
    if 'error' in result or 'message' in result:
        print(f"    -> API 响应: {result}")
    
    return verification_id


def get_verification_status(session, verification_id, program_id, user_agent):
    """获取验证当前状态"""
    chrome_ver = _extract_chrome_version(user_agent)
    nr_headers = generate_newrelic_headers()
    referer_url = f'https://services.sheerid.com/verify/{program_id}/?verificationId={verification_id}'

    headers = {
        'host': 'services.sheerid.com',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua': f'"Chromium";v="{chrome_ver}", "Google Chrome";v="{chrome_ver}", "Not_A Brand";v="99"',
        'clientversion': '2.157.0',
        'newrelic': nr_headers['newrelic'],
        'sec-ch-ua-mobile': '?0',
        'traceparent': nr_headers['traceparent'],
        'clientname': 'jslib',
        'user-agent': user_agent,
        'accept': 'application/json',
        'tracestate': nr_headers['tracestate'],
        'origin': 'https://services.sheerid.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': referer_url,
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en-GB;q=0.9,en;q=0.8',
        'priority': 'u=1, i',
    }

    resp = session.get(
        f'https://services.sheerid.com/rest/v2/verification/{verification_id}',
        headers=sanitize_headers(headers)
    )

    if resp.status_code == 200:
        data = resp.json()
        current_step = data.get('currentStep', 'unknown')
        current_state = data.get('currentState', 'unknown')
        print(f"    -> 当前状态: currentStep={current_step}, currentState={current_state}")
        return data
    else:
        print(f"    -> 获取状态失败: status={resp.status_code}")
        return None


def get_verification_status(session, verification_id, program_id, user_agent):
    """获取当前验证状态"""
    chrome_ver = _extract_chrome_version(user_agent)
    nr_headers = generate_newrelic_headers()

    headers = {
        'host': 'services.sheerid.com',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua': f'"Chromium";v="{chrome_ver}", "Google Chrome";v="{chrome_ver}", "Not_A Brand";v="99"',
        'clientversion': '2.157.0',
        'newrelic': nr_headers['newrelic'],
        'sec-ch-ua-mobile': '?0',
        'traceparent': nr_headers['traceparent'],
        'clientname': 'jslib',
        'user-agent': user_agent,
        'accept': 'application/json',
        'tracestate': nr_headers['tracestate'],
        'origin': 'https://services.sheerid.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': f'https://services.sheerid.com/verify/{program_id}/?verificationId={verification_id}',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en-GB;q=0.9,en;q=0.8',
        'priority': 'u=1, i',
    }

    resp = session.get(
        f'https://services.sheerid.com/rest/v2/verification/{verification_id}',
        headers=sanitize_headers(headers)
    )

    if resp.status_code == 200:
        return resp.json()
    else:
        print(f"    -> 获取状态失败: status={resp.status_code}")
        return None


def submit_military_status(session, verification_id, program_id, user_agent):
    """提交状态"""
    chrome_ver = _extract_chrome_version(user_agent)
    nr_headers = generate_newrelic_headers()

    headers = {
        'host': 'services.sheerid.com',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua': f'"Chromium";v="{chrome_ver}", "Google Chrome";v="{chrome_ver}", "Not_A Brand";v="99"',
        'clientversion': '2.157.0',
        'newrelic': nr_headers['newrelic'],
        'sec-ch-ua-mobile': '?0',
        'traceparent': nr_headers['traceparent'],
        'clientname': 'jslib',
        'user-agent': user_agent,
        'accept': 'application/json',
        'content-type': 'application/json',
        'tracestate': nr_headers['tracestate'],
        'origin': 'https://services.sheerid.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': f'https://services.sheerid.com/verify/{program_id}/?verificationId={verification_id}',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en-GB;q=0.9,en;q=0.8',
        'priority': 'u=1, i',
    }

    resp = session.post(
        f'https://services.sheerid.com/rest/v2/verification/{verification_id}/step/collectMilitaryStatus',
        headers=sanitize_headers(headers),
        json={'status': 'VETERAN'}
    )

    data = resp.json()
    current_step = data.get('currentStep', 'unknown')
    print(f"    -> 状态提交: currentStep={current_step}, status={resp.status_code}")
    
    if resp.status_code != 200:
        print(f"    -> 错误详情: {data}")
        raise Exception(f"提交状态失败: {resp.status_code}")

    return data


def submit_personal_info(session, verification_id, program_id, user_data, user_agent, fingerprint_hash):
    """提交个人信息"""
    referer_url = f'https://services.sheerid.com/verify/{program_id}/?verificationId={verification_id}'
    chrome_ver = _extract_chrome_version(user_agent)
    nr_headers = generate_newrelic_headers()

    headers = {
        'host': 'services.sheerid.com',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua': f'"Chromium";v="{chrome_ver}", "Google Chrome";v="{chrome_ver}", "Not_A Brand";v="99"',
        'clientversion': '2.157.0',
        'newrelic': nr_headers['newrelic'],
        'sec-ch-ua-mobile': '?0',
        'traceparent': nr_headers['traceparent'],
        'clientname': 'jslib',
        'user-agent': user_agent,
        'accept': 'application/json',
        'content-type': 'application/json',
        'tracestate': nr_headers['tracestate'],
        'origin': 'https://services.sheerid.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': referer_url,
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en-GB;q=0.9,en;q=0.8',
        'priority': 'u=1, i',
    }

    flags_json = json.dumps({
        "doc-upload-considerations": "default",
        "doc-upload-may24": "default",
        "doc-upload-redesign-use-legacy-message-keys": False,
        "docUpload-assertion-checklist": "default",
        "include-cvec-field-france-student": "not-labeled-optional",
        "org-search-overlay": "default",
        "org-selected-display": "default"
    })

    payload = {
        'firstName': user_data['firstName'],
        'lastName': user_data['lastName'],
        'birthDate': user_data['birthDate'],
        'email': user_data['email'],
        'phoneNumber': '',
        'organization': user_data['organization'],
        'dischargeDate': user_data.get('dischargeDate', '2025-01-02'),
        'deviceFingerprintHash': fingerprint_hash,
        'locale': 'en-US',
        'country': 'US',
        'metadata': {
            'marketConsentValue': False,
            'refererUrl': referer_url,
            'verificationId': verification_id,
            'flags': flags_json,
            'submissionOptIn': 'By submitting the personal information above, I acknowledge that my personal information is being collected under the <a target="blank" rel="noopener noreferrer" class="sid-privacy-policy sid-link" href="https://openai.com/policies/privacy-policy/">privacy policy</a> of the business from which I am seeking a discount, and I understand that my personal information will be shared with SheerID as a processor/third-party service provider in order for SheerID to confirm my eligibility for a special offer. Contact OpenAI Support for further assistance at support@openai.com'
        }
    }

    resp = session.post(
        f'https://services.sheerid.com/rest/v2/verification/{verification_id}/step/collectInactiveMilitaryPersonalInfo',
        headers=sanitize_headers(headers),
        json=payload
    )

    data = resp.json()
    
    # 打印响应状态供调试
    current_step = data.get('currentStep', 'unknown')
    error_ids = data.get('errorIds', [])
    print(f"    -> 响应: currentStep={current_step}, status={resp.status_code}, errorIds={error_ids}")

    # 只有明确的 verificationLimitExceeded 错误才标记为已验证
    if 'verificationLimitExceeded' in error_ids:
        data['_already_verified'] = True
        print(f"    -> 检测到资料已被验证过")

    if resp.status_code not in [200, 429]:
        raise Exception(f"提交个人信息失败: {resp.status_code}")

    return data


def submit_email_token(session, verification_id, program_id, email_token, user_agent, fingerprint_hash):
    """提交邮件验证 token"""
    chrome_ver = _extract_chrome_version(user_agent)
    nr_headers = generate_newrelic_headers()
    referer_url = f'https://services.sheerid.com/verify/{program_id}/?verificationId={verification_id}&emailToken={email_token}'

    headers = {
        'host': 'services.sheerid.com',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua': f'"Chromium";v="{chrome_ver}", "Google Chrome";v="{chrome_ver}", "Not_A Brand";v="99"',
        'clientversion': '2.157.0',
        'newrelic': nr_headers['newrelic'],
        'sec-ch-ua-mobile': '?0',
        'traceparent': nr_headers['traceparent'],
        'clientname': 'jslib',
        'user-agent': user_agent,
        'accept': 'application/json',
        'content-type': 'application/json',
        'tracestate': nr_headers['tracestate'],
        'origin': 'https://services.sheerid.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': referer_url,
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en-GB;q=0.9,en;q=0.8',
        'priority': 'u=1, i',
    }

    resp = session.post(
        f'https://services.sheerid.com/rest/v2/verification/{verification_id}/step/emailLoop',
        headers=sanitize_headers(headers),
        json={
            'emailToken': email_token,
            'deviceFingerprintHash': fingerprint_hash
        }
    )

    if resp.status_code == 200:
        return resp.json()
    return None


def try_again(session, verification_id, program_id, user_agent, fingerprint_hash):
    """点击 tryAgain 按钮刷新验证状态（当 not approved 时）"""
    chrome_ver = _extract_chrome_version(user_agent)
    nr_headers = generate_newrelic_headers()
    referer_url = f'https://services.sheerid.com/verify/{program_id}/?verificationId={verification_id}'

    headers = {
        'host': 'services.sheerid.com',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua': f'"Chromium";v="{chrome_ver}", "Google Chrome";v="{chrome_ver}", "Not_A Brand";v="99"',
        'clientversion': '2.157.0',
        'newrelic': nr_headers['newrelic'],
        'sec-ch-ua-mobile': '?0',
        'traceparent': nr_headers['traceparent'],
        'clientname': 'jslib',
        'user-agent': user_agent,
        'accept': 'application/json',
        'content-type': 'application/json',
        'tracestate': nr_headers['tracestate'],
        'origin': 'https://services.sheerid.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': referer_url,
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en-GB;q=0.9,en;q=0.8',
        'priority': 'u=1, i',
    }

    resp = session.post(
        f'https://services.sheerid.com/rest/v2/verification/{verification_id}/step/tryAgain',
        headers=sanitize_headers(headers),
        json={'deviceFingerprintHash': fingerprint_hash}
    )

    if resp.status_code == 200:
        data = resp.json()
        current_step = data.get('currentStep', 'unknown')
        current_state = data.get('currentState', 'unknown')
        print(f"    -> tryAgain 响应: currentStep={current_step}, currentState={current_state}")
        return data
    else:
        print(f"    -> tryAgain 失败: status={resp.status_code}")
        return None


def try_again(session, verification_id, program_id, user_agent, fingerprint_hash):
    """点击 tryAgain 按钮刷新验证状态（当 not approved 时）"""
    chrome_ver = _extract_chrome_version(user_agent)
    nr_headers = generate_newrelic_headers()
    referer_url = f'https://services.sheerid.com/verify/{program_id}/?verificationId={verification_id}'

    headers = {
        'host': 'services.sheerid.com',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua': f'"Chromium";v="{chrome_ver}", "Google Chrome";v="{chrome_ver}", "Not_A Brand";v="99"',
        'clientversion': '2.157.0',
        'newrelic': nr_headers['newrelic'],
        'sec-ch-ua-mobile': '?0',
        'traceparent': nr_headers['traceparent'],
        'clientname': 'jslib',
        'user-agent': user_agent,
        'accept': 'application/json',
        'content-type': 'application/json',
        'tracestate': nr_headers['tracestate'],
        'origin': 'https://services.sheerid.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': referer_url,
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en-GB;q=0.9,en;q=0.8',
        'priority': 'u=1, i',
    }

    resp = session.post(
        f'https://services.sheerid.com/rest/v2/verification/{verification_id}/step/tryAgain',
        headers=sanitize_headers(headers),
        json={'deviceFingerprintHash': fingerprint_hash}
    )

    if resp.status_code == 200:
        data = resp.json()
        current_step = data.get('currentStep', 'unknown')
        current_state = data.get('currentState', 'unknown')
        print(f"    -> tryAgain 响应: currentStep={current_step}, currentState={current_state}")
        return data
    else:
        print(f"    -> tryAgain 失败: status={resp.status_code}")
        return None


def verify(access_token, program_id, user_data, email, proxy_dict, tls_profile, email_client):
    """完整验证流程"""
    user_agent = tls_profile.user_agent if tls_profile else DEFAULT_UA
    session = create_session(proxy_dict, tls_profile)

    verification_id = None

    try:
        import uuid
        context = {
            'device_id': str(uuid.uuid4()),
            'client_version': 'prod-a7886199244b6997257a555113ee743fae95138c'
        }

        fingerprint_hash = generate_fingerprint()
        fingerprint_timestamp = int(time.time() * 1000)

        # 创建 verification
        print(f"    -> 创建验证请求...")
        verification_id = create_verification(session, access_token, program_id, context, user_agent)

        # 设置 cookie
        session.cookies.set('sid-verificationId', verification_id, domain='services.sheerid.com')
        session.cookies.set(f'fingerprint_{fingerprint_timestamp}', f'undefined-{fingerprint_timestamp}', domain='services.sheerid.com')

        # 检查初始状态
        print(f"    -> 检查初始状态...")
        status_data = get_verification_status(session, verification_id, program_id, user_agent)
        
        if not status_data:
            # 获取状态失败（可能是 429 或网络问题）
            print(f"    -> 获取状态失败，稍后重试")
            return {'success': False, 'message': '获取状态失败', 'retry': True}
        
        initial_step = status_data.get('currentStep', '')
        initial_state = status_data.get('currentState', '')
        error_ids = status_data.get('errorIds', [])
        
        # 定义预期的表单步骤
        expected_form_steps = ['collectMilitaryStatus', 'collectInactiveMilitaryPersonalInfo', 
                              'collectActiveMilitaryPersonalInfo', 'collectShortPersonalInfo']
        
        # 如果是 error 状态，尝试刷新
        if initial_step == 'error':
                # 可以尝试刷新的错误类型
                refresh_errors = ['notApproved', 'verificationLimitExceeded', 'cantVerify']
                should_try_refresh = any(err in error_ids for err in refresh_errors)
                
                if should_try_refresh:
                    matched_errors = [err for err in refresh_errors if err in error_ids]
                    print(f"    -> 检测到错误状态: {', '.join(matched_errors)}")
                    print(f"    -> 点击 Try Again 按钮刷新...")
                    
                    # 尝试刷新状态
                    refresh_result = try_again(session, verification_id, program_id, user_agent, fingerprint_hash)
                    
                    if refresh_result:
                        refresh_step = refresh_result.get('currentStep', 'error')
                        
                        if refresh_step == 'success':
                            print(f"    -> ✓ 刷新成功，验证已完成")
                            return {'success': True, 'message': '刷新后验证成功'}
                        elif refresh_step in expected_form_steps:
                            print(f"    -> ✓ 刷新成功，继续提交流程")
                            # 不返回，继续后续提交流程
                        else:
                            # 刷新后仍然失败
                            print(f"    -> ✗ 刷新后状态: {refresh_step}")
                            return {'success': False, 'message': f"刷新后验证失败: {', '.join(matched_errors)}", 'skip': True}
                    else:
                        # tryAgain API 失败（404等），说明需要重新创建验证
                        print(f"    -> ✗ Try Again 失败 (404)")
                        print(f"    -> 需要重新创建验证流程")
                        # 返回 retry 标志，让外层重新创建验证
                        return {'success': False, 'message': f"需要重新创建验证", 'retry': True}
                else:
                    # 其他不支持刷新的错误
                    return {'success': False, 'message': f"验证错误: {error_ids}"}
        
        # 如果已经成功了
        if initial_step == 'success':
            return {'success': True, 'message': '验证已完成（无需提交）'}
        
        # 如果状态不是预期的表单步骤，重新创建验证
        if initial_step not in expected_form_steps:
            print(f"    -> 状态异常: {initial_step}")
            print(f"    -> 需要正确的表单页面才能提交")
            print(f"    -> 预期步骤: {', '.join(expected_form_steps)}")
            return {'success': False, 'message': f"状态异常，重新创建验证", 'retry': True}

        # 状态正确，继续提交
        print(f"    -> 状态正确: {initial_step}")
        
        # 提交状态
        print(f"    -> 提交状态...")
        status_result = submit_military_status(session, verification_id, program_id, user_agent)
        status_step = status_result.get('currentStep')
        
        # 检查状态提交后的步骤
        if status_step == 'error':
            error_ids = status_result.get('errorIds', [])
            return {'success': False, 'message': f"状态提交错误: {error_ids}"}
        
        if status_step == 'success':
            return {'success': True, 'message': '验证成功（无需个人信息）'}
        
        # 只有在正确的步骤时才提交个人信息
        expected_steps = ['collectInactiveMilitaryPersonalInfo', 'collectActiveMilitaryPersonalInfo', 'collectShortPersonalInfo']
        if status_step not in expected_steps:
            print(f"    -> 警告: 意外的步骤 '{status_step}'，尝试继续提交个人信息...")

        # 提交个人信息
        print(f"    -> 提交个人信息...")
        user_data['email'] = email
        result = submit_personal_info(session, verification_id, program_id, user_data, user_agent, fingerprint_hash)
        current_step = result.get('currentStep')

        # 优先检查当前步骤，确保 emailLoop 不会被跳过
        if current_step == 'success':
            return {'success': True, 'message': '验证成功'}

        if current_step == 'error':
            error_ids = result.get('errorIds', [])
            return {'success': False, 'message': f"错误: {error_ids}"}

        if current_step == 'docUpload':
            return {'success': False, 'message': '需要上传文档'}

        # emailLoop - 需要邮件验证（优先处理，不受 _already_verified 影响）
        if current_step == 'emailLoop':
            print(f"    -> 等待验证邮件 (verificationId: {verification_id})...")

            verification_link = None
            email_token = None
            
            # 优先使用 WebhookEmailClient 的直接获取链接方法
            if hasattr(email_client, 'get_verification_link'):
                print(f"    -> 使用 Webhook 直接获取验证链接...")
                verification_link, email_token = email_client.get_verification_link(timeout=60)
                
                # 确认链接包含正确的 verificationId
                if verification_link and verification_id not in verification_link:
                    print(f"      警告: 链接的 verificationId 不匹配，继续等待...")
                    verification_link = None
                    email_token = None
            
            # 如果 webhook 方法失败，或使用其他邮箱方式，使用通用方法
            if not verification_link:
                print(f"    -> 使用通用方法获取邮件...")
                for retry in range(20):
                    emails = email_client.get_latest_emails(count=5)

                    for e in emails:
                        content = e.get('content', '')
                        if is_verification_email(content):
                            link = extract_verification_link(content)
                            if link and verification_id in link:
                                verification_link = link
                                break

                    if verification_link:
                        break

                    print(f"      等待中... ({retry+1}/20)")
                    time.sleep(3)

            if not verification_link:
                return {'success': False, 'message': '未收到验证邮件'}

            # 如果还没有 token，从链接提取
            if not email_token:
                email_token = extract_email_token(verification_link)
            
            if not email_token:
                return {'success': False, 'message': '无法提取 emailToken'}

            print(f"    -> 提交邮件验证 (token: {email_token})...")
            result = submit_email_token(session, verification_id, program_id, email_token, user_agent, fingerprint_hash)

            if result:
                current_step = result.get('currentStep')
                current_state = result.get('currentState', '')
                
                # 直接成功
                if current_step == 'success':
                    return {'success': True, 'message': '验证成功'}
                
                # 检查是否需要重试（pending 或 not approved）
                if current_state in ['pending', 'notApproved'] or current_step == 'pending':
                    print(f"    -> 检测到状态: {current_state or current_step}，尝试刷新...")
                    
                    # 重试最多 5 次
                    retry_result = None
                    for retry in range(5):
                        time.sleep(3)  # 等待 3 秒
                        print(f"    -> 刷新状态 ({retry+1}/5)...")
                        
                        retry_result = try_again(session, verification_id, program_id, user_agent, fingerprint_hash)
                        
                        if retry_result:
                            retry_step = retry_result.get('currentStep')
                            retry_state = retry_result.get('currentState', '')
                            
                            if retry_step == 'success':
                                return {'success': True, 'message': '验证成功（刷新后）'}
                            elif retry_state not in ['pending', 'notApproved'] and retry_step != 'pending':
                                # 状态改变了，但不是 success
                                break
                    
                    # 重试后再次检查最终状态
                    if retry_result:
                        if retry_result.get('currentStep') == 'success':
                            return {'success': True, 'message': '验证成功'}
                        else:
                            return {'success': False, 'message': f"验证失败: {retry_result.get('errorIds', [])}"}
                
                # 其他情况
                return {'success': False, 'message': f"验证失败: {result.get('errorIds', [])}"}
            else:
                return {'success': False, 'message': '提交邮件验证失败'}

        # 最后检查是否已验证过（作为兜底逻辑）
        if result.get('_already_verified'):
            return {'success': False, 'message': '资料已被验证过', 'skip': True}

        return {'success': False, 'message': f"未知状态: {current_step}"}

    except Exception as e:
        return {'success': False, 'error': str(e)}


def parse_data_line(line):
    """解析数据行: firstName|lastName|branch|birthDate|dischargeDate"""
    parts = line.split('|')
    if len(parts) < 4:
        return None

    first_name = parts[0].strip()
    last_name = parts[1].strip()
    branch = parts[2].strip()
    birth_date = parts[3].strip()
    discharge_date = parts[4].strip() if len(parts) > 4 else '2025-01-02'

    branch_name = match_branch(branch)
    org = BRANCH_ORG_MAP.get(branch_name, BRANCH_ORG_MAP['Army'])

    return {
        'firstName': first_name,
        'lastName': last_name,
        'birthDate': birth_date,
        'dischargeDate': discharge_date,
        'organization': org
    }


def move_to_used(line, status):
    """将用过的数据移到 used.txt"""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    with open(USED_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] [{status}] {line}\n")


def remove_from_data(line):
    """从 data.txt 中移除已用的行"""
    content = DATA_FILE.read_text(encoding='utf-8')
    lines = content.split('\n')
    new_lines = [l for l in lines if l.strip() != line.strip()]
    DATA_FILE.write_text('\n'.join(new_lines), encoding='utf-8')


def log_result(msg):
    """记录结果"""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    with open(RESULT_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {msg}\n")


def main():
    print()
    print('=' * 50)
    print('  SheerID Verification Tool')
    print('  ChatGPT Plus 身份验证工具')
    print('  作者: dy安心大油条')
    print('=' * 50)
    print()

    # 加载配置
    if not CONFIG_FILE.exists():
        print('[错误] 请先创建 config.json！参考 config.example.json')
        return

    config = json.loads(CONFIG_FILE.read_text(encoding='utf-8'))

    if not config.get('accessToken'):
        print('[错误] config.json 中缺少 accessToken')
        print('       请登录 chatgpt.com，从开发者工具获取 accessToken')
        return

    # 初始化邮箱（支持 IMAP、CloudMail、Mailpit 和 Webhook 四种方式）
    email_config = config.get('email', {})
    email_type = email_config.get('type', 'imap').lower()

    if email_type == 'cloudmail':
        # CloudMail API 方式
        if not email_config.get('api_url') or not email_config.get('email_address'):
            print('[错误] CloudMail 配置不完整，请检查 api_url 和 email_address')
            return
        email_client = CloudMailClient(email_config)
        print(f"[CloudMail] {email_config['email_address']}")
    elif email_type == 'mailpit':
        # Mailpit API 方式
        if not email_config.get('api_url'):
            print('[错误] Mailpit 配置不完整，请检查 api_url')
            return
        email_client = MailpitClient(email_config)
        email_addr = email_config.get('email_address', 'any@example.com')
        print(f"[Mailpit] {email_addr} (本地测试邮箱)")
    elif email_type == 'webhook':
        # Webhook 方式 - 本地 HTTP 服务接收
        if not email_config.get('api_url'):
            print('[错误] Webhook 配置不完整，请检查 api_url')
            return
        email_client = WebhookEmailClient(email_config)
        email_addr = email_config.get('email_address', 'any@example.com')
        print(f"[Webhook] {email_addr} (HTTP 服务接收)")
    else:
        # IMAP 方式
        if not email_config.get('email_address'):
            print('[错误] config.json 中缺少邮箱配置')
            return
        email_client = EmailClient(email_config)
        print(f"[IMAP] {email_config['email_address']}")

    if not email_client.connect():
        print('[错误] 邮箱连接失败，请检查配置')
        return
    print('[邮箱] 连接成功')

    # 加载数据
    if not DATA_FILE.exists():
        print('[错误] 请先创建 data.txt！参考 data.example.txt')
        return

    lines = [l.strip() for l in DATA_FILE.read_text(encoding='utf-8').split('\n')
             if l.strip() and not l.startswith('#')]

    if not lines:
        print('[错误] data.txt 中没有数据')
        return

    print(f"[数据] 共 {len(lines)} 条")
    print()
    print('-' * 50)

    # 写入结果文件头
    log_result(f"\n========== 验证开始 ==========")

    success_count = 0
    fail_count = 0
    skip_count = 0
    total = len(lines)
    i = 0
    retry_count = {}  # 记录每条数据的重试次数

    while i < total:
        line = lines[i]
        user_data = parse_data_line(line)
        if not user_data:
            print(f"[{i+1}/{total}] 格式错误，跳过")
            i += 1
            continue

        name = f"{user_data['firstName']} {user_data['lastName']}"
        branch = user_data['organization']['name']

        print(f"\n[{i+1}/{total}] {name} ({branch})")

        # 加载代理和 TLS 指纹（每次都重新加载，避免状态污染）
        proxy = load_random_proxy(PROXY_FILE)
        proxy_dict = get_proxy_dict(proxy)
        tls_profile = load_random_tls_profile(ua_keywords=["Chrome", "Windows"])

        result = verify(
            config['accessToken'],
            config.get('programId', DEFAULT_PROGRAM_ID),
            user_data,
            email_config['email_address'],
            proxy_dict,
            tls_profile,
            email_client
        )

        if result.get('success'):
            success_count += 1
            print(f"    [OK] 成功!")
            log_result(f"[OK] {name} | {branch}")
            move_to_used(line, '成功')
            remove_from_data(line)
            retry_count.pop(i, None)  # 清除重试计数
            print()
            print('-' * 50)
            print('  验证成功! 停止运行')
            print('-' * 50)
            break
        elif result.get('retry'):
            # 需要重新创建验证，重试当前记录
            current_retry = retry_count.get(i, 0)
            
            if current_retry >= 3:
                # 超过最大重试次数，标记为失败
                print(f"    [FAIL] 已重试 {current_retry} 次，跳过此记录")
                fail_count += 1
                log_result(f"[FAIL] {name} | {branch} | 重试次数超限")
                move_to_used(line, '失败')
                remove_from_data(line)
                retry_count[i] = 0  # 重置计数
                i += 1
            else:
                # 增加重试计数
                retry_count[i] = current_retry + 1
                wait_time = 5 + (current_retry * 5)  # 递增等待时间: 5, 10, 15 秒
                print(f"    [RETRY] 第 {retry_count[i]} 次重试，等待 {wait_time} 秒...")
                time.sleep(wait_time)
                # 不增加 i，继续处理当前记录
        elif result.get('fatal'):
            # 致命错误（如账号已失效），停止所有处理
            error_msg = result.get('message', '致命错误')
            fail_count += 1
            print(f"    [FATAL] {error_msg}")
            log_result(f"[FATAL] {name} | {branch} | {error_msg}")
            print()
            print('-' * 50)
            print('  ⚠️  检测到致命错误，停止运行')
            print('  请更换新的 ChatGPT 账号后重试')
            print('-' * 50)
            break
        elif result.get('skip'):
            skip_count += 1
            print(f"    [SKIP] 资料已验证过")
            log_result(f"[SKIP] {name} | {branch}")
            move_to_used(line, '跳过')
            remove_from_data(line)
            retry_count.pop(i, None)  # 清除重试计数
            i += 1
        else:
            error_msg = result.get('error') or result.get('message') or '未知错误'
            fail_count += 1
            print(f"    [FAIL] {error_msg}")
            log_result(f"[FAIL] {name} | {branch} | {error_msg}")
            move_to_used(line, '失败')
            remove_from_data(line)
            retry_count.pop(i, None)  # 清除重试计数
            i += 1

        if i < total:
            time.sleep(1)

    email_client.close()

    print()
    print('-' * 50)
    print(f"  完成! 成功:{success_count} 跳过:{skip_count} 失败:{fail_count}")
    print('-' * 50)

    log_result(f"========== 结束 成功:{success_count} 跳过:{skip_count} 失败:{fail_count} ==========")


if __name__ == '__main__':
    main()
