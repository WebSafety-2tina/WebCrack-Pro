#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
字典生成工具 for WebCrack
处理用户名和密码字典的生成
"""

import re
import os
from pathlib import Path
from .logger import Info


def generate_dictionary(url, config):
    """
    生成用户名和密码字典
    
    Args:
        url (str): 目标URL
        config (dict): 配置字典
        
    Returns:
        tuple: (username_list, password_list)
    """
    # 从基础字典开始
    username_list, password_list = _generate_base_dict(config)
    
    # 添加文件字典
    if config["dictionary"]["file"]["enabled"]:
        file_user_dict, file_pass_dict = _generate_file_dict(config)
        if file_user_dict and file_pass_dict:
            Info(f"[*] 从文件加载了 {len(file_user_dict)} 个用户名和 {len(file_pass_dict)} 个密码")
            username_list.extend(file_user_dict)
            password_list.extend(file_pass_dict)
        else:
            Info("[*] 未从文件加载到用户名或密码字典")
    
    # 添加域名字典
    if config["dictionary"]["domain"]["enabled"]:
        domain_user_dict, domain_pass_dict = _generate_domain_dict(url, config)
        if domain_user_dict and domain_pass_dict:
            Info(f"[*] 生成了 {len(domain_user_dict)} 个域名用户名和 {len(domain_pass_dict)} 个域名密码")
            username_list.extend(domain_user_dict)
            password_list.extend(domain_pass_dict)
    
    if username_list and password_list:
        # 去除重复项
        original_username_count = len(username_list)
        original_password_count = len(password_list)
        username_list = list(set(username_list))
        password_list = list(set(password_list))
        Info(f"[*] 字典去重: 用户名从 {original_username_count} 减少到 {len(username_list)}")
        Info(f"[*] 字典去重: 密码从 {original_password_count} 减少到 {len(password_list)}")
        
        return username_list, password_list
    else:
        raise Exception("[-] 字典生成失败")


def _generate_base_dict(config):
    """
    从配置生成基础字典
    
    Args:
        config (dict): 配置字典
        
    Returns:
        tuple: (username_list, password_list)
    """
    base_username_list = config["dictionary"]["base"]["username_list"].copy()
    base_password_list = config["dictionary"]["base"]["password_list"].copy()
    return base_username_list, base_password_list


def _generate_file_dict(config):
    """
    从文件生成字典
    
    Args:
        config (dict): 配置字典
        
    Returns:
        tuple: (username_list, password_list)
    """
    username_list = []
    password_list = []
    
    # 获取文件配置
    file_config = config["dictionary"]["file"]
    username_file = file_config["username_file"]
    password_file = file_config["password_file"]
    
    # 构造文件路径 (在conf目录中)
    current_dir = Path(__file__).parent
    conf_dir = current_dir.parent.parent / 'conf'
    username_file_path = conf_dir / username_file
    password_file_path = conf_dir / password_file
    
    Info(f"[*] 尝试加载用户名文件: conf/{username_file}")
    Info(f"[*] 尝试加载密码文件: conf/{password_file}")
    
    # 加载用户名
    if username_file_path.exists():
        Info(f"[*] 找到用户名文件: conf/{username_file}")
        with open(username_file_path, "r", encoding="UTF-8") as f:
            for line in f.readlines():
                username = line.strip()
                if username and not username.startswith('#'):
                    username_list.append(username)
        Info(f"[*] 从文件加载了 {len(username_list)} 个用户名")
    else:
        Info(f"[*] 未找到用户名文件: conf/{username_file}")
    
    # 加载密码
    if password_file_path.exists():
        Info(f"[*] 找到密码文件: conf/{password_file}")
        with open(password_file_path, "r", encoding="UTF-8") as f:
            for line in f.readlines():
                password = line.strip()
                if password and not password.startswith('#'):
                    password_list.append(password)
        Info(f"[*] 从文件加载了 {len(password_list)} 个密码")
    else:
        Info(f"[*] 未找到密码文件: conf/{password_file}")
    
    return username_list, password_list


def _generate_domain_dict(url, config):
    """
    生成域名字典
    
    Args:
        url (str): 目标URL
        config (dict): 配置字典
        
    Returns:
        tuple: (username_list, password_list)
    """
    username_list = []
    password_list = []
    temp_list = []
    
    suffix_list = config["dictionary"]["domain"]["suffix_list"]
    url_parts = url.split('/')
    host = url_parts[2].split(":")[0]
    
    # 检查是否为IP地址
    ip_pattern = re.compile(
        '^(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[1-9])\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)$')
    
    if ip_pattern.match(host):
        is_ip = True
        Info("[*] 目标是IP地址，跳过域名字典生成")
    else:
        is_ip = False
    
    if not is_ip:
        host_parts = host.split(".")
        parts_count = len(host_parts)
        
        # 生成域名字典1
        for i in range(parts_count):
            sub_parts = host_parts[i:]
            part = '.'.join(sub_parts)
            if len(part) < 5:
                continue
            password_list.append(part)
        
        # 生成域名字典2
        for i in range(parts_count):
            sub_part = host_parts[i]
            if len(sub_part) < 5:
                continue
            temp_list.append(sub_part)
        
        for part in temp_list:
            for suffix in suffix_list:
                password = part + suffix
                password_list.append(password)
        
        return username_list, password_list
    else:
        return [], []


def generate_sql_injection_dict(config):
    """
    生成SQL注入字典
    
    Args:
        config (dict): 配置字典
        
    Returns:
        tuple: (username_list, password_list)
    """
    sqlin_config = config["dictionary"]["sql_injection"]
    payload_list = sqlin_config["payload_list"]
    Info(f"[*] 加载了 {len(payload_list)} 个SQL注入载荷")
    return payload_list, payload_list