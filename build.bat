@echo off
chcp 65001 >nul
echo.
echo ==========================================
echo   BadgePatternTool 打包脚本
echo ==========================================
echo.

echo 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    echo 请先安装Python并添加到系统PATH
    pause
    exit /b 1
)

echo ✅ Python环境正常

echo.
echo 正在检查依赖包...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo ❌ PyInstaller未安装，正在安装...
    pip install pyinstaller
    if errorlevel 1 (
        echo ❌ PyInstaller安装失败
        pause
        exit /b 1
    )
)

echo ✅ PyInstaller已安装

echo.
echo 检查图标文件...
if not exist "src\assets\icon.ico" (
    echo ⚠️ 未找到图标文件，正在创建默认图标...
    python scripts/create_icon.py
    if errorlevel 1 (
        echo ❌ 图标创建失败，继续打包（无图标）
    ) else (
        echo ✅ 图标创建成功
    )
) else (
    echo ✅ 图标文件已存在
)

echo.
echo 开始打包程序...
python scripts/build.py

if errorlevel 1 (
    echo.
    echo ❌ 打包失败，请检查错误信息
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   🎉 打包完成！
echo ==========================================
echo.
echo 可执行文件位于: dist\BadgePatternTool.exe
echo 文件大小: 约53MB
echo.
echo 分发文件包括:
echo   - BadgePatternTool.exe (主程序)
echo   - CHANGELOG.md (更新日志)
echo.

pause
