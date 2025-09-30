#!/usr/bin/env python3
"""
RAGForge API 脚本工具
提供简洁易用的命令行接口
"""

import click
import sys
from pathlib import Path

# 导入命令模块
from commands.datasets import datasets
from commands.documents import documents
from commands.chunks import chunks
from commands.retrieval import retrieval
from commands.user import user
from commands.debug import debug
from commands.system import system
from commands.compare import compare


@click.group()
@click.option('--config', default='config.yaml', help='配置文件路径')
@click.option('--debug', is_flag=True, help='启用调试模式')
@click.pass_context
def cli(ctx, config, debug):
    """RAGForge API 脚本工具
    
    提供简洁易用的命令行接口，封装各种API调用。
    
    示例:
        python main.py user info
        python main.py debug check-connection
        python main.py datasets list
        python main.py documents list <dataset_id>
        python main.py retrieval search "查询内容" <dataset_id>
    """
    ctx.ensure_object(dict)
    ctx.obj['config'] = config
    ctx.obj['debug'] = debug


# 注册命令组
cli.add_command(user, name='user')
cli.add_command(debug, name='debug')
cli.add_command(datasets, name='datasets')
cli.add_command(documents, name='documents')
cli.add_command(chunks, name='chunks')
cli.add_command(retrieval, name='retrieval')
cli.add_command(system, name='system')
cli.add_command(compare, name='compare')


@cli.command()
def version():
    """显示版本信息"""
    click.echo("RAGForge API 脚本工具 v1.0.0")


@cli.command()
@click.option('--format', 'output_format', default='table', 
              type=click.Choice(['table', 'json', 'yaml']), 
              help='输出格式')
def api_list(output_format):
    """列出所有可用的API端点"""
    try:
        from api_client import APIClient
        from utils.output import OutputFormatter
        
        client = APIClient()
        formatter = OutputFormatter(output_format)
        
        # 获取API文档
        response = client.get('/apispec.json')
        
        # 格式化输出
        if output_format == 'table':
            # 提取API端点信息
            apis = []
            if isinstance(response, dict) and 'paths' in response:
                for path, methods in response['paths'].items():
                    for method, info in methods.items():
                        apis.append({
                            'path': path,
                            'method': method.upper(),
                            'summary': info.get('summary', ''),
                            'tags': ', '.join(info.get('tags', []))
                        })
            
            formatter.print_rich_table(apis, "可用API端点")
        else:
            print(formatter.format_output(response))
            
    except Exception as e:
        formatter = OutputFormatter()
        formatter.print_error(f"获取API列表失败: {e}")


@cli.command()
@click.argument('endpoint')
@click.option('--method', default='GET', 
              type=click.Choice(['GET', 'POST', 'PUT', 'DELETE']), 
              help='HTTP方法')
@click.option('--data', help='请求数据(JSON格式)')
@click.option('--format', 'output_format', default='table', 
              type=click.Choice(['table', 'json', 'yaml']), 
              help='输出格式')
def api_call(endpoint, method, data, output_format):
    """直接调用API端点"""
    try:
        import json
        from api_client import APIClient
        from utils.output import OutputFormatter
        
        client = APIClient()
        formatter = OutputFormatter(output_format)
        
        # 解析请求数据
        json_data = None
        if data:
            try:
                json_data = json.loads(data)
            except json.JSONDecodeError:
                formatter.print_error("请求数据格式错误，请使用有效的JSON格式")
                return
        
        # 调用API
        if method == 'GET':
            response = client.get(endpoint)
        elif method == 'POST':
            response = client.post(endpoint, json_data=json_data)
        elif method == 'PUT':
            response = client.put(endpoint, json_data=json_data)
        elif method == 'DELETE':
            response = client.delete(endpoint)
        
        # 格式化输出
        if output_format == 'table':
            if isinstance(response, list):
                formatter.print_rich_table(response, f"{method} {endpoint}")
            else:
                formatter.print_rich_table([response], f"{method} {endpoint}")
        else:
            print(formatter.format_output(response))
            
    except Exception as e:
        formatter = OutputFormatter()
        formatter.print_error(f"API调用失败: {e}")


@cli.command()
def config_show():
    """显示当前配置"""
    try:
        from api_client import APIClient
        from utils.output import OutputFormatter
        
        client = APIClient()
        formatter = OutputFormatter()
        
        config = client.get_config()
        formatter.print_rich_table([config], "当前配置")
        
    except Exception as e:
        formatter = OutputFormatter()
        formatter.print_error(f"获取配置失败: {e}")


def main():
    """主函数"""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n操作已取消")
        sys.exit(1)
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main() 