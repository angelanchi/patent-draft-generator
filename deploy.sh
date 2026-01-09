#!/bin/bash

# AI专利文件生成器 - 快速部署脚本
# 支持 Railway, Render, Heroku 等平台

set -e

echo "=========================================="
echo "AI专利文件生成器 - 快速部署向导"
echo "=========================================="
echo ""

# 检查 git 状态
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "错误：当前目录不是 Git 仓库"
    exit 1
fi

# 检查是否有未提交的更改
if ! git diff-index --quiet HEAD --; then
    echo "警告：您有未提交的更改"
    read -p "是否先提交更改？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add .
        read -p "请输入提交信息: " commit_msg
        git commit -m "$commit_msg"
    fi
fi

# 选择部署平台
echo "请选择部署平台："
echo "1) Railway (推荐，免费 $5/月)"
echo "2) Render (免费 750 小时/月)"
echo "3) Heroku (需要信用卡，$7/月起)"
echo "4) 仅推送到 GitHub"
echo ""
read -p "请输入选项 (1-4): " platform

case $platform in
    1)
        echo ""
        echo "=== Railway 部署 ==="
        echo ""

        # 检查 Railway CLI
        if ! command -v railway &> /dev/null; then
            echo "Railway CLI 未安装。正在安装..."
            npm i -g @railway/cli
        fi

        echo "正在登录 Railway..."
        railway login

        echo "正在初始化项目..."
        railway init

        echo "请在 Railway Dashboard 设置以下环境变量："
        echo "  OPENAI_API_KEY=你的OpenAI密钥"
        echo "  SECRET_KEY=你的Flask密钥"
        echo "  FLASK_ENV=production"
        echo ""
        read -p "设置完成后按 Enter 继续..."

        echo "正在部署..."
        railway up

        echo ""
        echo "部署完成！"
        echo "查看日志: railway logs"
        echo "打开应用: railway open"
        ;;

    2)
        echo ""
        echo "=== Render 部署 ==="
        echo ""
        echo "请按照以下步骤在 Render 部署："
        echo ""
        echo "1. 访问 https://render.com"
        echo "2. 使用 GitHub 账户登录"
        echo "3. 点击 'New +' -> 'Web Service'"
        echo "4. 连接此 GitHub 仓库"
        echo "5. 配置如下："
        echo "   - Build Command: pip install -r requirements.txt"
        echo "   - Start Command: gunicorn run:app --bind 0.0.0.0:\$PORT --timeout 300 --workers 2"
        echo "6. 添加环境变量（见 DEPLOYMENT.md）"
        echo "7. 点击 'Create Web Service'"
        echo ""
        echo "详细步骤请查看 DEPLOYMENT.md"
        ;;

    3)
        echo ""
        echo "=== Heroku 部署 ==="
        echo ""

        # 检查 Heroku CLI
        if ! command -v heroku &> /dev/null; then
            echo "错误：Heroku CLI 未安装"
            echo "请访问 https://devcenter.heroku.com/articles/heroku-cli 安装"
            exit 1
        fi

        echo "正在登录 Heroku..."
        heroku login

        read -p "请输入应用名称（留空自动生成）: " app_name

        if [ -z "$app_name" ]; then
            heroku create
        else
            heroku create "$app_name"
        fi

        echo ""
        echo "请设置环境变量："
        read -p "OpenAI API Key: " openai_key
        read -p "Flask Secret Key (留空自动生成): " secret_key

        if [ -z "$secret_key" ]; then
            secret_key=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
        fi

        heroku config:set OPENAI_API_KEY="$openai_key"
        heroku config:set SECRET_KEY="$secret_key"
        heroku config:set FLASK_ENV=production
        heroku config:set OPENAI_MODEL=gpt-4-turbo

        echo ""
        echo "正在部署..."
        git push heroku master

        echo ""
        echo "部署完成！"
        echo "打开应用: heroku open"
        echo "查看日志: heroku logs --tail"
        ;;

    4)
        echo ""
        echo "=== GitHub 推送 ==="
        echo ""

        # 检查是否已有远程仓库
        if git remote get-url origin &> /dev/null; then
            echo "远程仓库已存在: $(git remote get-url origin)"
            read -p "是否推送到此仓库？(y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                git push origin master
                echo "代码已推送到 GitHub"
            fi
        else
            echo "请先在 GitHub 创建仓库，然后执行："
            echo ""
            echo "git remote add origin https://github.com/您的用户名/IP-generator.git"
            echo "git push -u origin master"
        fi
        ;;

    *)
        echo "无效的选项"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "部署向导完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 访问应用 URL 测试功能"
echo "2. 查看 DEPLOYMENT.md 了解更多配置选项"
echo "3. 监控日志确保应用正常运行"
echo ""
