#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ES模板管理工具
用于应用、更新和管理Elasticsearch索引模板
"""

import os
import json
import argparse
from elasticsearch import Elasticsearch
from pathlib import Path

# 从环境变量获取ES连接信息
ES_HOST = os.getenv("ES_HOST_PROD", "http://localhost:9200")
ES_USER = os.getenv("ES_USER_PROD", "")
ES_PASSWORD = os.getenv("ES_PASSWORD_PROD", "")

def get_es_client():
    """创建ES客户端连接"""
    es_config = {
        'hosts': [ES_HOST],
        'timeout': 30
    }

    if ES_USER and ES_PASSWORD:
        es_config['http_auth'] = (ES_USER, ES_PASSWORD)

    return Elasticsearch(**es_config)

def load_template(template_path):
    """加载模板文件"""
    with open(template_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def apply_template(es_client, template_name, template_body):
    """应用模板到ES"""
    try:
        response = es_client.indices.put_template(
            name=template_name,
            body=template_body
        )
        print(f"✅ 模板 {template_name} 应用成功")
        return response
    except Exception as e:
        print(f"❌ 模板 {template_name} 应用失败: {e}")
        return None

def get_template(es_client, template_name):
    """获取现有模板"""
    try:
        return es_client.indices.get_template(name=template_name)
    except Exception as e:
        print(f"模板 {template_name} 不存在: {e}")
        return None

def delete_template(es_client, template_name):
    """删除模板"""
    try:
        response = es_client.indices.delete_template(name=template_name)
        print(f"✅ 模板 {template_name} 删除成功")
        return response
    except Exception as e:
        print(f"❌ 模板 {template_name} 删除失败: {e}")
        return None

def list_templates(es_client):
    """列出所有模板"""
    try:
        templates = es_client.indices.get_template()
        print("当前模板列表:")
        for name in templates.keys():
            print(f"  - {name}")
        return templates
    except Exception as e:
        print(f"获取模板列表失败: {e}")
        return None

def get_template_pattern(template_body):
    """从模板中提取索引模式"""
    return template_body.get('index_patterns', [])

def get_matching_indices(es_client, pattern):
    """获取匹配的现有索引"""
    try:
        indices = es_client.indices.get_alias(index=pattern)
        return list(indices.keys())
    except Exception:
        return []

def update_existing_indices(es_client, template_body):
    """更新现有索引的映射"""
    patterns = get_template_pattern(template_body)
    updated_indices = []

    for pattern in patterns:
        indices = get_matching_indices(es_client, pattern)
        for index in indices:
            try:
                # 获取当前映射
                current_mapping = es_client.indices.get_mapping(index=index)
                # 更新映射
                response = es_client.indices.put_mapping(
                    index=index,
                    body=template_body.get('mappings', {})
                )
                updated_indices.append(index)
                print(f"✅ 索引 {index} 映射更新成功")
            except Exception as e:
                print(f"❌ 索引 {index} 映射更新失败: {e}")

    return updated_indices

def main():
    parser = argparse.ArgumentParser(description='ES模板管理工具')
    parser.add_argument('--action', choices=['apply', 'list', 'delete', 'update_indices'],
                       default='list', help='操作类型')
    parser.add_argument('--template', help='模板名称')
    parser.add_argument('--template-file', help='模板文件路径')
    parser.add_argument('--update-existing', action='store_true',
                       help='是否更新现有索引的映射')

    args = parser.parse_args()

    es_client = get_es_client()

    if args.action == 'list':
        list_templates(es_client)

    elif args.action == 'apply':
        if not args.template_file:
            print("❌ 请指定模板文件路径 (--template-file)")
            return

        template_path = Path(args.template_file)
        if not template_path.exists():
            print(f"❌ 模板文件不存在: {template_path}")
            return

        template_body = load_template(template_path)
        template_name = args.template or template_path.stem.replace('_template', '')

        print(f"正在应用模板: {template_name}")
        response = apply_template(es_client, template_name, template_body)

        if response and args.update_existing:
            print("正在更新现有索引...")
            updated_indices = update_existing_indices(es_client, template_body)
            if updated_indices:
                print(f"更新的索引: {', '.join(updated_indices)}")

    elif args.action == 'delete':
        if not args.template:
            print("❌ 请指定要删除的模板名称 (--template)")
            return

        delete_template(es_client, args.template)

    elif args.action == 'update_indices':
        if not args.template_file:
            print("❌ 请指定模板文件路径 (--template-file)")
            return

        template_body = load_template(args.template_file)
        print("正在更新现有索引...")
        updated_indices = update_existing_indices(es_client, template_body)
        if updated_indices:
            print(f"更新的索引: {', '.join(updated_indices)}")

if __name__ == "__main__":
    main()
