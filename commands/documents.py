import click
from typing import Dict, Any, Optional
from api_client import APIClient
from utils.output import OutputFormatter


@click.group()
def documents():
    """文档管理命令"""
    pass


@documents.command(name='list')
@click.argument('dataset_id')
@click.option('--format', 'output_format', default='table', 
              type=click.Choice(['table', 'json', 'yaml', 'simple']), 
              help='输出格式')
@click.option('--page', default=1, type=int, help='页码，默认为1')
@click.option('--page-size', default=30, type=int, help='每页文档数量，默认为30')
@click.option('--all', is_flag=True, help='获取所有文档（自动分页）')
@click.option('--keywords', help='搜索关键词，匹配文档标题')
@click.option('--orderby', default='create_time', 
              type=click.Choice(['create_time', 'update_time']), 
              help='排序字段，默认为create_time')
@click.option('--desc/--asc', default=True, help='是否降序排列，默认为降序')
def list_documents(dataset_id, output_format, page, page_size, all, keywords, orderby, desc):
    """列出数据集中的文档"""
    try:
        client = APIClient()
        formatter = OutputFormatter(output_format)
        
        # 对于数据集相关API，使用Bearer格式的API token
        api_token = client.config.get('api', {}).get('api_token')
        if not api_token:
            formatter.print_error("未找到API令牌，请先登录")
            return
        
        # 使用API token设置认证头（Bearer格式）
        client.session.headers['Authorization'] = f"Bearer {api_token}"
        
        all_docs = []
        
        if all:
            # 获取所有文档，自动分页
            current_page = 1
            total_docs = 0
            
            while True:
                # 构建查询参数
                params = {
                    'page': current_page,
                    'page_size': page_size,
                    'orderby': orderby,
                    'desc': desc
                }
                
                if keywords:
                    params['keywords'] = keywords
                
                # 调用API
                response = client.get(f'/api/v1/datasets/{dataset_id}/documents', params=params)
                
                # 解析响应数据
                docs_data = response.get('data', {})
                docs = docs_data.get('docs', [])
                total = docs_data.get('total', 0)
                
                if not isinstance(docs, list):
                    docs = []
                
                all_docs.extend(docs)
                total_docs = total
                
                # 检查是否还有更多页面
                if len(docs) < page_size or len(all_docs) >= total_docs:
                    break
                
                current_page += 1
                
                # 显示进度
                formatter.print_info(f"已获取 {len(all_docs)}/{total_docs} 个文档...")
            
            docs = all_docs
            formatter.print_success(f"共获取到 {len(docs)} 个文档")
            
        else:
            # 单页获取
            # 构建查询参数
            params = {
                'page': page,
                'page_size': page_size,
                'orderby': orderby,
                'desc': desc
            }
            
            if keywords:
                params['keywords'] = keywords
            
            # 调用API
            response = client.get(f'/api/v1/datasets/{dataset_id}/documents', params=params)
            
            # 解析响应数据
            docs_data = response.get('data', {})
            docs = docs_data.get('docs', [])
            total = docs_data.get('total', 0)
            
            if not isinstance(docs, list):
                docs = []
            
            # 显示分页信息
            start_num = (page - 1) * page_size + 1
            end_num = min(page * page_size, total)
            formatter.print_info(f"显示第 {start_num}-{end_num} 个文档，共 {total} 个文档")
        
        # 格式化输出
        if output_format == 'table':
            formatter.print_rich_table(docs, f"数据集 {dataset_id} 的文档列表")
        elif output_format == 'simple':
            formatter.print_simple_list(docs, f"数据集 {dataset_id} 的文档列表")
        else:
            print(formatter.format_output(response))
            
    except Exception as e:
        formatter = OutputFormatter()
        formatter.print_error(f"获取文档列表失败: {e}")
        # 输出详细错误信息
        if hasattr(e, 'response') and e.response:
            formatter.print_error(f"API响应: {e.response.text}")


@documents.command()
@click.argument('dataset_id')
@click.argument('document_id')
@click.option('--format', 'output_format', default='table', 
              type=click.Choice(['table', 'json', 'yaml']), 
              help='输出格式')
