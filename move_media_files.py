"""
批量移动图片和视频文件到上级目录
将子文件夹中的孙文件夹里的媒体文件移动到子文件夹根目录
"""

import os
import shutil
from pathlib import Path

# 支持的图片和视频文件扩展名
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.svg', '.ico'}
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.m4v', '.mpeg', '.mpg'}
MEDIA_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS


def is_media_file(file_path):
    """判断文件是否为图片或视频"""
    return file_path.suffix.lower() in MEDIA_EXTENSIONS


def move_media_files(root_folder):
    """
    遍历总文件夹，将每个子文件夹下的孙文件夹中的媒体文件移动到子文件夹
    
    Args:
        root_folder: 总文件夹路径
    """
    root_path = Path(root_folder)
    
    if not root_path.exists():
        print(f"错误: 文件夹不存在 - {root_folder}")
        return
    
    if not root_path.is_dir():
        print(f"错误: 路径不是文件夹 - {root_folder}")
        return
    
    # 统计信息
    total_moved = 0
    total_skipped = 0
    
    print(f"\n开始处理文件夹: {root_folder}\n")
    print("=" * 70)
    
    # 遍历总文件夹下的每个子文件夹
    for sub_folder in root_path.iterdir():
        if not sub_folder.is_dir():
            continue
        
        print(f"\n处理子文件夹: {sub_folder.name}")
        print("-" * 70)
        
        moved_count = 0
        skipped_count = 0
        
        # 遍历子文件夹下的所有孙文件夹
        for item in sub_folder.rglob('*'):
            # 只处理文件，且必须在子文件夹的子目录中（不在子文件夹直接下）
            if item.is_file() and item.parent != sub_folder:
                if is_media_file(item):
                    # 目标路径：移动到子文件夹根目录
                    target_path = sub_folder / item.name
                    
                    # 处理文件名冲突
                    if target_path.exists():
                        # 如果目标文件已存在，添加编号
                        base_name = item.stem
                        extension = item.suffix
                        counter = 1
                        while target_path.exists():
                            target_path = sub_folder / f"{base_name}_{counter}{extension}"
                            counter += 1
                        print(f"  [重命名] {item.name} -> {target_path.name}")
                    else:
                        print(f"  [移动] {item.name}")
                    
                    try:
                        # 移动文件
                        shutil.move(str(item), str(target_path))
                        moved_count += 1
                    except Exception as e:
                        print(f"  [错误] 移动失败: {item.name} - {str(e)}")
                        skipped_count += 1
        
        # 删除空的孙文件夹
        try:
            for item in sub_folder.iterdir():
                if item.is_dir():
                    # 递归删除空文件夹
                    remove_empty_folders(item)
        except Exception as e:
            print(f"  [警告] 清理空文件夹时出错: {str(e)}")
        
        print(f"\n  小计: 移动 {moved_count} 个文件, 跳过 {skipped_count} 个文件")
        total_moved += moved_count
        total_skipped += skipped_count
    
    print("\n" + "=" * 70)
    print(f"\n处理完成!")
    print(f"总计: 移动 {total_moved} 个文件, 跳过 {total_skipped} 个文件\n")


def remove_empty_folders(folder_path):
    """递归删除空文件夹"""
    folder = Path(folder_path)
    
    if not folder.exists() or not folder.is_dir():
        return
    
    # 先处理子文件夹
    for item in folder.iterdir():
        if item.is_dir():
            remove_empty_folders(item)
    
    # 检查当前文件夹是否为空
    try:
        if not any(folder.iterdir()):
            print(f"  [删除空文件夹] {folder.name}")
            folder.rmdir()
    except Exception:
        pass  # 文件夹不为空或无法删除


def main():
    """主函数"""
    print("=" * 70)
    print("批量移动媒体文件工具")
    print("=" * 70)
    print("\n功能说明:")
    print("将总文件夹下每个子文件夹中的孙文件夹里的图片和视频文件")
    print("移动到对应的子文件夹根目录下\n")
    
    # 获取用户输入
    root_folder = input("请输入总文件夹的路径: ").strip().strip('"').strip("'")
    
    if not root_folder:
        print("错误: 未输入文件夹路径")
        return
    
    # 确认操作
    print(f"\n将处理文件夹: {root_folder}")
    confirm = input("确认继续? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("操作已取消")
        return
    
    # 执行移动操作
    move_media_files(root_folder)
    
    input("\n按回车键退出...")


if __name__ == "__main__":
    main()
