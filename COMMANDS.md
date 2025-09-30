# RAGForge Shell 命令参考

本文档提供了 RAGForge Shell 所有可用命令的详细参考。

## 命令概览

| 命令组 | 功能 | 主要命令 |
|--------|------|----------|
| `user` | 用户管理 | `login`, `logout`, `register`, `info`, `setting` |
| `system` | 系统管理 | `status`, `version`, `config`, `new-token`, `token-list` |
| `datasets` | 数据集管理 | `list`, `show`, `create`, `update`, `delete` |
| `documents` | 文档管理 | `list`, `show`, `upload`, `parse`, `status`, `parse-all` |
| `chunks` | 文档块管理 | `list`, `show`, `add`, `update`, `delete` |
| `retrieval` | 检索功能 | `search`, `search-all` |
| `debug` | 调试工具 | `test-api`, `check-connection`, `api-call` |
| `compare` | 文件比较 | `files`, `quick` |

## 用户管理命令 (user)

### 用户认证
```bash
uv run python main.py user login <username> <password>    # 用户登录
uv run python main.py user logout                         # 用户登出
uv run python main.py user register <username> <password> # 用户注册
uv run python main.py user status                         # 查看登录状态
```

### 用户信息
```bash
uv run python main.py user info                           # 获取用户信息
uv run python main.py user setting <email> <nickname>     # 更新用户设置
uv run python main.py user set-tenant-info <tenant_info>  # 设置租户信息
```

### 第三方登录
```bash
uv run python main.py user feishu-callback <code>         # 飞书登录回调
uv run python main.py user github-callback <code>         # GitHub登录回调
```

## 系统管理命令 (system)

### 系统信息
```bash
uv run python main.py system status                       # 系统状态
uv run python main.py system version                      # 系统版本
uv run python main.py system config                       # 系统配置
uv run python main.py system interface-config             # 接口配置
```

### 令牌管理
```bash
uv run python main.py system new-token                    # 生成新令牌
uv run python main.py system token-info <token>           # 令牌信息
uv run python main.py system token-list                   # 令牌列表
```

### 文件上传
```bash
uv run python main.py system upload-interface <file_path> # 上传接口文件
```

## 数据集管理命令 (datasets)

### 基本操作
```bash
uv run python main.py datasets list                       # 数据集列表
uv run python main.py datasets show <dataset_id>          # 查看数据集
uv run python main.py datasets create <name>              # 创建数据集
uv run python main.py datasets update <dataset_id> <name> # 更新数据集
uv run python main.py datasets delete <dataset_id>        # 删除数据集
```

### 选项参数
- `--description <text>`: 数据集描述
- `--format <format>`: 输出格式 (table, json, yaml, simple)

## 文档管理命令 (documents)

### 文档操作
```bash
uv run python main.py documents list <dataset_id>         # 文档列表
uv run python main.py documents show <dataset_id> <document_id> # 查看文档
uv run python main.py documents create <dataset_id> <name> # 创建文档
uv run python main.py documents upload <dataset_id> --file <file_path> # 上传文档
uv run python main.py documents update <dataset_id> <document_id> <name> # 更新文档
uv run python main.py documents delete <dataset_id> <document_id> # 删除文档
```

### 文档解析
```bash
uv run python main.py documents parse <dataset_id> <document_id>      # 启动解析
uv run python main.py documents status <dataset_id> <document_id>     # 查看状态
uv run python main.py documents parse-all <dataset_id>                # 批量解析
```

### 文档块
```bash
uv run python main.py documents chunks <dataset_id> <document_id>     # 查看文档块
```

### 选项参数
- `--content <text>`: 文档内容
- `--file <path>`: 文件路径
- `--format <format>`: 输出格式

## 文档块管理命令 (chunks)

### 块操作
```bash
uv run python main.py chunks list <dataset_id> <document_id>         # 块列表
uv run python main.py chunks show <dataset_id> <document_id> <chunk_id> # 查看块
uv run python main.py chunks add <dataset_id> <document_id> <content> # 添加块
uv run python main.py chunks update <dataset_id> <document_id> <chunk_id> # 更新块
uv run python main.py chunks delete <dataset_id> <document_id> <chunk_id> # 删除块
```

### 选项参数
- `--keywords <text>`: 关键词
- `--format <format>`: 输出格式

## 检索功能命令 (retrieval)

### 检索操作
```bash
uv run python main.py retrieval search "查询内容" <dataset_id>        # 单数据集检索
uv run python main.py retrieval search-all "查询内容"                  # 多数据集检索
```

