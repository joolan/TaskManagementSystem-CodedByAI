#!/usr/bin/env python3
"""
测试角色接口
"""
import requests

# 测试角色接口
base_url = "http://localhost:8001/api"

print("测试角色接口...")
print("=" * 50)

# 测试获取角色列表
print("\n测试获取角色列表接口 (/api/roles):")
try:
    # 先登录获取token
    login_response = requests.post(f"{base_url}/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    
    if login_response.status_code == 200:
        token = login_response.json().get("token")
        print(f"登录成功，获取到token: {token[:20]}...")
        
        # 使用token获取角色列表
        headers = {"Authorization": f"Bearer {token}"}
        roles_response = requests.get(f"{base_url}/roles", headers=headers)
        
        print(f"状态码: {roles_response.status_code}")
        print(f"响应: {roles_response.text}")
    else:
        print(f"登录失败: {login_response.text}")
        
except Exception as e:
    print(f"错误: {e}")

print("\n" + "=" * 50)
print("测试完成！")