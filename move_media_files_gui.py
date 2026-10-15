"""
批量移动图片和视频文件到上级目录 - 图形界面版本
支持拖拽操作
"""

import os
import shutil
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pathlib import Path
import threading
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    print("警告: tkinterdnd2 未安装，拖拽功能将不可用")
    TkinterDnD = tk.Tk

# 支持的图片和视频文件扩展名
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.svg', '.ico'}
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.m4v', '.mpeg', '.mpg'}
MEDIA_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS


class MediaMoverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("批量移动媒体文件工具")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 设置样式
        style = ttk.Style()
        style.theme_use('clam')
        
        # 创建界面
        self.create_widgets()
        
        # 处理状态
        self.is_processing = False
        
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text="批量移动媒体文件工具",
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, pady=(0, 10), sticky=tk.W)
        
        # 说明文字
        info_text = "功能：将子文件夹中的孙文件夹里的图片和视频移动到子文件夹根目录\n" \
                   "操作：拖拽总文件夹到下方区域，或点击\"选择文件夹\"按钮"
        info_label = ttk.Label(main_frame, text=info_text, foreground='#666')
        info_label.grid(row=1, column=0, pady=(0, 10), sticky=tk.W)
        
        # 处理模式选择
        mode_frame = ttk.LabelFrame(main_frame, text="处理模式", padding="10")
        mode_frame.grid(row=1, column=0, pady=(40, 10), sticky=(tk.W, tk.E))
        
        self.mode_var = tk.StringVar(value="single")
        
        single_mode_radio = ttk.Radiobutton(
            mode_frame,
            text="🎯 单个模式 - 只处理选中的文件夹（测试用）",
            variable=self.mode_var,
            value="single"
        )
        single_mode_radio.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        batch_mode_radio = ttk.Radiobutton(
            mode_frame,
            text="📦 批量模式 - 处理所有子文件夹（正式使用）",
            variable=self.mode_var,
            value="batch"
        )
        batch_mode_radio.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        mode_desc = ttk.Label(
            mode_frame,
            text="💡 提示：单个模式适合测试，批量模式用于正式处理多个文件夹",
            foreground='#0066cc',
            font=('Arial', 8)
        )
        mode_desc.grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        
        # 拖拽区域框架
        drop_frame = ttk.LabelFrame(main_frame, text="拖拽文件夹到此处", padding="20")
        drop_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        drop_frame.columnconfigure(0, weight=1)
        drop_frame.rowconfigure(0, weight=1)
        
        # 拖拽标签
        self.drop_label = tk.Label(
            drop_frame,
            text="📁\n\n拖拽文件夹到这里\n或点击下方按钮选择",
            font=('Arial', 14),
            bg='#f0f0f0',
            fg='#666',
            relief=tk.GROOVE,
            borderwidth=2,
            cursor='hand2'
        )
        self.drop_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 绑定拖拽事件
        try:
            self.drop_label.drop_target_register(DND_FILES)
            self.drop_label.dnd_bind('<<Drop>>', self.on_drop)
            self.drop_label.dnd_bind('<<DragEnter>>', self.on_drag_enter)
            self.drop_label.dnd_bind('<<DragLeave>>', self.on_drag_leave)
        except:
            pass
        
        # 按钮点击事件
        self.drop_label.bind('<Button-1>', lambda e: self.browse_folder())
        
        # 当前路径显示
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        path_frame.columnconfigure(1, weight=1)
        
        ttk.Label(path_frame, text="当前路径:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 5)
        )
        self.path_var = tk.StringVar(value="未选择")
        path_entry = ttk.Entry(
            path_frame, textvariable=self.path_var, state='readonly'
        )
        path_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # 文件夹结构预览
        preview_frame = ttk.LabelFrame(
            main_frame, text="文件夹结构预览", padding="5"
        )
        preview_frame.grid(
            row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10)
        )
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        self.preview_text = scrolledtext.ScrolledText(
            preview_frame,
            height=10,
            wrap=tk.NONE,
            font=('Consolas', 9),
            bg='#f8f8f8'
        )
        self.preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置预览文本标签
        self.preview_text.tag_config('folder', foreground='#0066cc', font=('Consolas', 9, 'bold'))
        self.preview_text.tag_config('media', foreground='#009900')
        self.preview_text.tag_config('other', foreground='#666666')
        self.preview_text.tag_config('count', foreground='#cc6600', font=('Consolas', 9, 'bold'))
        
        self.preview_text.insert(tk.END, "📂 等待选择文件夹...\n", 'folder')
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, pady=(0, 10))
        
        self.browse_btn = ttk.Button(
            button_frame,
            text="📂 选择文件夹",
            command=self.browse_folder,
            width=20
        )
        self.browse_btn.pack(side=tk.LEFT, padx=5)
        
        self.process_btn = ttk.Button(
            button_frame,
            text="▶️ 开始处理",
            command=self.start_processing,
            width=20,
            state=tk.DISABLED
        )
        self.process_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(
            button_frame,
            text="🗑️ 清空日志",
            command=self.clear_log,
            width=20
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # 进度条
        self.progress_var = tk.StringVar(value="就绪")
        progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        progress_label.grid(row=6, column=0, sticky=tk.W, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(
            main_frame, mode='indeterminate', length=300
        )
        self.progress_bar.grid(
            row=7, column=0, sticky=(tk.W, tk.E), pady=(0, 10)
        )
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="处理日志", padding="5")
        log_frame.grid(row=8, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(8, weight=2)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            wrap=tk.WORD,
            font=('Consolas', 9)
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置日志文本标签
        self.log_text.tag_config('info', foreground='black')
        self.log_text.tag_config('success', foreground='green')
        self.log_text.tag_config('warning', foreground='orange')
        self.log_text.tag_config('error', foreground='red')
        self.log_text.tag_config('header', foreground='blue', font=('Consolas', 9, 'bold'))
        
        self.log("程序已启动，等待选择文件夹...\n", 'info')
        
    def on_drag_enter(self, event):
        """拖拽进入时"""
        self.drop_label.config(bg='#e0f0ff', fg='#0066cc')
        
    def on_drag_leave(self, event):
        """拖拽离开时"""
        self.drop_label.config(bg='#f0f0f0', fg='#666')
        
    def on_drop(self, event):
        """处理拖拽释放"""
        self.drop_label.config(bg='#f0f0f0', fg='#666')
        
        # 获取拖拽的路径
        files = self.root.tk.splitlist(event.data)
        if files:
            folder_path = files[0].strip('{}')
            if os.path.isdir(folder_path):
                self.set_folder(folder_path)
            else:
                messagebox.showerror("错误", "请拖拽文件夹，而不是文件")
    
    def browse_folder(self):
        """浏览选择文件夹"""
        from tkinter import filedialog
        folder_path = filedialog.askdirectory(title="选择总文件夹")
        if folder_path:
            self.set_folder(folder_path)
    
    def set_folder(self, folder_path):
        """设置文件夹路径"""
        self.path_var.set(folder_path)
        self.process_btn.config(state=tk.NORMAL)
        self.log(f"\n已选择文件夹: {folder_path}\n", 'success')
        
        # 显示文件夹结构
        self.show_folder_structure(folder_path)
    
    def show_folder_structure(self, folder_path):
        """显示文件夹结构"""
        self.preview_text.delete(1.0, tk.END)
        
        try:
            root_path = Path(folder_path)
            mode = self.mode_var.get()
            
            # 统计信息
            total_folders = 0
            total_media = 0
            total_other = 0
            
            self.preview_text.insert(tk.END, f"📂 {root_path.name}\n", 'folder')
            
            if mode == "single":
                # 单个模式：显示当前文件夹的子文件夹结构
                items = sorted(root_path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
                for item in items:
                    if item.is_dir():
                        total_folders += 1
                        media_count, other_count = self.count_files_in_folder(item)
                        total_media += media_count
                        total_other += other_count
                        
                        self.preview_text.insert(tk.END, "│   ├── 📁 ", 'other')
                        self.preview_text.insert(tk.END, f"{item.name}", 'folder')
                        
                        if media_count > 0 or other_count > 0:
                            self.preview_text.insert(tk.END, f"  [{media_count} 媒体, {other_count} 其他]", 'count')
                        self.preview_text.insert(tk.END, "\n")
                        
                        # 显示子文件夹的前几个文件
                        self.show_subfolder_files(item, "│   │   ", max_files=3)
            else:
                # 批量模式：显示所有子文件夹
                subfolders = [f for f in root_path.iterdir() if f.is_dir()]
                for idx, subfolder in enumerate(sorted(subfolders, key=lambda x: x.name)):
                    total_folders += 1
                    is_last = (idx == len(subfolders) - 1)
                    prefix = "└── " if is_last else "├── "
                    
                    media_count, other_count = self.count_files_recursive(subfolder)
                    total_media += media_count
                    total_other += other_count
                    
                    self.preview_text.insert(tk.END, prefix + "📁 ", 'other')
                    self.preview_text.insert(tk.END, f"{subfolder.name}", 'folder')
                    
                    if media_count > 0 or other_count > 0:
                        self.preview_text.insert(tk.END, f"  [{media_count} 媒体, {other_count} 其他]", 'count')
                    self.preview_text.insert(tk.END, "\n")
                    
                    # 显示子文件夹的第一层子文件夹
                    child_prefix = "    " if is_last else "│   "
                    child_folders = [f for f in subfolder.iterdir() if f.is_dir()]
                    for child in sorted(child_folders, key=lambda x: x.name)[:3]:
                        child_media, child_other = self.count_files_in_folder(child)
                        self.preview_text.insert(tk.END, f"{child_prefix}├── 📁 ", 'other')
                        self.preview_text.insert(tk.END, f"{child.name}", 'folder')
                        if child_media > 0:
                            self.preview_text.insert(tk.END, f"  [{child_media} 媒体]", 'count')
                        self.preview_text.insert(tk.END, "\n")
                    
                    if len(child_folders) > 3:
                        self.preview_text.insert(tk.END, f"{child_prefix}└── ... 还有 {len(child_folders) - 3} 个文件夹\n", 'other')
            
            # 显示统计信息
            self.preview_text.insert(tk.END, "\n" + "─" * 50 + "\n", 'other')
            self.preview_text.insert(tk.END, f"📊 统计: ", 'folder')
            self.preview_text.insert(tk.END, f"{total_folders} 个文件夹, ", 'count')
            self.preview_text.insert(tk.END, f"{total_media} 个媒体文件, ", 'count')
            self.preview_text.insert(tk.END, f"{total_other} 个其他文件\n", 'other')
            
        except Exception as e:
            self.preview_text.insert(tk.END, f"\n❌ 读取文件夹结构失败: {str(e)}\n", 'other')
    
    def show_subfolder_files(self, folder, prefix, max_files=3):
        """显示子文件夹中的文件"""
        try:
            files = [f for f in folder.iterdir() if f.is_file()]
            shown = 0
            for file in sorted(files, key=lambda x: x.name)[:max_files]:
                if self.is_media_file(file):
                    self.preview_text.insert(tk.END, f"{prefix}├── 🖼️ ", 'media')
                    self.preview_text.insert(tk.END, f"{file.name}\n", 'media')
                else:
                    self.preview_text.insert(tk.END, f"{prefix}├── 📄 ", 'other')
                    self.preview_text.insert(tk.END, f"{file.name}\n", 'other')
                shown += 1
            
            if len(files) > max_files:
                self.preview_text.insert(tk.END, f"{prefix}└── ... 还有 {len(files) - max_files} 个文件\n", 'other')
        except Exception:
            pass
    
    def count_files_in_folder(self, folder):
        """统计文件夹中的文件数（不递归）"""
        media_count = 0
        other_count = 0
        try:
            for item in folder.iterdir():
                if item.is_file():
                    if self.is_media_file(item):
                        media_count += 1
                    else:
                        other_count += 1
        except Exception:
            pass
        return media_count, other_count
    
    def count_files_recursive(self, folder):
        """递归统计文件夹中的文件数"""
        media_count = 0
        other_count = 0
        try:
            for item in folder.rglob('*'):
                if item.is_file():
                    if self.is_media_file(item):
                        media_count += 1
                    else:
                        other_count += 1
        except Exception:
            pass
        return media_count, other_count
        
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
        
    def log(self, message, tag='info'):
        """添加日志"""
        self.log_text.insert(tk.END, message, tag)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def start_processing(self):
        """开始处理"""
        if self.is_processing:
            messagebox.showwarning("提示", "正在处理中，请等待...")
            return
            
        folder_path = self.path_var.get()
        if folder_path == "未选择" or not os.path.isdir(folder_path):
            messagebox.showerror("错误", "请先选择有效的文件夹")
            return
        
        # 确认操作
        mode = self.mode_var.get()
        mode_text = "单个模式：只处理当前文件夹" if mode == "single" else "批量模式：处理所有子文件夹"
        
        result = messagebox.askyesno(
            "确认操作",
            f"处理模式: {mode_text}\n\n"
            f"即将处理文件夹:\n{folder_path}\n\n"
            "孙文件夹里的图片和视频将被移动到子文件夹根目录。\n\n"
            "是否继续?"
        )
        
        if not result:
            return
        
        # 在新线程中处理
        self.is_processing = True
        self.process_btn.config(state=tk.DISABLED)
        self.browse_btn.config(state=tk.DISABLED)
        self.progress_bar.start(10)
        self.progress_var.set("处理中...")
        
        thread = threading.Thread(target=self.process_folder, args=(folder_path,))
        thread.daemon = True
        thread.start()
        
    def process_folder(self, root_folder):
        """处理文件夹（在独立线程中运行）"""
        try:
            root_path = Path(root_folder)
            total_moved = 0
            total_skipped = 0
            mode = self.mode_var.get()
            
            self.log("\n" + "=" * 70 + "\n", 'header')
            self.log(f"开始处理文件夹: {root_folder}\n", 'header')
            mode_text = "【单个模式】" if mode == "single" else "【批量模式】"
            self.log(f"处理模式: {mode_text}\n", 'header')
            self.log("=" * 70 + "\n", 'header')
            
            # 根据模式选择要处理的文件夹列表
            if mode == "single":
                # 单个模式：直接处理选中的文件夹本身
                folders_to_process = [root_path]
                self.log(f"\n直接处理文件夹: {root_path.name}\n", 'info')
            else:
                # 批量模式：处理总文件夹下的所有子文件夹
                folders_to_process = [f for f in root_path.iterdir() if f.is_dir()]
                self.log(f"\n将处理 {len(folders_to_process)} 个子文件夹\n", 'info')
            
            # 遍历要处理的文件夹
            for sub_folder in folders_to_process:
                if not sub_folder.is_dir():
                    continue
                
                self.log(f"\n处理文件夹: {sub_folder.name}\n", 'info')
                self.log("-" * 70 + "\n", 'info')
                
                moved_count = 0
                skipped_count = 0
                
                # 遍历文件夹下的所有子文件夹中的文件
                for item in sub_folder.rglob('*'):
                    if item.is_file() and item.parent != sub_folder:
                        if self.is_media_file(item):
                            target_path = sub_folder / item.name
                            
                            # 显示来源路径（相对于处理的文件夹）
                            relative_source = item.relative_to(sub_folder)
                            
                            # 处理文件名冲突
                            if target_path.exists():
                                base_name = item.stem
                                extension = item.suffix
                                counter = 1
                                while target_path.exists():
                                    target_path = sub_folder / f"{base_name}_{counter}{extension}"
                                    counter += 1
                                self.log(f"  [重命名] {relative_source} -> {target_path.name}\n", 'warning')
                            else:
                                self.log(f"  [移动] {relative_source}\n", 'success')
                            
                            try:
                                shutil.move(str(item), str(target_path))
                                moved_count += 1
                            except Exception as e:
                                self.log(f"  [错误] 移动失败: {item.name} - {str(e)}\n", 'error')
                                skipped_count += 1
                
                # 删除空的子文件夹
                try:
                    for item in sub_folder.iterdir():
                        if item.is_dir():
                            self.remove_empty_folders(item)
                except Exception as e:
                    self.log(f"  [警告] 清理空文件夹时出错: {str(e)}\n", 'warning')
                
                self.log(f"\n  小计: 移动 {moved_count} 个文件, 跳过 {skipped_count} 个文件\n", 'info')
                total_moved += moved_count
                total_skipped += skipped_count
            
            self.log("\n" + "=" * 70 + "\n", 'header')
            self.log("处理完成!\n", 'success')
            self.log(f"总计: 移动 {total_moved} 个文件, 跳过 {total_skipped} 个文件\n", 'success')
            self.log("=" * 70 + "\n", 'header')
            
            # 显示完成消息
            self.root.after(0, lambda: messagebox.showinfo(
                "完成",
                f"处理完成!\n\n移动: {total_moved} 个文件\n跳过: {total_skipped} 个文件"
            ))
            
        except Exception as e:
            self.log(f"\n[错误] 处理失败: {str(e)}\n", 'error')
            self.root.after(0, lambda: messagebox.showerror("错误", f"处理失败:\n{str(e)}"))
        
        finally:
            # 恢复界面状态
            self.is_processing = False
            self.root.after(0, self.processing_complete)
    
    def processing_complete(self):
        """处理完成后恢复界面"""
        self.progress_bar.stop()
        self.progress_var.set("就绪")
        self.process_btn.config(state=tk.NORMAL)
        self.browse_btn.config(state=tk.NORMAL)
    
    def is_media_file(self, file_path):
        """判断文件是否为图片或视频"""
        return file_path.suffix.lower() in MEDIA_EXTENSIONS
    
    def remove_empty_folders(self, folder_path):
        """递归删除空文件夹"""
        folder = Path(folder_path)
        
        if not folder.exists() or not folder.is_dir():
            return
        
        # 先处理子文件夹
        for item in folder.iterdir():
            if item.is_dir():
                self.remove_empty_folders(item)
        
        # 检查当前文件夹是否为空
        try:
            if not any(folder.iterdir()):
                self.log(f"  [删除空文件夹] {folder.name}\n", 'warning')
                folder.rmdir()
        except Exception:
            pass


def main():
    """主函数"""
    try:
        root = TkinterDnD.Tk()
    except:
        print("警告: tkinterdnd2 未正确安装，拖拽功能将受限")
        root = tk.Tk()
    
    app = MediaMoverGUI(root)
    
    # 设置窗口图标（如果有的话）
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    # 窗口居中
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()