def show(dataset_id, document_id, output_format):
    """显示文档详细信息"""
    try:
        client = APIClient()
        formatter = OutputFormatter(output_format)
        
        # 检查是否有API token
        if not _ensure_token(client, formatter):
            return

        # 调用API
        response = client.get(f'/api/v1/datasets/{dataset_id}/documents/{document_id}')
        
        # 格式化输出
        if output_format == 'table':
            formatter.print_rich_table([response], f"文档 {document_id} 详情")
        else:
            print(formatter.format_output(response))
            
    except Exception as e:
        formatter = OutputFormatter()
        formatter.print_error(f"获取文档详情失败: {e}")


@documents.command()
@click.argument('dataset_id')
@click.argument('name')
@click.option('--content', help='文档内容')
@click.option('--format', 'output_format', default='table', 
              type=click.Choice(['table', 'json', 'yaml']), 
              help='输出格式')
def create(dataset_id, name, content, output_format):
    """在数据集中创建新文档"""
    try:
        client = APIClient()
        formatter = OutputFormatter(output_format)
        
        # 检查是否有API token
        if not _ensure_token(client, formatter):
            return

        # 构建请求数据
        document_data = {
            'name': name
        }
        
        if content:
            document_data['content'] = content
        
        # 调用API
        response = client.post(f'/api/v1/datasets/{dataset_id}/documents', 
                             json_data={'document': document_data})
        
        # 检查API响应是否真正成功
        if response.get('code') == 0 and not response.get('message', '').startswith('Please check your authorization'):
            formatter.print_success(f"文档 {name} 创建成功")
        else:
            error_msg = response.get('message', '未知错误')
            formatter.print_error(f"创建文档失败: {error_msg}")
            return
        
        # 格式化输出
        if output_format == 'table':
            formatter.print_rich_table([response.get('document', {})], "创建的文档")
        else:
            print(formatter.format_output(response))
            
    except Exception as e:
        formatter = OutputFormatter()
        formatter.print_error(f"创建文档失败: {e}")


@documents.command()
@click.argument('dataset_id')
@click.argument('document_id')
def delete(dataset_id, document_id):
    """删除文档"""
    try:
        client = APIClient()
        formatter = OutputFormatter()
        
        # 检查是否有API token
        if not _ensure_token(client, formatter):
            return

        # 调用API
        client.delete(f'/api/v1/datasets/{dataset_id}/documents/{document_id}')
        
        formatter.print_success(f"文档 {document_id} 删除成功")
        
    except Exception as e:
        formatter = OutputFormatter()
        formatter.print_error(f"删除文档失败: {e}")


@documents.command()
@click.argument('dataset_id')
@click.argument('document_id')
@click.argument('name')
@click.option('--content', help='新的文档内容')
@click.option('--format', 'output_format', default='table', 
              type=click.Choice(['table', 'json', 'yaml']), 
              help='输出格式')
def update(dataset_id, document_id, name, content, output_format):
    """更新文档信息"""
    try:
        client = APIClient()
        formatter = OutputFormatter(output_format)
        
        # 检查是否有API token
        if not _ensure_token(client, formatter):
            return

        # 构建请求数据
        update_data = {
            'name': name
        }
        
        if content:
            update_data['content'] = content
        
        # 调用API
        response = client.put(f'/api/v1/datasets/{dataset_id}/documents/{document_id}', 
                            json_data={'document': update_data})
        
        formatter.print_success(f"文档 {document_id} 更新成功")
        
        # 格式化输出
        if output_format == 'table':
            formatter.print_rich_table([response], "更新后的文档")
        else:
            print(formatter.format_output(response))
            
    except Exception as e:
        formatter = OutputFormatter()
        formatter.print_error(f"更新文档失败: {e}")


@documents.command()
@click.argument('dataset_id')
@click.argument('document_id')
@click.option('--format', 'output_format', default='table', 
              type=click.Choice(['table', 'json', 'yaml']), 
              help='输出格式')
def chunks(dataset_id, document_id, output_format):
    """列出文档的所有块"""
    try:
        client = APIClient()
        formatter = OutputFormatter(output_format)
        
        # 检查是否有API token
        if not _ensure_token(client, formatter):
            return

        # 调用API
        response = client.get(f'/api/v1/datasets/{dataset_id}/documents/{document_id}/chunks')
        
        # 格式化输出
        if output_format == 'table':
            formatter.print_rich_table(response.get('chunks', []), f"文档 {document_id} 的块列表")
        else:
            print(formatter.format_output(response))
            
    except Exception as e:
        formatter = OutputFormatter()
        formatter.print_error(f"获取文档块列表失败: {e}") 


