# RAGForge Shell

一个功能完整的 RAGForge 命令行工具，提供数据集管理、文档上传、解析、检索和文件比较等完整功能。

## ✨ 功能特性

### 🚀 核心功能
- **用户管理**: 登录、注册、密码管理、第三方登录
- **系统管理**: 系统状态、版本信息、令牌管理、文件上传
- **数据集管理**: 创建、查看、更新、删除数据集
- **文档管理**: 上传、解析、查看、删除文档
- **检索功能**: 多数据集检索、单数据集检索、单文档检索
- **文件比较**: 智能比较待上传文件和已上传文件清单
- **调试工具**: API测试、连接检查、原始调用

### 📁 支持的文件格式
- **PDF**: Adobe PDF文档
- **Word**: Microsoft Word文档 (.doc, .docx)
- **文本**: 纯文本文件 (.txt, .md)
- **其他**: 根据系统配置支持更多格式

### 🔍 文件比较功能
- **智能匹配**: 支持文件名格式差异的模糊匹配
- **多种输出格式**: 支持表格、JSON、YAML等格式
- **详细统计**: 提供匹配率、文件数量等统计信息
- **报告生成**: 可生成详细的比较报告文件
- **进度显示**: 处理大量文件时显示进度

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装依赖包
uv pip install -r requirements.txt
```

### 2. 配置认证

编辑 `config.yaml` 文件，设置你的 RAGForge API 信息（其他配置在登录之后会自动更新）：

```yaml
api:
  base_url: http://localhost:9380
```

### 3. 基本使用

#### 用户登录
```bash
# 用户登录
uv run python main.py user login <username> <password>

# 查看数据集列表
uv run python main.py datasets list

# 查看数据集文档列表
uv run python main.py documents list <dataset_id>
```

#### 基本操作
```bash
# 检查系统状态
uv run python main.py system status

# 上传文档
uv run python main.py documents upload <dataset_id> --file <file_path>

# 启动文档解析
uv run python main.py documents parse <dataset_id> <document_id>

# 检索文档内容
uv run python main.py retrieval search "查询内容" <dataset_id>

# 比较文件（新功能）
python3 main.py compare files <待上传文件> <已上传文件>
```

## 完整工作流程

### 1. 系统检查
```bash
# 检查系统状态
uv run python main.py system status

# 查看数据集列表
uv run python main.py datasets list
```

### 2. 文档上传
```bash
# 上传文档到数据集
uv run python main.py documents upload <dataset_id> --file <file_path>

# 查看上传结果
uv run python main.py documents list <dataset_id>
```

### 3. 文档解析
```bash
# 启动文档解析
uv run python main.py documents parse <dataset_id> <document_id>

# 查看解析状态
uv run python main.py documents status <dataset_id> <document_id>

# 批量启动解析
uv run python main.py documents parse-all <dataset_id>
```

### 4. 内容检索
```bash
# 检索文档内容
uv run python main.py retrieval search "查询内容" <dataset_id>
```

### 5. 文件比较（可选）
```bash
# 比较待上传文件和已上传文件清单
python3 main.py compare files <待上传文件> <已上传文件>

# 快速查看未上传的文件
python3 main.py compare quick <待上传文件> <已上传文件>

# 生成详细报告
python3 main.py compare files <待上传文件> <已上传文件> --output report.txt
```

## 文档解析状态

文档有以下几种解析状态：

- **UNSTART**: 未开始解析 (对应后端 TaskStatus.UNSTART = "0")
- **RUNNING**: 正在解析中 (对应后端 TaskStatus.RUNNING = "1")
- **CANCEL**: 已取消 (对应后端 TaskStatus.CANCEL = "2")
- **DONE**: 解析完成 (对应后端 TaskStatus.DONE = "3")
- **FAIL**: 解析失败 (对应后端 TaskStatus.FAIL = "4")

## 使用示例

### 示例1: 完整工作流程

```bash
# 1. 检查系统状态
uv run python main.py system status

# 2. 查看数据集
uv run python main.py datasets list

# 3. 上传文档
uv run python main.py documents upload 083591d662c911f08ba44a90b26523d1 --file my_document.pdf

# 4. 启动解析
uv run python main.py documents parse 083591d662c911f08ba44a90b26523d1 <document_id>

# 5. 监控解析进度
uv run python main.py documents status 083591d662c911f08ba44a90b26523d1 <document_id>

# 6. 检索内容
uv run python main.py retrieval search "文档内容" 083591d662c911f08ba44a90b26523d1
```

### 示例2: 批量处理

```bash
# 批量启动所有未解析文档
uv run python main.py documents parse-all <dataset_id>

# 查看所有文档状态
uv run python main.py documents list <dataset_id> --format json | jq '.data.docs[] | {id, name, run, progress}'
```

### 示例3: 文件比较

```bash
# 比较待上传文件和已上传文件清单
python3 main.py compare files /path/to/pending.txt /path/to/uploaded.txt

# 快速查看比较结果
python3 main.py compare quick /path/to/pending.txt /path/to/uploaded.txt

# 生成详细报告
python3 main.py compare files /path/to/pending.txt /path/to/uploaded.txt --output missing_files.txt

# JSON格式输出
python3 main.py compare files /path/to/pending.txt /path/to/uploaded.txt --format json
```

### 示例4: 自动化脚本

```bash
# 运行完整的文件上传演示
uv run python examples/file_upload_example.py

