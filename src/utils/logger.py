#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志模块 for WebCrack
处理所有活动和结果的日志记录
"""

import time
import os
from pathlib import Path
from datetime import datetime

# 定义 ANSI 颜色代码
RESET = '\033[0m'
GREEN = '\033[92m'
PURPLE = '\033[95m'


class Logger:
    """WebCrack的日志记录器"""
    
    def __init__(self, log_dir=None):
        """
        初始化日志记录器
        
        Args:
            log_dir (str, optional): 日志文件目录
        """
        if log_dir is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
            # 使用模块的父级目录作为基础目录
            base_dir = Path(__file__).parent.parent.parent
            self.log_dir = base_dir / 'logs' / date_str
        else:
            self.log_dir = Path(log_dir)
            
        # 创建日志目录（如果不存在）
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 日志文件路径
        self.success_file = self.log_dir / "success.txt"
        self.log_file = self.log_dir / "logs.txt"
        
        # 任务ID
        self.task_id = None
    
    def set_task_id(self, task_id):
        """
        设置任务ID用于日志记录
        
        Args:
            task_id (int): 任务ID
        """
        self.task_id = task_id
    
    def _get_timestamp(self):
        """
        获取当前时间戳
        
        Returns:
            str: 格式化的时间戳
        """
        return datetime.now().strftime('%Y-%m-%d %X')
    
    def _write_log(self, filename, message):
        """
        写入消息到日志文件
        
        Args:
            filename (Path): 日志文件路径
            message (str): 要写入的消息
        """
        try:
            with open(filename, "a+", encoding="UTF-8") as f:
                f.write(message + "\n")
        except Exception as e:
            print(f"写入日志文件 {filename} 出错: {e}")
    
    def info(self, message):
        """
        记录信息日志
        
        Args:
            message (str): 要记录的消息
        """
        timestamp = self._get_timestamp()
        if self.task_id is not None:
            log_message = f"{timestamp}  任务ID: {self.task_id} {message}"
        else:
            log_message = f"{timestamp}  {message}"
            
        print(log_message)
        self._write_log(self.log_file, log_message)
    
    def error(self, message):
        """
        记录错误日志（紫色显示）
        
        Args:
            message (str): 要记录的错误消息
        """
        timestamp = self._get_timestamp()
        if self.task_id is not None:
            log_message = f"{timestamp}  任务ID: {self.task_id} {message}"
        else:
            log_message = f"{timestamp}  {message}"
            
        print(PURPLE + log_message + RESET)
        self._write_log(self.log_file, log_message)
    
    def success(self, message):
        """
        记录成功日志（绿色显示）
        
        Args:
            message (str): 要记录的成功消息
        """
        timestamp = self._get_timestamp()
        if self.task_id is not None:
            log_message = f"{timestamp}  任务ID: {self.task_id} {message}"
        else:
            log_message = f"{timestamp}  {message}"
            
        print(GREEN + log_message + RESET)
        self._write_log(self.success_file, log_message)
        self._write_log(self.log_file, log_message)


# 全局日志记录器实例
_logger = None


def init_logger(log_dir=None):
    """
    初始化全局日志记录器
    
    Args:
        log_dir (str, optional): 日志文件目录
    """
    global _logger
    _logger = Logger(log_dir)
    return _logger


def Info(message):
    """
    记录信息日志
    
    Args:
        message (str): 要记录的消息
    """
    if _logger is None:
        init_logger()
    _logger.info(message)


def Error(message):
    """
    记录错误日志（紫色显示）
    
    Args:
        message (str): 要记录的错误消息
    """
    if _logger is None:
        init_logger()
    _logger.error(message)


def Success(message):
    """
    记录成功日志（绿色显示）
    
    Args:
        message (str): 要记录的成功消息
    """
    if _logger is None:
        init_logger()
    _logger.success(message)