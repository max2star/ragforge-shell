import click
import re
import os
from typing import List, Set, Dict, Tuple
from pathlib import Path


@click.group()
def compare():
    """文件比较命令"""
    pass


def extract_pending_files(pending_file_path: str) -> List[str]:
    """
    从待上传文件清单中提取文件名
    文件格式: [公开]数字.pdf
    """
    pending_files = []
    try:
        with open(pending_file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                # 直接检查文件名格式
                if line and line.startswith('[公开]') and line.endswith('.pdf'):
                    pending_files.append(line)
    except FileNotFoundError:
        raise FileNotFoundError(f"找不到待上传文件清单: {pending_file_path}")
    except Exception as e:
        raise Exception(f"读取待上传文件清单时出错: {e}")
    
    return pending_files


def extract_uploaded_files(uploaded_file_path: str) -> Set[str]:
    """
    从已上传文件清单中提取文件名
    文件格式: upload_数字_[公开]文件名.pdf
    """
    uploaded_files = set()
    try:
        with open(uploaded_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 使用正则表达式匹配文件名模式
        # 匹配: upload_数字_[公开]任何字符.pdf
        pattern = r'upload_\d+_\[公开\]([^.]+\.pdf)'
        matches = re.findall(pattern, content)
        
        for match in matches:
            filename = f"{match}"
            uploaded_files.add(filename)
            
    except FileNotFoundError:
        raise FileNotFoundError(f"找不到已上传文件清单: {uploaded_file_path}")
    except Exception as e:
        raise Exception(f"读取已上传文件清单时出错: {e}")
    
    return uploaded_files


def fuzzy_match(pending_file: str, uploaded_files: Set[str]) -> Tuple[bool, str]:
    """
    模糊匹配函数
    检查待上传文件是否在已上传文件中存在对应的记录
    """
    # 从待上传文件名中提取数字部分（去掉[公开]前缀和.pdf后缀）
    # 例如：[公开]999.pdf -> 999.pdf
    if pending_file.startswith('[公开]'):
        pending_base = pending_file[4:]  # 去掉"[公开]"，这是4个字符
    else:
        pending_base = pending_file
    
    # 直接匹配
    if pending_base in uploaded_files:
        return True, pending_base
    
    # 模糊匹配：去掉扩展名进行比较
    pending_name = pending_base.replace('.pdf', '').replace('.PDF', '')
    
    for uploaded_file in uploaded_files:
        uploaded_name = uploaded_file.replace('.pdf', '').replace('.PDF', '')
        
        # 如果数字部分相同，认为匹配
        if pending_name == uploaded_name:
            return True, uploaded_file
    
    return False, ""


def find_missing_files(pending_file_path: str, uploaded_file_path: str) -> Dict[str, List[str]]:
    """
    找出未上传的文件
    返回结果包含:
    - missing_files: 未上传的文件列表
    - found_files: 已找到的文件列表及其匹配的已上传文件
    """
    pending_files = extract_pending_files(pending_file_path)
    uploaded_files = extract_uploaded_files(uploaded_file_path)
    
    missing_files = []
    found_files = []
    
    for pending_file in pending_files:
        is_found, matched_file = fuzzy_match(pending_file, uploaded_files)
        
        if is_found:
            found_files.append((pending_file, matched_file))
        else:
            missing_files.append(pending_file)
    
    return {
        'missing_files': missing_files,
        'found_files': found_files,
        'total_pending': len(pending_files),
        'total_uploaded': len(uploaded_files),
        'found_count': len(found_files),
        'missing_count': len(missing_files)
    }


@compare.command()
@click.argument('pending_file', type=click.Path(exists=True))
@click.argument('uploaded_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='输出报告文件路径')
@click.option('--format', 'output_format', default='table', 
              type=click.Choice(['table', 'json', 'yaml', 'simple']), 
              help='输出格式')
@click.option('--show-found', is_flag=True, help='显示已找到的文件列表')
@click.option('--show-missing', is_flag=True, default=True, help='显示未上传的文件列表')
def files(pending_file, uploaded_file, output, output_format, show_found, show_missing):
    """比较待上传文件和已上传文件清单
    
    示例:
        python main.py compare files /path/to/pending.txt /path/to/uploaded.txt
        python main.py compare files /path/to/pending.txt /path/to/uploaded.txt --output report.txt
        python main.py compare files /path/to/pending.txt /path/to/uploaded.txt --format json
    """
    try:
        from utils.output import OutputFormatter
        formatter = OutputFormatter(output_format)
        
        # 执行比较
        click.echo("正在比较文件...")
        results = find_missing_files(pending_file, uploaded_file)
        
        # 显示统计信息
        click.echo(f"\n📊 比较结果:")
        click.echo(f"   待上传文件总数: {results['total_pending']}")
        click.echo(f"   已上传文件总数: {results['total_uploaded']}")
        click.echo(f"   已找到文件数: {results['found_count']}")
        click.echo(f"   未上传文件数: {results['missing_count']}")
        
        match_rate = (results['found_count'] / results['total_pending']) * 100 if results['total_pending'] > 0 else 0
        click.echo(f"   匹配成功率: {match_rate:.1f}%")
        
        # 显示已找到的文件
        if show_found and results['found_files']:
            click.echo(f"\n✅ 已找到的文件 (前10个):")
            for i, (pending, uploaded) in enumerate(results['found_files'][:10], 1):
                click.echo(f"   {i:2d}. {pending} -> {uploaded}")
            
            if len(results['found_files']) > 10:
                click.echo(f"   ... 还有 {len(results['found_files']) - 10} 个文件")
        
        # 显示未上传的文件
        if show_missing and results['missing_files']:
            click.echo(f"\n❌ 未上传的文件 ({results['missing_count']} 个):")
            
            if output_format == 'table':
                # 使用表格格式显示
                table_data = []
                for i, missing_file in enumerate(results['missing_files'], 1):
                    table_data.append({
                        '序号': i,
                        '文件名': missing_file
                    })
                formatter.print_rich_table(table_data, "未上传文件列表")
            else:
                # 使用简单列表格式
                for i, missing_file in enumerate(results['missing_files'], 1):
                    click.echo(f"   {i:2d}. {missing_file}")
        elif show_missing and not results['missing_files']:
            click.echo("\n🎉 所有文件都已上传！")
        
        # 保存报告到文件
        if output:
            save_results_to_file(results, output)
            click.echo(f"\n📄 详细报告已保存到: {output}")
        
        # 输出JSON/YAML格式
        if output_format in ['json', 'yaml']:
            output_data = {
                'statistics': {
                    'total_pending': results['total_pending'],
                    'total_uploaded': results['total_uploaded'],
                    'found_count': results['found_count'],
                    'missing_count': results['missing_count'],
                    'match_rate': match_rate
                },
                'found_files': [{'pending': p, 'uploaded': u} for p, u in results['found_files']],
                'missing_files': results['missing_files']
            }
            click.echo(f"\n{formatter.format_output(output_data)}")
            
    except FileNotFoundError as e:
        click.echo(f"❌ 文件未找到: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"❌ 比较过程中出错: {e}", err=True)
        raise click.Abort()


def save_results_to_file(results: Dict[str, List[str]], output_file: str):
    """保存结果到文件"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("文件比较结果\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"统计信息:\n")
            f.write(f"- 待上传文件总数: {results['total_pending']}\n")
            f.write(f"- 已上传文件总数: {results['total_uploaded']}\n")
            f.write(f"- 已找到文件数: {results['found_count']}\n")
            f.write(f"- 未上传文件数: {results['missing_count']}\n\n")
            
            match_rate = (results['found_count'] / results['total_pending']) * 100 if results['total_pending'] > 0 else 0
            f.write(f"- 匹配成功率: {match_rate:.1f}%\n\n")
            
            f.write("已找到的文件 (待上传 -> 已上传):\n")
            f.write("-" * 50 + "\n")
            for pending, uploaded in results['found_files']:
                f.write(f"{pending} -> {uploaded}\n")
            
            f.write(f"\n未上传的文件列表 ({results['missing_count']} 个):\n")
            f.write("-" * 50 + "\n")
            for missing_file in results['missing_files']:
                f.write(f"{missing_file}\n")
                
    except Exception as e:
        raise Exception(f"保存结果时出错: {e}")


@compare.command()
@click.argument('pending_file', type=click.Path(exists=True))
@click.argument('uploaded_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='输出报告文件路径')
def quick(pending_file, uploaded_file, output):
    """快速比较文件（简化输出）
    
    示例:
        python main.py compare quick /path/to/pending.txt /path/to/uploaded.txt
    """
    try:
        # 执行比较
        results = find_missing_files(pending_file, uploaded_file)
        
        # 显示简化结果
        click.echo(f"📊 待上传: {results['total_pending']} | 已上传: {results['total_uploaded']} | 匹配: {results['found_count']} | 未上传: {results['missing_count']}")
        
        match_rate = (results['found_count'] / results['total_pending']) * 100 if results['total_pending'] > 0 else 0
        click.echo(f"🎯 匹配率: {match_rate:.1f}%")
        
        if results['missing_files']:
            click.echo(f"\n❌ 未上传文件 ({len(results['missing_files'])} 个):")
            for missing_file in results['missing_files']:
                click.echo(f"   {missing_file}")
        else:
            click.echo("\n🎉 所有文件都已上传！")
        
        # 保存报告
        if output:
            save_results_to_file(results, output)
            click.echo(f"\n📄 报告已保存到: {output}")
            
    except Exception as e:
        click.echo(f"❌ 比较过程中出错: {e}", err=True)
        raise click.Abort()
