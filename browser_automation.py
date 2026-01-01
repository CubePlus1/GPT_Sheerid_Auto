"""
浏览器自动化模块 - 模拟人类点击验证按钮
使用 Selenium 在 ChatGPT 页面自动触发验证流程
"""

import time
import json
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class ChatGPTAutomation:
    def __init__(self, access_token, headless=False):
        """
        初始化浏览器自动化
        
        Args:
            access_token: ChatGPT accessToken（从 config.json 获取）
            headless: 是否无头模式运行（默认 False，显示浏览器窗口）
        """
        self.access_token = access_token
        self.headless = headless
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """配置并启动 Chrome 浏览器"""
        options = Options()
        
        # 基础配置
        if self.headless:
            options.add_argument('--headless=new')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        # 模拟真实用户
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 禁用图片加载（加快速度）
        prefs = {
            'profile.managed_default_content_settings.images': 2,
            'disk-cache-size': 4096
        }
        options.add_experimental_option('prefs', prefs)
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 15)
            
            # 隐藏 webdriver 特征
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
            })
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("    ✓ 浏览器启动成功")
            return True
            
        except Exception as e:
            print(f"    ✗ 浏览器启动失败: {e}")
            return False
    
    def inject_auth_token(self):
        """注入 ChatGPT accessToken"""
        try:
            # 先访问主页建立 cookie
            self.driver.get('https://chatgpt.com')
            time.sleep(2)
            
            # 通过 localStorage 注入 token
            script = f"""
            const token = '{self.access_token}';
            localStorage.setItem('accessToken', token);
            
            // 设置其他可能需要的认证信息
            const authData = {{
                accessToken: token,
                expires: Date.now() + 86400000
            }};
            localStorage.setItem('auth', JSON.stringify(authData));
            
            return true;
            """
            
            result = self.driver.execute_script(script)
            
            if result:
                print("    ✓ accessToken 注入成功")
                time.sleep(1)
                return True
            else:
                print("    ✗ accessToken 注入失败")
                return False
                
        except Exception as e:
            print(f"    ✗ Token 注入异常: {e}")
            return False
    
    def navigate_to_veterans_page(self):
        """导航到军人验证页面"""
        try:
            url = 'https://chatgpt.com/veterans-claim'
            print(f"    → 访问: {url}")
            
            self.driver.get(url)
            time.sleep(3)
            
            # 检查页面是否加载成功
            if 'veterans' in self.driver.current_url.lower():
                print("    ✓ 页面加载成功")
                return True
            else:
                print(f"    ✗ 页面跳转异常: {self.driver.current_url}")
                return False
                
        except Exception as e:
            print(f"    ✗ 页面访问失败: {e}")
            return False
    
    def click_verify_button(self):
        """
        点击"验证资格"按钮
        
        Returns:
            dict: {'success': bool, 'verification_id': str}
        """
        try:
            print("    → 查找验证按钮...")
            
            # 尝试多种可能的选择器
            button_selectors = [
                "//button[contains(text(), '验证资格')]",
                "//button[contains(text(), 'Verify eligibility')]",
                "//button[contains(text(), '验证')]",
                "//button[contains(text(), 'Verify')]",
                "//button[@type='submit']",
                "//a[contains(@href, 'verify')]",
                "button[class*='verify']",
                "button[class*='btn']"
            ]
            
            button = None
            for selector in button_selectors:
                try:
                    if selector.startswith('//'):
                        button = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        button = self.wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    
                    if button:
                        print(f"    ✓ 找到按钮: {selector}")
                        break
                        
                except (TimeoutException, NoSuchElementException):
                    continue
            
            if not button:
                print("    ✗ 未找到验证按钮")
                # 打印页面源代码用于调试
                print("\n=== 页面内容 ===")
                print(self.driver.page_source[:1000])
                print("================\n")
                return {'success': False, 'message': '未找到验证按钮'}
            
            # 滚动到按钮位置
            self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
            time.sleep(0.5)
            
            # 点击按钮
            print("    → 点击验证按钮...")
            button.click()
            time.sleep(3)
            
            # 检查是否跳转到 SheerID 页面或弹出窗口
            current_url = self.driver.current_url
            
            # 检查是否有新窗口/iframe
            handles = self.driver.window_handles
            if len(handles) > 1:
                print("    ✓ 检测到新窗口，切换...")
                self.driver.switch_to.window(handles[-1])
                current_url = self.driver.current_url
            
            # 检查 iframe
            try:
                iframe = self.driver.find_element(By.TAG_NAME, 'iframe')
                self.driver.switch_to.frame(iframe)
                print("    ✓ 切换到 iframe")
                current_url = self.driver.current_url
            except NoSuchElementException:
                pass
            
            print(f"    → 当前 URL: {current_url}")
            
            # 从 URL 或页面中提取 verificationId
            verification_id = self.extract_verification_id(current_url)
            
            if verification_id:
                print(f"    ✓ 获取到 verificationId: {verification_id}")
                return {
                    'success': True,
                    'verification_id': verification_id,
                    'url': current_url
                }
            else:
                print("    ✗ 未获取到 verificationId")
                return {
                    'success': False,
                    'message': '点击成功但未获取到验证ID',
                    'url': current_url
                }
                
        except TimeoutException:
            print("    ✗ 等待超时")
            return {'success': False, 'message': '页面加载超时'}
            
        except Exception as e:
            print(f"    ✗ 点击失败: {e}")
            return {'success': False, 'message': str(e)}
    
    def extract_verification_id(self, url_or_page):
        """
        从 URL 或页面源码中提取 verificationId
        
        Args:
            url_or_page: URL 字符串或完整页面 HTML
        
        Returns:
            str: verificationId 或 None
        """
        try:
            # 从 URL 中提取
            import re
            
            # SheerID 的验证 URL 格式
            patterns = [
                r'verification[Ii]d[=/]([a-f0-9]{24})',
                r'/verify/([a-f0-9]{24})',
                r'id=([a-f0-9]{24})',
                r'"verificationId"\s*:\s*"([a-f0-9]{24})"',
                r"'verificationId'\s*:\s*'([a-f0-9]{24})'"
            ]
            
            # 先在 URL 中搜索
            for pattern in patterns:
                match = re.search(pattern, url_or_page)
                if match:
                    return match.group(1)
            
            # 在页面源码中搜索
            try:
                page_source = self.driver.page_source
                for pattern in patterns:
                    match = re.search(pattern, page_source)
                    if match:
                        return match.group(1)
            except:
                pass
            
            # 尝试从 localStorage/sessionStorage 获取
            try:
                script = """
                return localStorage.getItem('verificationId') || 
                       sessionStorage.getItem('verificationId') ||
                       window.verificationId;
                """
                verification_id = self.driver.execute_script(script)
                if verification_id:
                    return verification_id
            except:
                pass
            
            return None
            
        except Exception as e:
            print(f"    ! 提取 verificationId 异常: {e}")
            return None
    
    def trigger_verification(self):
        """
        完整流程：触发验证并返回 verificationId
        
        Returns:
            dict: {'success': bool, 'verification_id': str, 'message': str}
        """
        try:
            # 1. 启动浏览器
            if not self.setup_driver():
                return {'success': False, 'message': '浏览器启动失败'}
            
            # 2. 注入 token
            if not self.inject_auth_token():
                return {'success': False, 'message': 'Token 注入失败'}
            
            # 3. 访问验证页面
            if not self.navigate_to_veterans_page():
                return {'success': False, 'message': '页面访问失败'}
            
            # 4. 点击验证按钮
            result = self.click_verify_button()
            
            return result
            
        except Exception as e:
            print(f"    ✗ 流程异常: {e}")
            return {'success': False, 'message': str(e)}
        
        finally:
            # 保持浏览器打开以便调试
            if not self.headless:
                print("\n    [提示] 浏览器将保持打开 10 秒以便查看...")
                time.sleep(10)
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            try:
                self.driver.quit()
                print("    ✓ 浏览器已关闭")
            except:
                pass


def test_automation():
    """测试函数"""
    config_file = Path(__file__).parent / 'config.json'
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        access_token = config.get('accessToken', '').strip()
        
        if not access_token:
            print("错误: config.json 中未找到 accessToken")
            return
        
        print("=== ChatGPT 浏览器自动化测试 ===\n")
        
        automation = ChatGPTAutomation(access_token, headless=False)
        result = automation.trigger_verification()
        
        print("\n=== 结果 ===")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        automation.close()
        
    except FileNotFoundError:
        print(f"错误: 未找到配置文件 {config_file}")
    except json.JSONDecodeError:
        print("错误: config.json 格式错误")
    except Exception as e:
        print(f"错误: {e}")


if __name__ == '__main__':
    test_automation()
