#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
页面解析模块 for WebCrack
处理登录页面解析和验证码检测/识别
"""

from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup as BS
import re

try:
    import ddddocr
    DDDDOCR_AVAILABLE = True
except ImportError:
    DDDDOCR_AVAILABLE = False

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from ..utils.logger import Info, Error


class PageParser:
    """WebCrack的页面解析器"""
    
    def __init__(self, url, config):
        """
        初始化页面解析器
        
        Args:
            url (str): 目标URL
            config (dict): 配置字典
        """
        self.url = url
        self.config = config
        self.requests_proxies = config["brute_force"]["requests_proxies"]
        self.timeout = config["brute_force"]["timeout"]
        
        # 解析数据
        self.response_content = ''
        self.form_content = ''
        self.username_field = ''
        self.password_field = ''
        self.form_data = {}
        self.cms_info = ''
        self.post_path = ''
        
        # 验证码相关
        self.captcha_input_name = ''  # 验证码输入框名称
        self.captcha_img_url = ''     # 验证码图片URL
        self.captcha_value = ''       # 验证码值(如果已识别)
    
    def run(self):
        """
        运行完整的解析过程
        
        Returns:
            bool: 解析成功返回True，否则返回False
        """
        try:
            self._get_response_content()
            self._parse_cms()
            self._parse_form()
            
            # 如果启用验证码且ddddocr可用，则处理验证码
            if self.config["captcha"]["enabled"] and DDDDOCR_AVAILABLE:
                self._parse_captcha_with_ocr()
            else:
                self._parse_captcha()
                
            self._check_login_page()
            self._parse_post_path()
            self._parse_form_parameters()
            
            # 如果检测到验证码则记录信息
            if self.captcha_input_name and self.captcha_img_url:
                Info(f"[*] 检测到验证码: 字段={self.captcha_input_name}, 图片={self.captcha_img_url}")
                
            return True
        except Exception as e:
            Error(f"[-] {self.url} 解析出错: {str(e)}")
            return False
    
    def _get_response_content(self):
        """
        获取目标URL的响应内容
        """
        from src.utils.header_generator import get_random_headers
        
        try:
            res = requests.get(
                self.url, 
                timeout=self.timeout, 
                verify=False, 
                headers=get_random_headers(self.config),
                proxies=self.requests_proxies
            )
            res.encoding = res.apparent_encoding
            self.response_content = res.text
            
            # 记录响应的更多信息，帮助调试
            Info(f"[*] {self.url} 响应状态码: {res.status_code}, 内容长度: {len(res.text)} 字符")
            
            # 如果状态码不是200，记录警告信息
            if res.status_code != 200:
                Info(f"[*] {self.url} 返回非200状态码: {res.status_code}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"获取页面内容失败: {str(e)}")
    
    def _parse_cms(self):
        """
        解析页面中的CMS信息
        """
        for cms_name, cms_data in self.config["cms"].items():
            keyword = cms_data["keywords"]
            if keyword and (keyword in self.response_content):
                Info(f"[*] {self.url} 识别到CMS: {cms_data['name']}")
                if cms_data['alert']:
                    Info(f"[*] {self.url} {cms_data['note']}")
                self.cms_info = cms_data
                break
    
    def _parse_form(self):
        """
        解析页面表单内容
        """
        html = self.response_content
        result = re.findall(".*<form (.*)</form>.*", html, re.S)
        if result:
            form_data = '<form ' + result[0] + ' </form>'
            form_soup = BS(form_data, "lxml")
            self.form_content = form_soup.form
        else:
            # 提供更详细的错误信息
            content_length = len(html)
            has_body = "<body" in html.lower()
            has_input = "<input" in html.lower()
            
            error_details = f"无法找到表单元素。页面长度: {content_length} 字符"
            if not has_body:
                error_details += ", 页面缺少<body>标签"
            if not has_input:
                error_details += ", 页面缺少<input>元素"
                
            # 检查是否是错误页面或重定向页面
            if "404" in html or "not found" in html.lower():
                error_details += ", 可能是404页面"
            elif "500" in html or "internal server error" in html.lower():
                error_details += ", 可能是500服务器错误"
            elif "<script" in html and "location.href" in html:
                error_details += ", 可能包含重定向脚本"
                
            raise Exception(error_details)
    
    def _check_login_page(self):
        """
        检查页面是否为登录页面
        """
        login_keywords = self.config["parser"]["login_keywords"]
        form_str = str(self.form_content).lower()
        
        for keyword in login_keywords:
            if keyword in form_str:
                return True
                
        raise Exception("可能不是登录页面")
    
    def _parse_captcha(self):
        """
        使用关键字匹配解析验证码(原始方法)
        """
        captcha_keywords = self.config["parser"]["captcha_keywords"]
        content_lower = self.response_content.lower()
        
        for keyword in captcha_keywords:
            if keyword in content_lower:
                raise Exception(f"登录页面存在验证码关键字: '{keyword}'")
    
    def _parse_captcha_with_ocr(self):
        """
        使用OCR识别解析验证码
        """
        # 检查验证码关键字
        captcha_keywords = self.config["parser"]["captcha_keywords"]
        captcha_found = False
        content_lower = self.response_content.lower()
        
        for keyword in captcha_keywords:
            if keyword in content_lower:
                captcha_found = True
                break
        
        # 如果发现验证码，尝试识别
        if captcha_found:
            Info(f"[*] {self.url} 检测到验证码，尝试OCR识别")
            self._find_captcha_elements()
    
    def _find_captcha_elements(self):
        """
        查找验证码输入框和图片元素
        """
        captcha_img_keywords = self.config["parser"]["captcha_img_keywords"]
        captcha_input_name = self.config["captcha"]["captcha_input_name"]
        captcha_img_name = self.config["captcha"]["captcha_img_name"]
        
        # 查找验证码输入框
        for input_element in self.form_content.find_all('input'):
            if input_element.has_attr('name'):
                input_name = input_element['name'].lower()
                # 检查是否为验证码输入框
                if (captcha_input_name in input_name or 
                    any(keyword in input_name for keyword in ["captcha", "code", "verify", "验证码"])):
                    self.captcha_input_name = input_element['name']
                    Info(f"[*] 找到验证码输入框: {self.captcha_input_name}")
                    break
        
        # 查找验证码图片
        for img_element in self.form_content.find_all('img'):
            if img_element.has_attr('src'):
                img_src = img_element['src'].lower()
                # 检查是否为验证码图片
                if (captcha_img_name in img_src or 
                    any(keyword in img_src for keyword in captcha_img_keywords)):
                    # 构造完整图片URL
                    self.captcha_img_url = urljoin(self.url, img_element['src'])
                    Info(f"[*] 找到验证码图片: {self.captcha_img_url}")
                    break
        
        # 如果找到验证码元素，尝试识别
        if self.captcha_input_name and self.captcha_img_url:
            self._recognize_captcha()
        elif self.captcha_input_name or self.captcha_img_url:
            Info(f"[*] 检测到部分验证码元素，继续处理")
        else:
            Info(f"[*] 检测到验证码关键字但未找到验证码元素，继续处理")
    
    def _recognize_captcha(self):
        """
        使用ddddocr识别验证码
        """
        if not DDDDOCR_AVAILABLE:
            Error("[-] 未安装ddddocr库，无法进行验证码识别")
            return
        
        try:
            Info(f"[*] 正在识别验证码图片: {self.captcha_img_url}")
            
            from src.utils.header_generator import get_random_headers
            
            # 下载验证码图片
            headers = get_random_headers(self.config)
            response = requests.get(
                self.captcha_img_url, 
                headers=headers,
                timeout=self.timeout, 
                verify=False,
                proxies=self.requests_proxies
            )
            
            if response.status_code == 200:
                # 使用ddddocr识别验证码
                ocr = ddddocr.DdddOcr()
                captcha_text = ocr.classification(response.content)
                Info(f"[*] 验证码识别结果: {captcha_text}")
                
                # 保存识别值用于暴力破解
                self.captcha_value = captcha_text
            else:
                Error(f"[-] 下载验证码图片失败，状态码: {response.status_code}")
        except Exception as e:
            Error(f"[-] 验证码识别失败: {str(e)}")
    
    def _parse_post_path(self):
        """
        解析表单提交路径
        """
        url = self.url
        content = self.form_content
        form_action = str(content).split('\n')[0]
        soup = BS(form_action, "lxml")
        res = urlparse(url)
        
        try:
            action_path = soup.form['action']
        except:
            self.post_path = url  # 如果没有action则默认为URL
            return

        if action_path.startswith('http'):  # 绝对路径
            path = action_path
        elif action_path.startswith('/'):  # 根路径
            root_path = res.scheme + '://' + res.netloc
            path = root_path + action_path
        elif action_path == '':  # 空action
            path = url
        else:  # 相对路径
            relative_path = url.rstrip(url.split('/')[-1])
            path = relative_path + action_path
            
        if not path:
            raise Exception("无法确定提交路径")
        self.post_path = path
    
    def _parse_form_parameters(self):
        """
        解析表单参数
        """
        content = self.form_content
        data = {}
        username_field = ''
        password_field = ''
        
        username_keywords = self.config["parser"]["username_keywords"]
        password_keywords = self.config["parser"]["password_keywords"]
        default_value = self.config["parser"]["default_value"]
        
        # 提取所有输入字段
        for input_element in content.find_all('input'):
            if input_element.has_attr('name'):
                parameter = input_element['name']
            else:
                parameter = ''
                
            if input_element.has_attr('value'):
                value = input_element['value']
            else:
                value = default_value
                
            if parameter:
                data[parameter] = value

        # 提取用户名和密码字段名
        for parameter in data:
            if not username_field and parameter != password_field:
                for keyword in username_keywords:
                    if keyword in parameter.lower():
                        username_field = parameter
                        break
            if not password_field and parameter != username_field:
                for keyword in password_keywords:
                    if keyword in parameter.lower():
                        password_field = parameter
                        break

        # 移除reset字段
        reset_fields = []
        for key in data.keys():
            if 'reset' in key.lower():
                reset_fields.append(key)
                
        for field in reset_fields:
            data.pop(field, None)

        if username_field and password_field:
            self.username_field = username_field
            self.password_field = password_field
            self.form_data = data
            # 如果识别了验证码则添加到表单数据中
            if self.captcha_input_name and self.captcha_value:
                self.form_data[self.captcha_input_name] = self.captcha_value
        else:
            raise Exception("无法找到登录参数")