@documents.command()
@click.argument('dataset_id')
@click.option('--file', 'file_path', required=True, help='要上传的本地文件路径')
@click.option('--format', 'output_format', default='table', 
              type=click.Choice(['table', 'json', 'yaml']), 
              help='输出格式')
def upload(dataset_id, file_path, output_format):
    """上传本地文件到知识库（dataset）"""
    import os
    import requests
    from utils.output import OutputFormatter
    try:
        client = APIClient()
        formatter = OutputFormatter(output_format)
        
        # 检查是否有API token
        if not _ensure_token(client, formatter):
            return
        
        if not os.path.isfile(file_path):
            formatter.print_error(f"文件不存在: {file_path}")
            return
        
        # 修正上传接口路径和参数
        headers = {}
        if 'Authorization' in client.session.headers:
            headers['Authorization'] = client.session.headers['Authorization']
        url = client.base_url.rstrip('/') + '/v1/document/upload'
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f)}
            data = {'kb_id': dataset_id}
            resp = requests.post(url, headers=headers, files=files, data=data)
        
        try:
            response = resp.json()
        except Exception:
            formatter.print_error(f"服务端返回非JSON: {resp.text}")
            return
        
        if response.get('code') == 0:
            formatter.print_success(f"文件 {file_path} 上传成功")
            if output_format == 'table':
                formatter.print_rich_table(response.get('data', []), "上传结果")
            else:
                print(formatter.format_output(response))
        else:
            formatter.print_error(f"上传失败: {response.get('message', '未知错误')}")
    except Exception as e:
        formatter = OutputFormatter()
        formatter.print_error(f"文件上传失败: {e}")


@documents.command()
@click.argument('dataset_id')
@click.argument('document_id')
@click.option('--format', 'output_format', default='table', 
              type=click.Choice(['table', 'json', 'yaml']), 
              help='输出格式')
def parse(dataset_id, document_id, output_format):
    """启动文档解析"""
    try:
        client = APIClient()
        formatter = OutputFormatter(output_format)
        
        # 对于文档解析API，使用auth_token
        auth_token = client.config.get('api', {}).get('auth_token')
        if not auth_token:
            formatter.print_error("未找到认证令牌，请先登录")
            return
        
        # 使用auth_token设置认证头
        client.session.headers['Authorization'] = auth_token
        
        # 构建解析请求数据 - 使用正确的API格式
        parse_data = {
            "doc_ids": [document_id],
            "run": "1"  # TaskStatus.RUNNING = "1"
        }
        
        # 调用正确的文档解析API
        response = client.post('/v1/document/run', json_data=parse_data)
        
        if response is True or (isinstance(response, dict) and response.get('code') == 0):
            formatter.print_success(f"文档 {document_id} 解析已启动")
            if output_format == 'table':
                formatter.print_rich_table([{"status": "success", "message": "解析已启动"}], "解析启动结果")
            else:
                print(formatter.format_output({"status": "success", "message": "解析已启动"}))
        else:
            error_msg = "未知错误"
            if isinstance(response, dict):
                error_msg = response.get('message', '未知错误')
            formatter.print_error(f"启动解析失败: {error_msg}")
            
    except Exception as e:
        formatter = OutputFormatter()
        formatter.print_error(f"启动文档解析失败: {e}")


@documents.command()
@click.argument('dataset_id')
@click.argument('document_id')
@click.option('--format', 'output_format', default='table', 
              type=click.Choice(['table', 'json', 'yaml']), 
              help='输出格式')
