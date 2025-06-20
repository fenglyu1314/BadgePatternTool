#!/usr/bin/env python3
"""
版本管理脚本
用于统一管理和更新项目中的版本号
"""

import re
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Tuple

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 需要更新版本号的文件列表
VERSION_FILES = [
    {
        'file': 'src/common/constants.py',
        'pattern': r'APP_VERSION = "[^"]*"',
        'replacement': 'APP_VERSION = "{version}"',
        'description': '应用程序常量定义'
    },
    {
        'file': 'CHANGELOG.md',
        'pattern': r'## \[[\d.]+\] - \d{4}-\d{2}-\d{2}',
        'replacement': '## [{version}] - {date}',
        'description': '更新日志',
        'prepend': True  # 在文件开头添加新版本
    },
    {
        'file': 'docs/代码架构文档.md',
        'pattern': r'__version__ = "[^"]*"',
        'replacement': '__version__ = "{version}"',
        'description': '代码架构文档示例'
    },
    {
        'file': 'scripts/build.py',
        'pattern': r'BadgePatternTool v[\d.]+',
        'replacement': 'BadgePatternTool v{version}',
        'description': '构建脚本'
    }
]

def get_current_version() -> str:
    """获取当前版本号"""
    constants_file = PROJECT_ROOT / 'src/common/constants.py'
    if not constants_file.exists():
        return "1.0.0"
    
    content = constants_file.read_text(encoding='utf-8')
    match = re.search(r'APP_VERSION = "([^"]*)"', content)
    return match.group(1) if match else "1.0.0"

def validate_version(version: str) -> bool:
    """验证版本号格式（语义化版本）"""
    pattern = r'^\d+\.\d+\.\d+$'
    return bool(re.match(pattern, version))

def compare_versions(v1: str, v2: str) -> int:
    """比较版本号大小
    返回值：-1(v1<v2), 0(v1==v2), 1(v1>v2)
    """
    def version_tuple(v):
        return tuple(map(int, v.split('.')))
    
    t1, t2 = version_tuple(v1), version_tuple(v2)
    return (t1 > t2) - (t1 < t2)

def update_file_version(file_info: dict, new_version: str) -> bool:
    """更新单个文件中的版本号"""
    file_path = PROJECT_ROOT / file_info['file']
    
    if not file_path.exists():
        print(f"⚠️  文件不存在: {file_path}")
        return False
    
    try:
        content = file_path.read_text(encoding='utf-8')
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        # 准备替换内容
        replacement = file_info['replacement'].format(
            version=new_version,
            date=current_date
        )
        
        # 执行替换
        if file_info.get('prepend') and file_info['file'] == 'CHANGELOG.md':
            # 特殊处理CHANGELOG.md，在现有版本前添加新版本
            lines = content.split('\n')
            insert_index = -1
            
            # 找到第一个版本条目的位置
            for i, line in enumerate(lines):
                if re.match(r'## \[[\d.]+\]', line):
                    insert_index = i
                    break
            
            if insert_index > 0:
                # 插入新版本条目
                new_entry = f"""## [{new_version}] - {current_date}

### 新增
- 

### 改进
- 

### 修复
- 

"""
                lines.insert(insert_index, new_entry)
                content = '\n'.join(lines)
            else:
                print(f"⚠️  无法在CHANGELOG.md中找到插入位置")
                return False
        else:
            # 普通替换
            new_content = re.sub(file_info['pattern'], replacement, content)
            if new_content == content:
                print(f"⚠️  在 {file_path} 中未找到匹配的版本号模式")
                return False
            content = new_content
        
        # 写回文件
        file_path.write_text(content, encoding='utf-8')
        print(f"✅ 已更新: {file_info['description']} ({file_path})")
        return True
        
    except Exception as e:
        print(f"❌ 更新失败 {file_path}: {e}")
        return False

def update_version(new_version: str, force: bool = False) -> bool:
    """更新项目版本号"""
    current_version = get_current_version()
    
    print(f"当前版本: {current_version}")
    print(f"目标版本: {new_version}")
    
    # 验证版本号格式
    if not validate_version(new_version):
        print("❌ 版本号格式无效，请使用语义化版本格式 (如: 1.2.3)")
        return False
    
    # 检查版本号是否递增
    if not force and compare_versions(new_version, current_version) <= 0:
        print(f"❌ 新版本号 {new_version} 必须大于当前版本 {current_version}")
        print("   使用 --force 参数可以强制更新")
        return False
    
    print(f"\n开始更新版本号到 {new_version}...")
    print("=" * 50)
    
    success_count = 0
    total_count = len(VERSION_FILES)
    
    # 更新所有文件
    for file_info in VERSION_FILES:
        if update_file_version(file_info, new_version):
            success_count += 1
    
    print("=" * 50)
    print(f"更新完成: {success_count}/{total_count} 个文件成功更新")
    
    if success_count == total_count:
        print(f"🎉 版本号已成功更新到 {new_version}")
        print("\n📝 下一步操作建议:")
        print("1. 检查 CHANGELOG.md 并补充版本更新内容")
        print("2. 提交更改: git add . && git commit -m 'chore: 升级版本到 {}'".format(new_version))
        print("3. 创建标签: git tag v{}".format(new_version))
        return True
    else:
        print("⚠️  部分文件更新失败，请检查错误信息")
        return False

def show_current_version():
    """显示当前版本信息"""
    current_version = get_current_version()
    print(f"当前版本: {current_version}")
    
    # 显示各文件中的版本号
    print("\n📋 各文件版本号状态:")
    for file_info in VERSION_FILES:
        file_path = PROJECT_ROOT / file_info['file']
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            match = re.search(file_info['pattern'], content)
            if match:
                print(f"  {file_info['description']}: {match.group(0)}")
            else:
                print(f"  {file_info['description']}: ❌ 未找到版本号")
        else:
            print(f"  {file_info['description']}: ❌ 文件不存在")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='BadgePatternTool 版本管理工具')
    parser.add_argument('version', nargs='?', help='新版本号 (如: 1.4.1)')
    parser.add_argument('--force', action='store_true', help='强制更新版本号')
    parser.add_argument('--show', action='store_true', help='显示当前版本信息')
    
    args = parser.parse_args()
    
    if args.show or not args.version:
        show_current_version()
        if not args.version:
            return
    
    # 更新版本号
    success = update_version(args.version, args.force)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
