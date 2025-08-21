#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WebCrack - Modern Version
Advanced Web Login Brute Force Tool with CAPTCHA Recognition

This is a modernized version of the WebCrack tool with improved structure,
enhanced CAPTCHA recognition, and better code organization.
"""

import os
import sys
import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from pyfiglet import Figlet
from src.core.brute_force import BruteForceTask
from src.utils.config import load_config
from src.utils.logger import init_logger


def print_banner():
    """Print the application banner with color and compact ASCII art"""
    # 定义 ANSI 颜色代码
    GREEN = '\033[92m'
    YELLOW = '\033[33m'  # 更黄的金色
    RESET = '\033[0m'

    # 使用pyfiglet生成ASCII艺术标题
    f = Figlet(font='slant')
    print(GREEN + f.renderText('WebCrack-PRO') + RESET)

    # 缩小并美化 ASCII 艺术标题
    banner = f'''
{YELLOW}[*]WEB后台弱口令和万能密码检测工具
[*]根据https://github.com/yzddmr6/WebCrack/进行升级
[*]原作者: @yzddmr6 & AI
[*]BY: @WebSafety-2tina & AI
[*]Github:https://github.com/WebSafety-2tina/WebCrack-PRO
[*]增加:1.增加更多的UA 2.增加https代理模式 3.增加更多字典 4.增加多线程模式
'''

    print(banner)


def load_urls_from_file(file_path):
    """
    从文件加载URL列表
    
    Args:
        file_path (str): 包含URL的文件路径
        
    Returns:
        list: 有效的URL列表
    """
    urls = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                url = line.strip()
                if url and not url.startswith('#') and not ('.edu.cn' in url or '.gov.cn' in url):
                    urls.append(url)
    except FileNotFoundError:
        print(f"错误: 文件 {file_path} 不存在!")
        sys.exit(1)
    except Exception as e:
        print(f"读取文件出错: {e}")
        sys.exit(1)
        
    return urls


def set_proxy(config):
    """
    设置代理配置
    
    Args:
        config (dict): 配置字典
    """
    proxy_choice = input("是否使用代理? (y/n): ").strip().lower()
    if proxy_choice == 'y':
        proxy_addr = input("请输入代理地址 (例如: 127.0.0.1:8080): ").strip()
        if proxy_addr:
            config["brute_force"]["requests_proxies"] = {
                "http": f"http://{proxy_addr}",
                "https": f"https://{proxy_addr}"
            }
            print(f"代理已设置为: {proxy_addr}")
        else:
            print("代理地址为空，将不使用代理。")
    else:
        print("将不使用代理。")


def run_single_task(task_id, url, config):
    """
    运行单个暴力破解任务
    
    Args:
        task_id (int): 任务ID
        url (str): 目标URL
        config (dict): 配置字典
    """
    task = BruteForceTask(config)
    task.run(task_id, url)


def run_batch_tasks(urls, config):
    """
    运行批量暴力破解任务（不使用多线程处理多个URL）
    
    Args:
        urls (list): URL列表
        config (dict): 配置字典
    """
    total_tasks = len(urls)
    print(f"总任务数: {total_tasks}")
    
    # 不再询问用户是否使用多线程处理多个URL
    max_workers = 1
    print("逐个处理URL任务，每个URL内部可使用多线程加速暴力破解")
    
    start_time = datetime.datetime.now()
    
    # 单线程执行任务，一个任务完成后再进行下一个
    # 但每个任务内部可以使用多线程进行暴力破解
    for i, url in enumerate(urls, 1):
        try:
            run_single_task(i, url, config)
        except Exception as e:
            print(f"任务 {i} 处理URL {url} 时出错: {e}")
    
    end_time = datetime.datetime.now()
    print(f'所有任务已完成! 耗时: {end_time - start_time}')


def main():
    """主函数"""
    print_banner()
    
    # 加载配置
    try:
        config = load_config()
    except Exception as e:
        print(f"加载配置失败: {e}")
        sys.exit(1)
    
    # 设置代理
    set_proxy(config)
    
    # 选择模式
    mode_choice = input("请选择模式 (1: 简单模式 2: 复杂模式): ").strip()
    if mode_choice == "1":
        # 简单模式 - 只使用基础字典中的用户名和password_list.txt中的密码
        config["dictionary"]["file"]["enabled"] = False  # 禁用文件字典
        config["dictionary"]["domain"]["enabled"] = False  # 禁用域名字典
        print("已选择简单模式")
    elif mode_choice == "2":
        # 复杂模式 - 使用username.txt和password.txt文件
        config["dictionary"]["file"]["enabled"] = True
        config["dictionary"]["file"]["username_file"] = "username.txt"
        config["dictionary"]["file"]["password_file"] = "password.txt"
        print("已选择复杂模式")
    else:
        print("无效选择，使用默认设置")
    
    # 获取URL输入
    url_input = input('请输入URL文件名或单个URL:\n').strip()
    
    if '://' in url_input:
        # 单个URL
        run_single_task(1, url_input, config)
    else:
        # URL文件
        urls = load_urls_from_file(url_input)
        if not urls:
            print("文件中未找到有效的URL!")
            sys.exit(1)
        
        run_batch_tasks(urls, config)


if __name__ == '__main__':
    main()