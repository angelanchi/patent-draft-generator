# AI专利文件生成器 - 快速部署脚本 (Windows PowerShell)
# 支持 Railway, Render, Heroku 等平台

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "AI专利文件生成器 - 快速部署向导" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 git 状态
try {
    git rev-parse --git-dir | Out-Null
} catch {
    Write-Host "错误：当前目录不是 Git 仓库" -ForegroundColor Red
    exit 1
}

# 检查是否有未提交的更改
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "警告：您有未提交的更改" -ForegroundColor Yellow
    $commit = Read-Host "是否先提交更改？(y/n)"
    if ($commit -eq 'y') {
        git add .
        $commitMsg = Read-Host "请输入提交信息"
        git commit -m $commitMsg
    }
}

# 选择部署平台
Write-Host "请选择部署平台：" -ForegroundColor Green
Write-Host "1) Railway (推荐，免费 `$5/月)"
Write-Host "2) Render (免费 750 小时/月)"
Write-Host "3) Heroku (需要信用卡，`$7/月起)"
Write-Host "4) 仅推送到 GitHub"
Write-Host ""
$platform = Read-Host "请输入选项 (1-4)"

switch ($platform) {
    "1" {
        Write-Host ""
        Write-Host "=== Railway 部署 ===" -ForegroundColor Cyan
        Write-Host ""

        # 检查 Railway CLI
        $railwayExists = Get-Command railway -ErrorAction SilentlyContinue
        if (-not $railwayExists) {
            Write-Host "Railway CLI 未安装。正在安装..." -ForegroundColor Yellow
            npm i -g @railway/cli
        }

        Write-Host "正在登录 Railway..."
        railway login

        Write-Host "正在初始化项目..."
        railway init

        Write-Host ""
        Write-Host "请在 Railway Dashboard 设置以下环境变量：" -ForegroundColor Yellow
        Write-Host "  OPENAI_API_KEY=你的OpenAI密钥"
        Write-Host "  SECRET_KEY=你的Flask密钥"
        Write-Host "  FLASK_ENV=production"
        Write-Host ""
        Read-Host "设置完成后按 Enter 继续"

        Write-Host "正在部署..."
        railway up

        Write-Host ""
        Write-Host "部署完成！" -ForegroundColor Green
        Write-Host "查看日志: railway logs"
        Write-Host "打开应用: railway open"
    }

    "2" {
        Write-Host ""
        Write-Host "=== Render 部署 ===" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "请按照以下步骤在 Render 部署：" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "1. 访问 https://render.com"
        Write-Host "2. 使用 GitHub 账户登录"
        Write-Host "3. 点击 'New +' -> 'Web Service'"
        Write-Host "4. 连接此 GitHub 仓库"
        Write-Host "5. 配置如下："
        Write-Host "   - Build Command: pip install -r requirements.txt"
        Write-Host "   - Start Command: gunicorn run:app --bind 0.0.0.0:`$PORT --timeout 300 --workers 2"
        Write-Host "6. 添加环境变量（见 DEPLOYMENT.md）"
        Write-Host "7. 点击 'Create Web Service'"
        Write-Host ""
        Write-Host "详细步骤请查看 DEPLOYMENT.md"

        # 询问是否打开浏览器
        $openBrowser = Read-Host "是否打开 Render 网站？(y/n)"
        if ($openBrowser -eq 'y') {
            Start-Process "https://render.com"
        }
    }

    "3" {
        Write-Host ""
        Write-Host "=== Heroku 部署 ===" -ForegroundColor Cyan
        Write-Host ""

        # 检查 Heroku CLI
        $herokuExists = Get-Command heroku -ErrorAction SilentlyContinue
        if (-not $herokuExists) {
            Write-Host "错误：Heroku CLI 未安装" -ForegroundColor Red
            Write-Host "请访问 https://devcenter.heroku.com/articles/heroku-cli 安装"
            $openBrowser = Read-Host "是否打开下载页面？(y/n)"
            if ($openBrowser -eq 'y') {
                Start-Process "https://devcenter.heroku.com/articles/heroku-cli"
            }
            exit 1
        }

        Write-Host "正在登录 Heroku..."
        heroku login

        $appName = Read-Host "请输入应用名称（留空自动生成）"

        if ([string]::IsNullOrWhiteSpace($appName)) {
            heroku create
        } else {
            heroku create $appName
        }

        Write-Host ""
        Write-Host "请设置环境变量：" -ForegroundColor Yellow
        $openaiKey = Read-Host "OpenAI API Key"
        $secretKey = Read-Host "Flask Secret Key (留空自动生成)"

        if ([string]::IsNullOrWhiteSpace($secretKey)) {
            $secretKey = -join ((1..64) | ForEach-Object { '{0:x}' -f (Get-Random -Maximum 16) })
        }

        heroku config:set OPENAI_API_KEY="$openaiKey"
        heroku config:set SECRET_KEY="$secretKey"
        heroku config:set FLASK_ENV=production
        heroku config:set OPENAI_MODEL=gpt-4-turbo

        Write-Host ""
        Write-Host "正在部署..."
        git push heroku master

        Write-Host ""
        Write-Host "部署完成！" -ForegroundColor Green
        Write-Host "打开应用: heroku open"
        Write-Host "查看日志: heroku logs --tail"
    }

    "4" {
        Write-Host ""
        Write-Host "=== GitHub 推送 ===" -ForegroundColor Cyan
        Write-Host ""

        # 检查是否已有远程仓库
        try {
            $remoteUrl = git remote get-url origin
            Write-Host "远程仓库已存在: $remoteUrl" -ForegroundColor Green
            $push = Read-Host "是否推送到此仓库？(y/n)"
            if ($push -eq 'y') {
                git push origin master
                Write-Host "代码已推送到 GitHub" -ForegroundColor Green
            }
        } catch {
            Write-Host "未检测到远程仓库" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "请按照以下步骤操作：" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "1. 访问 https://github.com/new 创建新仓库"
            Write-Host "2. 仓库名称建议使用: IP-generator"
            Write-Host "3. 选择 Private（推荐）或 Public"
            Write-Host "4. 不要勾选任何初始化选项"
            Write-Host "5. 创建后，在下方输入仓库 URL"
            Write-Host ""

            $createNew = Read-Host "是否打开 GitHub 创建仓库页面？(y/n)"
            if ($createNew -eq 'y') {
                Start-Process "https://github.com/new"
            }

            Write-Host ""
            $repoUrl = Read-Host "请输入 GitHub 仓库 URL (例如: https://github.com/username/IP-generator.git)"

            if (![string]::IsNullOrWhiteSpace($repoUrl)) {
                git remote add origin $repoUrl
                git push -u origin master
                Write-Host ""
                Write-Host "代码已推送到 GitHub！" -ForegroundColor Green
            }
        }
    }

    default {
        Write-Host "无效的选项" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "部署向导完成！" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步：" -ForegroundColor Green
Write-Host "1. 访问应用 URL 测试功能"
Write-Host "2. 查看 DEPLOYMENT.md 了解更多配置选项"
Write-Host "3. 监控日志确保应用正常运行"
Write-Host ""
Write-Host "快速命令：" -ForegroundColor Yellow
Write-Host "  查看完整文档: cat DEPLOYMENT.md"
Write-Host "  运行测试: python test_patent_generation.py"
Write-Host "  本地运行: python run.py"
Write-Host ""
