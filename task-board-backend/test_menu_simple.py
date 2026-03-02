#!/usr/bin/env python3
"""
测试菜单接口是否存在（简化版）
"""
import requests

# 测试菜单接口
base_url = "http://localhost:8001/api"

print("测试菜单接口...")
print("=" * 50)

# 测试获取用户菜单接口
print("\n测试获取用户菜单接口 (/api/menus/user):")
try:
    response = requests.get(f"{base_url}/menus/user")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
except Exception as e:
    print(f"错误: {e}")

print("\n" + "=" * 50)
print("测试完成！")