# 使用简单上传脚本
uv run python examples/simple_upload.py <dataset_id> <file_path>
```

## 命令参考

### 用户管理 (user)
```bash
uv run python main.py user login <username> <password>    # 用户登录
uv run python main.py user logout                         # 用户登出
uv run python main.py user register <username> <password> # 用户注册
uv run python main.py user info                           # 获取用户信息
uv run python main.py user setting <email> <nickname>     # 更新用户设置
```

### 系统管理 (system)
```bash
uv run python main.py system status                       # 系统状态
uv run python main.py system version                      # 系统版本
uv run python main.py system config                       # 系统配置
uv run python main.py system new-token                    # 生成新令牌
uv run python main.py system token-list                   # 令牌列表
```

### 数据集管理 (datasets)
```bash
uv run python main.py datasets list                       # 数据集列表
uv run python main.py datasets show <dataset_id>          # 查看数据集
uv run python main.py datasets create <name>              # 创建数据集
uv run python main.py datasets delete <dataset_id>        # 删除数据集
```

### 文档管理 (documents)
```bash
uv run python main.py documents list <dataset_id>         # 文档列表
uv run python main.py documents upload <dataset_id> --file <file_path> # 上传文档
uv run python main.py documents parse <dataset_id> <document_id>      # 启动解析
uv run python main.py documents status <dataset_id> <document_id>     # 查看状态
uv run python main.py documents parse-all <dataset_id>                # 批量解析
```

### 检索功能 (retrieval)
```bash
uv run python main.py retrieval search "查询内容" <dataset_id>        # 检索内容
uv run python main.py retrieval search-all "查询内容"                  # 多数据集检索
```

### 文件比较 (compare)
```bash
python3 main.py compare files <待上传文件> <已上传文件>    # 详细比较文件
python3 main.py compare quick <待上传文件> <已上传文件>    # 快速比较（简化输出）
python3 main.py compare files <待上传文件> <已上传文件> --output report.txt  # 生成报告
python3 main.py compare files <待上传文件> <已上传文件> --format json        # JSON格式输出
```

### 调试功能 (debug)
```bash
uv run python main.py debug test-api                      # API测试
uv run python main.py debug check-connection              # 连接检查
uv run python main.py debug api-call <method> <endpoint> # 原始API调用
```

## 📁 目录结构

```
ragforge-shell/
├── main.py                    # 主入口脚本
├── api_client.py              # API客户端封装
├── password_utils.py          # 密码加密工具
├── reset_password.py          # 密码重置工具
├── config.yaml                # 配置文件
├── requirements.txt           # 依赖包列表
├── commands/                  # 命令模块目录
│   ├── datasets.py           # 数据集管理命令
│   ├── documents.py          # 文档管理命令
│   ├── chunks.py             # 文档块管理命令
│   ├── retrieval.py          # 检索功能命令
│   ├── user.py               # 用户管理命令
│   ├── system.py             # 系统管理命令
│   ├── compare.py            # 文件比较命令 ⭐
│   └── debug.py              # 调试命令
├── utils/                    # 工具函数目录
│   └── output.py             # 输出格式化工具
├── examples/                 # 示例脚本目录
│   ├── file_upload_example.py # 完整文件上传演示
│   └── simple_upload.py      # 简单文件上传脚本
└── 文档文件
    ├── README.md             # 主文档
    ├── COMMANDS.md           # 命令参考文档
    └── PROJECT_CLEANUP.md    # 项目整理总结
```

> ⭐ 标记表示新增的文件比较功能

## ⚙️ 配置说明

### config.yaml 配置

```yaml
api:
  api_token: your-api-token      # API令牌
  auth_token: your-auth-token    # 认证令牌
  base_url: http://localhost:9380 # API基础URL
  headers:
    Accept: application/json
    Content-Type: application/json
  timeout: 30
logging:
  format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  level: INFO
output:
  format: table                  # 输出格式: table, json, yaml, simple
  max_width: 120
```

### 📊 输出格式

支持多种输出格式：
- `table`: 表格格式（默认）
- `json`: JSON格式
- `yaml`: YAML格式
- `simple`: 简单列表格式

## 🔧 故障排除

### 常见问题

1. **模块未找到错误**
   ```bash
   # 确保使用uv运行
   uv run python main.py <command>
   ```

2. **认证错误**
   - 检查 `config.yaml` 中的令牌配置
   - 确保令牌有效且未过期

3. **API连接错误**
   - 检查 `base_url` 配置
   - 确保RAGForge服务正在运行

4. **文档解析状态不更新**
   - 解析是异步过程，需要等待
   - 使用 `documents status` 命令监控进度

5. **文件比较错误**
   - 确保文件路径正确且文件存在
   - 检查文件编码格式（建议使用UTF-8）

### 调试命令

```bash
# 测试API连接
uv run python main.py debug test-api

# 检查连接状态
uv run python main.py debug check-connection

# 查看系统状态
uv run python main.py system status

# 测试文件比较功能
python3 main.py compare --help
```

## 👨‍💻 开发说明

### 添加新命令

1. 在 `commands/` 目录下创建新的命令模块
2. 在 `main.py` 中导入并注册新命令
3. 更新 `COMMANDS.md` 文档

### 测试命令

```bash
# 运行所有命令测试
uv run python main.py --help

# 测试特定命令
uv run python main.py <command> --help

# 测试文件比较功能
python3 main.py compare files --help
```

## 📄 许可证

本项目基于 Apache License 2.0 开源协议。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

---

## 🆕 最新更新

### v1.1.0 - 文件比较功能
- ✅ 新增 `compare` 命令组
- ✅ 支持智能文件比较和匹配
- ✅ 多种输出格式支持
- ✅ 详细统计和报告生成 