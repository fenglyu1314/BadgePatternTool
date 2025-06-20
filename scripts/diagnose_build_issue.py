#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断构建问题
检查为什么构建的可执行文件无法正常运行
"""

import sys
import subprocess
from pathlib import Path

def test_direct_python_run():
    """测试直接用Python运行是否正常"""
    print("🔍 测试直接Python运行")
    print("-" * 40)
    
    try:
        result = subprocess.run([
            sys.executable, "src/main.py"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ 直接Python运行正常")
            return True
        else:
            print("❌ 直接Python运行失败")
            print("错误输出:", result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("✅ 直接Python运行正常 (GUI启动)")
        return True
    except Exception as e:
        print(f"❌ 直接Python运行出错: {e}")
        return False

def test_minimal_build():
    """测试最小化构建"""
    print("\n🔍 测试最小化构建")
    print("-" * 40)
    
    # 创建最小化的.spec文件
    minimal_spec = """
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/assets', 'assets'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='BadgePatternTool_minimal',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 启用控制台以查看错误
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/assets/icon.png',
)
"""
    
    # 写入最小化.spec文件
    with open("BadgePatternTool_minimal.spec", "w", encoding="utf-8") as f:
        f.write(minimal_spec)
    
    try:
        print("构建最小化版本...")
        result = subprocess.run([
            "pyinstaller", "--clean", "--noconfirm", "BadgePatternTool_minimal.spec"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 最小化构建成功")
            
            # 测试运行
            exe_path = Path("dist/BadgePatternTool_minimal.exe")
            if exe_path.exists():
                print("测试最小化版本运行...")
                try:
                    result = subprocess.run([str(exe_path)], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        print("✅ 最小化版本运行正常")
                        return True
                    else:
                        print("❌ 最小化版本运行失败")
                        print("错误输出:", result.stderr)
                        return False
                except subprocess.TimeoutExpired:
                    print("✅ 最小化版本运行正常 (GUI启动)")
                    return True
            else:
                print("❌ 最小化版本文件不存在")
                return False
        else:
            print("❌ 最小化构建失败")
            print("错误输出:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 最小化构建出错: {e}")
        return False

def check_problematic_excludes():
    """检查可能有问题的排除模块"""
    print("\n🔍 检查可能有问题的排除模块")
    print("-" * 40)
    
    # 读取当前.spec文件
    with open("BadgePatternTool.spec", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 可能导致GUI问题的排除
    problematic_excludes = [
        'threading',    # GUI可能需要线程
        'queue',        # 线程间通信
        'signal',       # 信号处理
        'subprocess',   # 子进程
        'tempfile',     # 临时文件
        'shutil',       # 文件操作
        'pathlib',      # 路径操作
        'platform',     # 平台信息
        'locale',       # 本地化
        'codecs',       # 编码
        'base64',       # 编码
        'binascii',     # 二进制转换
    ]
    
    found_problematic = []
    for module in problematic_excludes:
        if f"'{module}'" in content:
            found_problematic.append(module)
    
    if found_problematic:
        print(f"⚠️ 发现可能有问题的排除模块: {found_problematic}")
        return found_problematic
    else:
        print("✅ 未发现明显有问题的排除模块")
        return []

def suggest_fixes():
    """建议修复方案"""
    print("\n💡 修复建议")
    print("-" * 40)
    
    suggestions = [
        "1. 恢复基础模块: threading, queue, signal, subprocess",
        "2. 恢复编码模块: codecs, base64, binascii", 
        "3. 恢复文件操作: tempfile, shutil, pathlib",
        "4. 启用控制台模式查看详细错误信息",
        "5. 逐步减少排除模块，找到最小可工作集合",
        "6. 检查PySide6相关模块是否被误排除"
    ]
    
    for suggestion in suggestions:
        print(f"  💡 {suggestion}")

def main():
    """主函数"""
    print("=" * 60)
    print("构建问题诊断")
    print("=" * 60)
    
    # 测试直接Python运行
    python_ok = test_direct_python_run()
    
    # 检查问题模块
    problematic = check_problematic_excludes()
    
    # 测试最小化构建
    minimal_ok = test_minimal_build()
    
    # 建议修复
    suggest_fixes()
    
    print("\n" + "=" * 60)
    if python_ok and not minimal_ok:
        print("❌ 问题确认：过度优化导致构建失败")
        print("🔧 建议：减少模块排除，恢复关键模块")
    elif not python_ok:
        print("❌ 问题确认：源代码本身有问题")
        print("🔧 建议：先修复源代码问题")
    else:
        print("✅ 基础功能正常，需要进一步调试")
    
    return python_ok and minimal_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
