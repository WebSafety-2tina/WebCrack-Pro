#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Header Generator module for WebCrack
Handles generation of random headers including User-Agent
"""

import random


def get_random_headers(config):
    """
    Generate random headers
    
    Args:
        config (dict): Configuration dictionary
        
    Returns:
        dict: Random headers
    """
    headers_config = config["headers"]
    
    if headers_config["enabled"]:
        # Select random User-Agent
        user_agent = random.choice(headers_config["user_agents"])
        
        # Generate random IP addresses
        a = str(random.randint(1, 255))
        b = str(random.randint(1, 255))
        c = str(random.randint(1, 255))
        random_xff = '127.' + a + '.' + b + '.' + c
        random_ci = '127.' + c + '.' + a + '.' + b
        
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'User-Agent': user_agent,
            'X-Forwarded-For': random_xff,
            'Client-IP': random_ci,
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            "Referer": "http://www.baidu.com/",
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    else:
        headers = headers_config["default_headers"].copy()

    return headers