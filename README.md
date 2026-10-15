# 批量移动媒体文件工具

一个支持图形界面和拖拽操作的Python工具，用于批量整理文件夹中的图片和视频文件。

## 功能特点

- ✅ **图形界面** - 友好的GUI界面，易于操作
- ✅ **拖拽支持** - 支持拖拽文件夹到窗口
- ✅ **批量处理** - 自动处理所有子文件夹
- ✅ **多格式支持** - 支持常见的图片和视频格式
- ✅ **智能重命名** - 自动处理文件名冲突
- ✅ **实时日志** - 显示详细的处理过程
- ✅ **自动清理** - 处理完成后删除空文件夹

## 支持的文件格式

**图片格式**: jpg, jpeg, png, gif, bmp, webp, tiff, svg, ico

**视频格式**: mp4, avi, mov, wmv, flv, mkv, webm, m4v, mpeg, mpg

## 使用方法

### 方法一：使用启动脚本（推荐）
1. 双击运行 `启动程序.bat`
2. 程序会自动检查并安装依赖
3. 拖拽文件夹到窗口或点击"选择文件夹"按钮
4. 点击"开始处理"按钮

### 方法二：直接运行Python程序
1. 确保已安装依赖（仅拖拽功能需要；不安装时仍可用“选择文件夹”按钮）：
   ```bash
   pip install tkinterdnd2
   ```

2. 运行GUI版本：
   ```bash
   python move_media_files_gui.py
   ```

3. 运行命令行版本：
   ```bash
   python move_media_files.py
   ```

## 使用场景

假设你有如下文件结构：
```
总文件夹/
├── 旅游照片/
│   ├── 北京/
│   │   ├── IMG001.jpg
│   │   └── VID001.mp4
│   └── 上海/
│       └── IMG002.jpg
└── 家庭视频/
    └── 2024/
        └── video.mp4
```

处理后会变成：
```
总文件夹/
├── 旅游照片/
│   ├── IMG001.jpg
│   ├── VID001.mp4
│   └── IMG002.jpg
└── 家庭视频/
    └── video.mp4
```

所有子文件夹中的媒体文件都会被移动到对应的父文件夹中，空文件夹会被自动删除。

## 安全提示

- ⚠️ 处理前建议备份重要文件
- ⚠️ 确认文件夹路径正确后再开始处理
- ⚠️ 处理过程不可撤销

## 系统要求

- Windows 10/11
- Python 3.7+（GUI 依赖标准库 tkinter）
- 依赖包：tkinterdnd2（可选，仅用于拖拽文件夹；未安装时不影响按钮选择与命令行版本）

## 文件说明

- `move_media_files_gui.py` - 图形界面版本（推荐）
- `move_media_files.py` - 命令行版本
- `启动程序.bat` - Windows启动脚本
- `README.md` - 说明文档

## 故障排除

**问题：拖拽功能不可用**
- 解决：确保已安装 `tkinterdnd2` 包

**问题：程序无法启动**
- 解决：检查Python版本是否 >= 3.7

**问题：找不到文件**
- 解决：确保文件路径中没有特殊字符

## 更新日志

**v2.0** (2025-11-15)
- 新增图形界面版本
- 支持拖拽操作
- 实时显示处理日志
- 优化用户体验

**v1.0** (2025-11-15)
- 初始版本
- 命令行界面
- 基础文件移动功能

## License & Attribution / 许可与来源

Original project code authored for this repository is released under the MIT License; see [LICENSE](./LICENSE).

When reusing or redistributing a substantial portion, retain the LICENSE and its copyright notice. The copyright notice includes this original source URL: https://github.com/change979666/media-file-organizer. Please keep the source link visible in your redistributed source or project documentation.

This license applies only to original material that the repository maintainer has the right to license. Third-party libraries, vendor code, platform SDKs, trademarks, screenshots, icons, fonts, and other external assets remain subject to their respective licenses and terms. Review those terms before reuse.

**Project status:** personal/archived project, shared as-is. Maintenance, compatibility, and production readiness are not guaranteed.
