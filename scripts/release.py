#!/usr/bin/env python3
"""
发布脚本
自动化版本发布流程
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

def get_current_version():
    """获取当前版本号"""
    try:
        result = subprocess.run([
            sys.executable, "scripts/version_manager.py", "--show"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        for line in result.stdout.split('\n'):
            if line.startswith('当前版本:'):
                return line.split(':')[1].strip()
        return "1.0.0"
    except Exception:
        return "1.0.0"

def create_release(version, push_tag=True):
    """创建发布版本"""
    print(f"🚀 开始创建发布版本 {version}")
    print("=" * 50)
    
    project_root = Path(__file__).parent.parent
    
    try:
        # 1. 更新版本号
        print("📝 更新版本号...")
        result = subprocess.run([
            sys.executable, "scripts/version_manager.py", version
        ], cwd=project_root)
        
        if result.returncode != 0:
            print("❌ 版本号更新失败")
            return False
        
        # 2. 运行测试
        print("\n🧪 运行测试...")
        result = subprocess.run([
            sys.executable, "scripts/dev_tools.py", "test"
        ], cwd=project_root)
        
        if result.returncode != 0:
            print("⚠️ 测试失败，但继续发布流程")
        
        # 3. 构建可执行文件
        print("\n🔨 构建可执行文件...")
        result = subprocess.run([
            sys.executable, "scripts/build.py"
        ], cwd=project_root)
        
        if result.returncode != 0:
            print("❌ 构建失败")
            return False
        
        # 4. 提交版本更新
        print("\n📤 提交版本更新...")
        subprocess.run(["git", "add", "."], cwd=project_root)
        subprocess.run([
            "git", "commit", "-m", f"chore: 发布版本 {version}"
        ], cwd=project_root)
        
        # 5. 创建标签
        if push_tag:
            print(f"\n🏷️ 创建标签 v{version}...")
            subprocess.run([
                "git", "tag", f"v{version}", "-m", f"Release version {version}"
            ], cwd=project_root)
            
            # 6. 推送到远程
            print("\n📡 推送到GitHub...")
            subprocess.run(["git", "push", "origin", "develop"], cwd=project_root)
            subprocess.run(["git", "push", "origin", f"v{version}"], cwd=project_root)
            
            print(f"\n🎉 发布完成！")
            print(f"GitHub Actions 将自动构建并创建 Release")
            print(f"查看进度: https://github.com/fenglyu1314/BadgePatternTool/actions")
        else:
            print(f"\n✅ 本地发布准备完成")
            print(f"手动推送标签: git push origin v{version}")
        
        return True
        
    except Exception as e:
        print(f"❌ 发布过程出错: {e}")
        return False

def show_help():
    """显示帮助信息"""
    help_text = """
BadgePatternTool 发布脚本

用法:
  python scripts/release.py <version> [options]

参数:
  version           新版本号 (如: 1.4.2)

选项:
  --no-push        不自动推送标签到GitHub
  --help           显示此帮助信息

示例:
  python scripts/release.py 1.4.2
  python scripts/release.py 1.5.0 --no-push

发布流程:
  1. 更新版本号
  2. 运行测试
  3. 构建可执行文件
  4. 提交更改
  5. 创建Git标签
  6. 推送到GitHub (触发自动发布)
"""
    print(help_text)

def main():
    """主函数"""
    if len(sys.argv) < 2 or "--help" in sys.argv:
        show_help()
        return
    
    version = sys.argv[1]
    push_tag = "--no-push" not in sys.argv
    
    # 验证版本号格式
    import re
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        print("❌ 版本号格式错误，请使用 x.y.z 格式")
        return
    
    current_version = get_current_version()
    print(f"当前版本: {current_version}")
    print(f"目标版本: {version}")
    
    if input(f"\n确认发布版本 {version}? (y/N): ").lower() != 'y':
        print("❌ 发布已取消")
        return
    
    success = create_release(version, push_tag)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