### 高级选项
- `--top-k <number>`: 返回的最大块数量 (默认: 10)
- `--similarity-threshold <float>`: 相似度阈值 (0-1)
- `--vector-similarity-weight <float>`: 向量相似度权重
- `--highlight`: 高亮匹配内容
- `--document-ids <ids>`: 限制检索的文档ID列表

## 调试功能命令 (debug)

### 调试工具
```bash
uv run python main.py debug test-api                      # API测试
uv run python main.py debug check-connection              # 连接检查
uv run python main.py debug api-call <method> <endpoint> # 原始API调用
```

### 配置工具
```bash
uv run python main.py config-show                         # 显示配置
uv run python main.py api-list                            # API列表
uv run python main.py version                             # 版本信息
```

## 输出格式

所有命令都支持以下输出格式：

- `table`: 表格格式（默认）
- `json`: JSON格式
- `yaml`: YAML格式
- `simple`: 简单列表格式

### 使用示例
```bash
# 表格格式
uv run python main.py datasets list

# JSON格式
uv run python main.py datasets list --format json

# 简单列表
uv run python main.py datasets list --format simple
```

## 常用工作流程

### 1. 完整文档处理流程
```bash
# 1. 检查系统状态
uv run python main.py system status

# 2. 查看数据集
uv run python main.py datasets list

# 3. 上传文档
uv run python main.py documents upload <dataset_id> --file <file_path>

# 4. 启动解析
uv run python main.py documents parse <dataset_id> <document_id>

# 5. 监控状态
uv run python main.py documents status <dataset_id> <document_id>

# 6. 检索内容
uv run python main.py retrieval search "查询内容" <dataset_id>
```

### 2. 批量文档处理
```bash
# 批量启动解析
uv run python main.py documents parse-all <dataset_id>

# 查看所有文档状态
uv run python main.py documents list <dataset_id> --format json | jq '.data.docs[] | {id, name, run, progress}'
```

### 3. 多数据集检索
```bash
# 跨数据集检索
uv run python main.py retrieval search-all "查询内容" --top-k 20 --similarity-threshold 0.8
```

## 错误处理

### 常见错误及解决方案

1. **认证错误**
   ```bash
   # 重新登录
   uv run python main.py user login <username> <password>
   ```

2. **连接错误**
   ```bash
   # 检查连接
   uv run python main.py debug check-connection
   ```

3. **参数错误**
   ```bash
   # 查看命令帮助
   uv run python main.py <command> --help
   ```

## 高级用法

### 脚本集成
```bash
#!/bin/bash
# 自动化文档处理脚本

DATASET_ID="your_dataset_id"
FILE_PATH="your_file_path"

# 上传文档
uv run python main.py documents upload $DATASET_ID --file $FILE_PATH

# 获取文档ID
DOC_ID=$(uv run python main.py documents list $DATASET_ID --format json | jq -r '.data.docs[0].id')

# 启动解析
uv run python main.py documents parse $DATASET_ID $DOC_ID

# 监控解析进度
while true; do
    STATUS=$(uv run python main.py documents status $DATASET_ID $DOC_ID --format json | jq -r '.run')
    if [ "$STATUS" = "DONE" ]; then
        echo "解析完成！"
        break
    fi
    sleep 10
done
```

### 批量操作
```bash
# 批量创建文档
for file in *.pdf; do
    uv run python main.py documents upload <dataset_id> --file "$file"
done

# 批量启动解析
uv run python main.py documents parse-all <dataset_id>
```

## 文件比较命令 (compare)

### 文件比较功能
```bash
# 详细比较文件
python3 main.py compare files <待上传文件> <已上传文件>

# 快速比较（简化输出）
python3 main.py compare quick <待上传文件> <已上传文件>

# 比较并保存报告
python3 main.py compare files <待上传文件> <已上传文件> --output report.txt

# 指定输出格式
python3 main.py compare files <待上传文件> <已上传文件> --format json
python3 main.py compare files <待上传文件> <已上传文件> --format yaml
```

### 使用示例
```bash
# 比较中文图书文件和已上传文件清单
python3 main.py compare files /root/中文图书 /root/ragforge-shell/upload_file.txt

# 快速查看比较结果
python3 main.py compare quick /root/中文图书 /root/ragforge-shell/upload_file.txt

# 生成详细报告
python3 main.py compare files /root/中文图书 /root/ragforge-shell/upload_file.txt --output missing_files.txt
```

### 功能特点
- **智能匹配**: 支持文件名格式差异的模糊匹配
- **多种输出格式**: 支持表格、JSON、YAML等格式
- **详细统计**: 提供匹配率、文件数量等统计信息
- **报告生成**: 可生成详细的比较报告文件
- **进度显示**: 处理大量文件时显示进度 