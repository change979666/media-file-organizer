@echo off
chcp 65001 >nul
title 批量移动媒体文件工具

echo ========================================
echo 批量移动媒体文件工具 - 启动中...
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python
    pause
    exit /b 1
)

REM 检查依赖是否安装
python -c "import tkinterdnd2" >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装依赖包...
    pip install tkinterdnd2 pillow
    echo.
)

REM 启动程序
echo [启动] 正在启动图形界面...
echo.
python move_media_files_gui.py

if errorlevel 1 (
    echo.
    echo [错误] 程序运行出错
    pause
)
