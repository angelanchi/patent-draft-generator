# 部署指南

本文档提供将 AI 专利文件生成器部署到各种云平台的详细步骤。

## 目录

- [准备工作](#准备工作)
- [方案 1: Railway 部署（推荐）](#方案-1-railway-部署推荐)
- [方案 2: Render 部署](#方案-2-render-部署)
- [方案 3: Heroku 部署](#方案-3-heroku-部署)
- [方案 4: Azure App Service 部署](#方案-4-azure-app-service-部署)
- [环境变量配置](#环境变量配置)
- [部署后验证](#部署后验证)
- [故障排除](#故障排除)

---

## 准备工作

### 1. 确保代码已推送到 GitHub

```bash
# 检查远程仓库
git remote -v

# 如果没有远程仓库，添加
git remote add origin https://github.com/您的用户名/IP-generator.git

# 推送代码
git push -u origin master
```

### 2. 准备 OpenAI API 密钥

访问 https://platform.openai.com/api-keys 获取 API 密钥。

### 3. 准备 Flask Secret Key

在 Python 中生成：
```python
import secrets
print(secrets.token_hex(32))
```

---

## 方案 1: Railway 部署（推荐）

Railway 提供免费额度，配置简单，支持自动部署。

### 优点
- 免费额度：每月 $5 credit
- 自动从 GitHub 部署
- 支持环境变量管理
- 提供自定义域名

### 部署步骤

1. **访问 Railway**
   - 前往 https://railway.app
   - 使用 GitHub 账户登录

2. **创建新项目**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择 `IP-generator` 仓库

3. **配置环境变量**
   - 在项目设置中，点击 "Variables"
   - 添加以下环境变量：
     ```
     OPENAI_API_KEY=你的OpenAI密钥
     SECRET_KEY=你的Flask密钥
     FLASK_ENV=production
     OPENAI_MODEL=gpt-4-turbo
     OPENAI_MAX_TOKENS=2000
     OPENAI_TEMPERATURE=0.7
     OUTPUT_DIR=/tmp/output
     UPLOAD_DIR=/tmp/uploads
     PORT=8080
     ```

4. **部署**
   - Railway 会自动检测 Python 项目
   - 自动安装依赖并启动应用
   - 等待部署完成（约 2-3 分钟）

5. **获取 URL**
   - 部署成功后，Railway 会提供一个 URL
   - 格式：`https://your-app.railway.app`

### Railway CLI 部署（可选）

```bash
# 安装 Railway CLI
npm i -g @railway/cli

# 登录
railway login

# 初始化项目
railway init

# 部署
railway up

# 查看日志
railway logs
```

---

## 方案 2: Render 部署

Render 提供慷慨的免费层，适合小型项目。

### 优点
- 免费层：750 小时/月
- 自动 SSL 证书
- 支持自定义域名
- 自动从 Git 部署

### 部署步骤

1. **访问 Render**
   - 前往 https://render.com
   - 使用 GitHub 账户注册/登录

2. **创建 Web Service**
   - 点击 "New +" → "Web Service"
   - 连接 GitHub 仓库 `IP-generator`

3. **配置服务**
   - **Name**: `ip-generator`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app --bind 0.0.0.0:$PORT --timeout 300 --workers 2`
   - **Plan**: Free

4. **添加环境变量**
   在 "Environment" 标签页添加：
   ```
   OPENAI_API_KEY=你的OpenAI密钥
   SECRET_KEY=你的Flask密钥
   FLASK_ENV=production
   OPENAI_MODEL=gpt-4-turbo
   OUTPUT_DIR=/tmp/output
   UPLOAD_DIR=/tmp/uploads
   ```

5. **部署**
   - 点击 "Create Web Service"
   - Render 会自动构建和部署
   - 等待部署完成（约 5-10 分钟）

6. **访问应用**
   - URL 格式：`https://ip-generator.onrender.com`

### 注意事项
- 免费层应用在无活动 15 分钟后会休眠
- 首次访问可能需要等待 30-60 秒唤醒

---

## 方案 3: Heroku 部署

Heroku 是老牌 PaaS 平台，配置成熟。

### 优点
- 成熟的生态系统
- 丰富的插件市场
- 详细的文档

### 注意
- Heroku 已取消免费层（需要信用卡）
- 基础套餐：$7/月

### 部署步骤

1. **安装 Heroku CLI**
   ```bash
   # Windows (使用 Chocolatey)
   choco install heroku-cli

   # 或下载安装器
   # https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **登录 Heroku**
   ```bash
   heroku login
   ```

3. **创建 Heroku 应用**
   ```bash
   heroku create ip-generator-你的名字
   ```

4. **设置环境变量**
   ```bash
   heroku config:set OPENAI_API_KEY=你的OpenAI密钥
   heroku config:set SECRET_KEY=你的Flask密钥
   heroku config:set FLASK_ENV=production
   heroku config:set OPENAI_MODEL=gpt-4-turbo
   heroku config:set OUTPUT_DIR=/tmp/output
   heroku config:set UPLOAD_DIR=/tmp/uploads
   ```

5. **部署**
   ```bash
   git push heroku master
   ```

6. **打开应用**
   ```bash
   heroku open
   ```

7. **查看日志**
   ```bash
   heroku logs --tail
   ```

---

## 方案 4: Azure App Service 部署

适合企业用户或需要与 Azure 其他服务集成的场景。

### 优点
- 企业级支持
- 与 Azure 生态系统集成
- 高可用性选项

### 部署步骤

1. **安装 Azure CLI**
   ```bash
   # Windows
   # 下载并安装：https://aka.ms/installazurecliwindows
   ```

2. **登录 Azure**
   ```bash
   az login
   ```

3. **创建资源组**
   ```bash
   az group create --name ip-generator-rg --location eastasia
   ```

4. **创建 App Service Plan**
   ```bash
   az appservice plan create --name ip-generator-plan \
       --resource-group ip-generator-rg \
       --sku B1 --is-linux
   ```

5. **创建 Web App**
   ```bash
   az webapp create --name ip-generator-你的名字 \
       --resource-group ip-generator-rg \
       --plan ip-generator-plan \
       --runtime "PYTHON:3.11"
   ```

6. **配置部署**
   ```bash
   az webapp deployment source config --name ip-generator-你的名字 \
       --resource-group ip-generator-rg \
       --repo-url https://github.com/你的用户名/IP-generator \
       --branch master --manual-integration
   ```

7. **设置环境变量**
   ```bash
   az webapp config appsettings set --name ip-generator-你的名字 \
       --resource-group ip-generator-rg \
       --settings OPENAI_API_KEY=你的密钥 \
                  SECRET_KEY=你的Flask密钥 \
                  FLASK_ENV=production
   ```

8. **访问应用**
   - URL: `https://ip-generator-你的名字.azurewebsites.net`

---

## 环境变量配置

所有平台都需要配置以下环境变量：

### 必需变量

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | `sk-...` |
| `SECRET_KEY` | Flask 会话密钥 | `生成的随机字符串` |
| `FLASK_ENV` | Flask 运行环境 | `production` |

### 可选变量（使用默认值）

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `OPENAI_MODEL` | `gpt-4-turbo` | OpenAI 模型 |
| `OPENAI_MAX_TOKENS` | `2000` | 最大 token 数 |
| `OPENAI_TEMPERATURE` | `0.7` | 生成温度 |
| `OUTPUT_DIR` | `/tmp/output` | 输出目录 |
| `UPLOAD_DIR` | `/tmp/uploads` | 上传目录 |
| `LOG_LEVEL` | `INFO` | 日志级别 |

### 云平台特殊配置

**Railway / Heroku / Render**
```bash
OUTPUT_DIR=/tmp/output
UPLOAD_DIR=/tmp/uploads
```
注：这些平台使用临时文件系统，应用重启后文件会丢失。

**Azure**
```bash
OUTPUT_DIR=/home/output
UPLOAD_DIR=/home/uploads
```
注：Azure 提供持久化存储。

---

## 部署后验证

部署完成后，执行以下检查：

### 1. 健康检查
访问：`https://your-app-url/health`

应返回：
```json
{
  "status": "healthy",
  "service": "IP Generator",
  "version": "1.0.0"
}
```

### 2. 首页访问
访问：`https://your-app-url/`

应显示首页和导航栏。

### 3. API 测试
使用以下命令测试 API：

```bash
curl -X POST https://your-app-url/api/estimate/cost \
  -H "Content-Type: application/json" \
  -d '{
    "patent_name": "测试专利",
    "inventors": "测试人员",
    "keywords": "测试关键字",
    "technical_description": "这是一个测试描述，用于验证 API 是否正常工作。"
  }'
```

### 4. 查看日志

**Railway**
```bash
railway logs
```

**Render**
在 Dashboard → Logs 查看

**Heroku**
```bash
heroku logs --tail
```

**Azure**
```bash
az webapp log tail --name ip-generator-你的名字 --resource-group ip-generator-rg
```

---

## 故障排除

### 问题 1: 应用无法启动

**症状**: 部署成功但应用无法访问

**解决方案**:
1. 检查日志中的错误信息
2. 确认所有必需的环境变量已设置
3. 确认 `requirements.txt` 中的依赖版本兼容

### 问题 2: OpenAI API 错误

**症状**: 生成专利时报错

**解决方案**:
1. 检查 `OPENAI_API_KEY` 是否正确设置
2. 确认 OpenAI 账户有足够余额
3. 检查 API 密钥是否有正确的权限

### 问题 3: 文件上传失败

**症状**: 上传图片时出错

**解决方案**:
1. 确认 `UPLOAD_DIR` 路径正确
2. 云平台使用 `/tmp` 目录（临时存储）
3. 检查文件大小是否超过 `MAX_UPLOAD_SIZE`

### 问题 4: 生成超时

**症状**: 生成专利时超时

**解决方案**:
1. 增加服务器超时设置（Procfile 中的 `--timeout 300`）
2. 使用 `gpt-3.5-turbo` 代替 `gpt-4-turbo`（更快但质量稍低）
3. 减少 `OPENAI_MAX_TOKENS` 值

### 问题 5: 应用休眠（免费层）

**症状**: 首次访问很慢（Render 免费层）

**解决方案**:
1. 使用付费层避免休眠
2. 设置定时任务定期访问应用保持活跃
3. 接受冷启动延迟（30-60 秒）

---

## 成本估算

### Railway
- 免费层：$5 credit/月
- 付费层：$0.000463/GB-hour（约 $10-20/月）

### Render
- 免费层：750 小时/月（足够单应用使用）
- Starter：$7/月（无休眠）

### Heroku
- Basic：$7/月
- Standard：$25-50/月

### Azure
- B1 Plan：约 $13/月
- S1 Plan：约 $74/月

### OpenAI API 成本
- 生成一份完整专利（6 章节）：
  - 使用 GPT-4-turbo：约 $0.15-0.30
  - 使用 GPT-3.5-turbo：约 $0.02-0.05
- 月成本取决于使用量

---

## 推荐配置

### 开发/测试
- 平台：Railway 或 Render 免费层
- 模型：gpt-3.5-turbo
- 成本：免费（仅 OpenAI API 成本）

### 生产环境（低流量）
- 平台：Render Starter 或 Heroku Basic
- 模型：gpt-4-turbo
- 成本：约 $7-10/月 + API 成本

### 生产环境（高流量）
- 平台：Azure Standard 或 AWS
- 模型：gpt-4-turbo
- 成本：约 $50-100/月 + API 成本
- 建议：添加 Redis 缓存、负载均衡

---

## 安全建议

1. **环境变量**
   - 永远不要在代码中硬编码密钥
   - 使用平台的环境变量管理

2. **HTTPS**
   - 所有推荐平台默认提供 SSL/TLS
   - 确保强制使用 HTTPS

3. **速率限制**
   - 在生产环境启用 `ENABLE_RATE_LIMITING=true`
   - 防止 API 滥用

4. **日志**
   - 设置 `LOG_LEVEL=INFO` 或 `WARNING`
   - 避免记录敏感信息

5. **定期更新**
   - 定期更新依赖包：`pip install -U -r requirements.txt`
   - 关注安全公告

---

## 监控与维护

### 日志监控
- 定期检查错误日志
- 监控 API 调用成本

### 性能监控
- 使用平台提供的监控工具
- 跟踪响应时间和资源使用

### 备份
- 定期备份生成的专利文件
- 考虑集成云存储（AWS S3、Azure Blob）

---

## 下一步

部署成功后，您可以：

1. 配置自定义域名
2. 设置 CI/CD 自动部署
3. 添加数据库支持（用户管理、历史记录）
4. 集成云存储（持久化文件）
5. 添加用户认证系统
6. 实现批量生成功能

---

如有问题，请查看：
- [README.md](README.md) - 项目文档
- [QUICKSTART.md](QUICKSTART.md) - 快速开始
- [CONTRIBUTING.md](CONTRIBUTING.md) - 贡献指南