def status(dataset_id, document_id, output_format):
    """查看文档解析状态"""
    try:
        client = APIClient()
        formatter = OutputFormatter(output_format)
        
        # 对于数据集相关API，使用Bearer格式的API token
        api_token = client.config.get('api', {}).get('api_token')
        if not api_token:
            formatter.print_error("未找到API令牌，请先登录")
            return
        
        # 使用API token设置认证头（Bearer格式）
        client.session.headers['Authorization'] = f"Bearer {api_token}"
        
        # 获取文档列表，找到指定文档
        response = client.get(f'/api/v1/datasets/{dataset_id}/documents')
        
        docs = response.get('data', {}).get('docs', [])
        target_doc = None
        
        for doc in docs:
            if doc.get('id') == document_id:
                target_doc = doc
                break
        
        if not target_doc:
            formatter.print_error(f"未找到文档 {document_id}")
            return
        
        # 提取解析状态信息
        status_info = {
            'id': target_doc.get('id'),
            'name': target_doc.get('name'),
            'run': target_doc.get('run'),
            'status': target_doc.get('status'),
            'progress': target_doc.get('progress', 0),
            'progress_msg': target_doc.get('progress_msg', ''),
            'chunk_count': target_doc.get('chunk_count', 0),
            'token_count': target_doc.get('token_count', 0)
        }
        
        # 格式化输出
        if output_format == 'table':
            formatter.print_rich_table([status_info], f"文档 {document_id} 解析状态")
        else:
            print(formatter.format_output(status_info))
            
    except Exception as e:
        formatter = OutputFormatter()
        formatter.print_error(f"获取文档解析状态失败: {e}")


@documents.command()
@click.argument('dataset_id')
@click.option('--format', 'output_format', default='table', 
              type=click.Choice(['table', 'json', 'yaml']), 
              help='输出格式')
def parse_all(dataset_id, output_format):
    """批量启动所有未解析文档的解析"""
    try:
        client = APIClient()
        formatter = OutputFormatter(output_format)
        
        # 对于文档解析API，使用auth_token
        auth_token = client.config.get('api', {}).get('auth_token')
        if not auth_token:
            formatter.print_error("未找到认证令牌，请先登录")
            return
        
        # 使用auth_token设置认证头
        client.session.headers['Authorization'] = auth_token
        
        # 获取文档列表 - 使用Bearer格式的API token
        api_token = client.config.get('api', {}).get('api_token')
        if api_token:
            client.session.headers['Authorization'] = f"Bearer {api_token}"
        
        response = client.get(f'/api/v1/datasets/{dataset_id}/documents')
        docs = response.get('data', {}).get('docs', [])
        
        if not docs:
            formatter.print_error(f"数据集 {dataset_id} 中没有文档")
            return
        
        # 筛选未解析的文档
        unparsed_docs = [doc for doc in docs if doc.get('run') == 'UNSTART']
        
        if not unparsed_docs:
            formatter.print_success("所有文档都已开始解析或已完成")
            return
        
        # 恢复使用auth_token进行解析API调用
        client.session.headers['Authorization'] = auth_token
        
        # 启动解析
        results = []
        for doc in unparsed_docs:
            doc_id = doc.get('id')
            doc_name = doc.get('name')
            
            try:
                # 使用正确的API格式
                parse_data = {
                    "doc_ids": [doc_id],
                    "run": "1"  # TaskStatus.RUNNING = "1"
                }
                result = client.post('/v1/document/run', json_data=parse_data)
                
                if result.get('code') == 0:
                    results.append({
                        'id': doc_id,
                        'name': doc_name,
                        'status': '启动成功',
                        'message': '解析已启动'
                    })
                else:
                    results.append({
                        'id': doc_id,
                        'name': doc_name,
                        'status': '启动失败',
                        'message': result.get('message', '未知错误')
                    })
            except Exception as e:
                results.append({
                    'id': doc_id,
                    'name': doc_name,
                    'status': '启动失败',
                    'message': str(e)
                })
        
        # 格式化输出
        if output_format == 'table':
            formatter.print_rich_table(results, f"批量解析结果 ({len(results)} 个文档)")
        else:
            print(formatter.format_output(results))
            
    except Exception as e:
        formatter = OutputFormatter()
        formatter.print_error(f"批量启动解析失败: {e}")


def _ensure_token(client, formatter):
    """自动兼容两种token方式"""
    # 优先尝试 auth_token（直接token）
    auth_token = client.config.get('api', {}).get('auth_token')
    if auth_token:
        client.session.headers['Authorization'] = auth_token
        return True
    
    # 备选 api_token（Bearer格式）
    api_token = client.config.get('api', {}).get('api_token')
    if api_token:
        client.session.headers['Authorization'] = f"Bearer {api_token}"
        return True
    
    formatter.print_error("未找到API令牌，请先登录")
    return False 