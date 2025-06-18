@echo off
chcp 65001 >nul
echo.
echo ==========================================
echo   Windows图标缓存清理工具
echo ==========================================
echo.

echo 正在清理Windows图标缓存...
echo.

echo 1. 停止Windows资源管理器...
taskkill /f /im explorer.exe >nul 2>&1

echo 2. 清理图标缓存文件...
cd /d "%userprofile%\AppData\Local"

if exist IconCache.db (
    del /f /q IconCache.db
    echo    ✅ 删除 IconCache.db
) else (
    echo    ⚠️ IconCache.db 不存在
)

if exist "Microsoft\Windows\Explorer" (
    cd "Microsoft\Windows\Explorer"
    for %%i in (iconcache_*.db) do (
        del /f /q "%%i" >nul 2>&1
        echo    ✅ 删除 %%i
    )
    cd /d "%userprofile%\AppData\Local"
) else (
    echo    ⚠️ Explorer缓存目录不存在
)

echo 3. 重启Windows资源管理器...
start explorer.exe

echo.
echo ==========================================
echo   🎉 图标缓存清理完成！
echo ==========================================
echo.
echo 建议:
echo 1. 重新运行BadgePatternTool程序
echo 2. 检查窗口标题栏和任务栏图标
echo 3. 如果仍无显示，请重启计算机
echo.

pause
