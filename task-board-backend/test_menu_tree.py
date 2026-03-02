#!/usr/bin/env python3
"""
测试菜单树接口
"""
import requests
import json

# 测试菜单接口
base_url = "http://localhost:8001/api"

print("测试菜单树接口...")
print("=" * 50)

# 测试获取菜单树
print("\n测试获取菜单树接口 (/api/menus/tree):")
try:
    # 先登录获取token
    login_response = requests.post(f"{base_url}/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    
    if login_response.status_code == 200:
        token = login_response.json().get("token")
        print(f"登录成功，获取到token: {token[:20]}...")
        
        # 使用token获取菜单树
        headers = {"Authorization": f"Bearer {token}"}
        menu_response = requests.get(f"{base_url}/menus/tree", headers=headers)
        
        print(f"状态码: {menu_response.status_code}")
        
        if menu_response.status_code == 200:
            menus = menu_response.json()
            print(f"\n菜单数量: {len(menus)}")
            print(f"\n完整的菜单数据（JSON格式）:")
            print(json.dumps(menus, indent=2, ensure_ascii=False))
        else:
            print(f"响应: {menu_response.text}")
    else:
        print(f"登录失败: {login_response.text}")
        
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("测试完成！")