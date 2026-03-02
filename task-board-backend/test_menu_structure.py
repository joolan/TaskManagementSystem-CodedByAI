#!/usr/bin/env python3
"""
测试菜单数据结构
"""
import requests
import json

# 测试菜单接口
base_url = "http://localhost:8001/api"

print("测试菜单数据结构...")
print("=" * 50)

# 测试获取用户菜单接口
print("\n测试获取用户菜单接口 (/api/menus/user):")
try:
    # 先登录获取token
    login_response = requests.post(f"{base_url}/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    
    if login_response.status_code == 200:
        token = login_response.json().get("token")
        print(f"登录成功，获取到token: {token[:20]}...")
        
        # 使用token获取菜单
        headers = {"Authorization": f"Bearer {token}"}
        menu_response = requests.get(f"{base_url}/menus/user", headers=headers)
        
        print(f"状态码: {menu_response.status_code}")
        
        if menu_response.status_code == 200:
            menus = menu_response.json()
            print(f"菜单数量: {len(menus)}")
            print(f"菜单结构:")
            
            def print_menu(menu, level=0):
                indent = "  " * level
                print(f"{indent}- {menu['name']} (id={menu['id']}, parent_id={menu['parent_id']})")
                if menu.get('children'):
                    for child in menu['children']:
                        print_menu(child, level + 1)
            
            for menu in menus:
                print_menu(menu)
                
            # 检查是否有重复
            all_ids = []
            def collect_ids(menu):
                all_ids.append(menu['id'])
                if menu.get('children'):
                    for child in menu['children']:
                        collect_ids(child)
            
            for menu in menus:
                collect_ids(menu)
            
            if len(all_ids) != len(set(all_ids)):
                print(f"\n警告：发现重复的菜单ID！")
                duplicates = [id for id in all_ids if all_ids.count(id) > 1]
                print(f"重复的ID: {set(duplicates)}")
            else:
                print(f"\n✓ 没有重复的菜单ID")
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