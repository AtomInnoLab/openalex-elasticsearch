#!/bin/bash

# ES模板应用脚本
# 用于批量应用或更新所有模板

set -e

echo "🚀 开始应用ES模板..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装"
    exit 1
fi

# 检查模板文件
TEMPLATES_DIR="elasticsearch_templates"
if [ ! -d "$TEMPLATES_DIR" ]; then
    echo "❌ 模板目录不存在: $TEMPLATES_DIR"
    exit 1
fi

# 应用模板函数
apply_template() {
    local template_file="$1"
    local template_name="$2"

    if [ ! -f "$template_file" ]; then
        echo "⚠️  模板文件不存在: $template_file"
        return
    fi

    echo "📝 正在应用模板: $template_name"

    if python3 manage_templates.py --action apply \
        --template-file "$template_file" \
        --template "$template_name" \
        --update-existing; then
        echo "✅ 模板 $template_name 应用成功"
    else
        echo "❌ 模板 $template_name 应用失败"
    fi
}

# 应用所有模板
echo "📋 发现的模板文件:"
ls -la "$TEMPLATES_DIR"/*.json

# 应用authors模板
apply_template "$TEMPLATES_DIR/authors_template.json" "authors"

# 应用works模板
apply_template "$TEMPLATES_DIR/works_template.json" "works"

# 应用其他模板（如果存在）
if [ -f "$TEMPLATES_DIR/venues_template.json" ] && [ -s "$TEMPLATES_DIR/venues_template.json" ]; then
    apply_template "$TEMPLATES_DIR/venues_template.json" "venues"
else
    echo "⚠️  venues_template.json 不存在或为空，跳过"
fi

echo "🎉 模板应用完成!"

# 显示当前模板状态
echo ""
echo "📊 当前模板状态:"
python3 manage_templates.py --action list
