# Elasticsearch 模板管理指南

## 概述

本文档介绍如何管理 Elasticsearch 索引模板，包括模板的应用、更新和维护。

## 模板工作原理

### 1. 模板生效机制

ES 模板通过以下方式生效：

1. **索引模式匹配**：模板定义 `index_patterns`，当创建新索引时，ES 会自动匹配并应用模板
2. **动态映射**：模板包含映射定义，确定字段类型和分析器
3. **设置配置**：模板包含索引设置（如分片数、刷新间隔等）

```json
{
  "index_patterns": ["authors-v*"],
  "settings": {
    "number_of_shards": 1,
    "refresh_interval": "1h"
  },
  "mappings": {
    "properties": {
      "display_name": {"type": "text"}
    }
  }
}
```

### 2. 模板类型

- **索引模板**：定义索引结构和设置
- **组件模板**：可复用的映射或设置组件
- **组合模板**：组合多个组件模板

## 模板管理工具

项目中提供了 `manage_templates.py` 工具来管理ES模板。

### 安装依赖

```bash
pip install elasticsearch
```

### 基本用法

#### 1. 查看现有模板

```bash
python manage_templates.py --action list
```

#### 2. 应用模板

```bash
# 应用authors模板
python manage_templates.py --action apply \
  --template-file elasticsearch_templates/authors_template.json \
  --template authors

# 应用works模板并更新现有索引
python manage_templates.py --action apply \
  --template-file elasticsearch_templates/works_template.json \
  --update-existing
```

#### 3. 删除模板

```bash
python manage_templates.py --action delete --template authors
```

#### 4. 更新现有索引映射

```bash
python manage_templates.py --action update_indices \
  --template-file elasticsearch_templates/authors_template.json
```

## 手动模板管理

### 使用 REST API

#### 1. 应用模板

```bash
curl -X PUT "localhost:9200/_template/authors" \
  -H 'Content-Type: application/json' \
  -d @elasticsearch_templates/authors_template.json
```

#### 2. 查看模板

```bash
curl -X GET "localhost:9200/_template/authors"
```

#### 3. 删除模板

```bash
curl -X DELETE "localhost:9200/_template/authors"
```

#### 4. 更新现有索引映射

```bash
curl -X PUT "localhost:9200/authors-v8/_mapping" \
  -H 'Content-Type: application/json' \
  -d '{
    "properties": {
      "new_field": {"type": "keyword"}
    }
  }'
```

## 动态模板管理

### 何时需要添加新模板

1. **新实体类型**：如添加新的数据类型（venues、concepts等）
2. **字段变更**：需要修改字段类型或添加新字段
3. **性能优化**：调整分片数、分析器等设置

### 创建新模板步骤

1. **定义模板结构**

```json
{
  "index_patterns": ["new-entity-v*"],
  "settings": {
    "number_of_shards": 1,
    "refresh_interval": "1h",
    "analysis": {
      "normalizer": {
        "lower": {"filter": "lowercase"}
      }
    }
  },
  "mappings": {
    "properties": {
      "id": {"type": "keyword"},
      "name": {"type": "text"},
      "created_date": {"type": "date"}
    }
  }
}
```

2. **保存到模板目录**

```bash
# 保存到 elasticsearch_templates/new_entity_template.json
```

3. **应用模板**

```bash
python manage_templates.py --action apply \
  --template-file elasticsearch_templates/new_entity_template.json
```

## 最佳实践

### 1. 版本控制

- 模板文件应纳入版本控制
- 使用有意义的版本号（如 `authors-v8`）
- 记录模板变更历史

### 2. 索引模式命名

- 使用描述性模式：`authors-v*`, `works-v*`
- 包含版本信息便于升级
- 避免通配符过宽

### 3. 映射设计

- 合理选择字段类型（text vs keyword）
- 设置合适的分析器
- 考虑搜索和聚合需求

### 4. 性能考虑

- 适当的分片数（通常1-3个）
- 合理的刷新间隔
- 考虑只读字段（index: false）

### 5. 向后兼容性

- 模板更新时注意现有数据兼容性
- 使用 `ignore_malformed` 处理异常数据
- 逐步迁移而非一次性变更

## 故障排除

### 常见问题

1. **模板不生效**
   - 检查索引模式匹配
   - 确认模板语法正确
   - 查看ES日志

2. **映射冲突**
   - 新模板与现有索引冲突
   - 使用 `update_existing` 参数更新现有索引

3. **性能问题**
   - 检查分片数设置
   - 调整刷新间隔
   - 优化字段映射

### 监控和维护

- 定期检查模板状态
- 监控索引性能
- 及时更新模板以支持新需求

## 总结

ES 模板是管理索引结构的关键工具，通过合理的模板设计和维护，可以确保：

1. **一致性**：统一的数据结构和设置
2. **可扩展性**：轻松添加新字段和索引
3. **性能优化**：合理的配置提升查询效率
4. **维护便利**：集中管理，易于更新

使用提供的管理工具可以简化模板的日常维护工作。
