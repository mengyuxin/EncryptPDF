# 🔒 EncryptPDF — PDF 文件加密保护工具

> 给 PDF 文件一键加密，防止被篡改或未经授权访问。
> 轻量级、单文件、纯 Python 实现，开箱即用。

## ✨ 功能特性

- **🔐 自动生成强密码** — 32 位随机密码（含数字、大小写字母、特殊符号）
- **✏️ 自定义密码** — 支持指定自己的密码
- **🔄 替换原文件** — 加密后直接替换原文件，并自动备份
- **📦 批量处理** — 支持通配符 `*.pdf`，一次加密整个目录
- **🚫 权限控制** — 可禁止打印、禁止复制内容（保护模式）
- **⚡ 加密强度可选** — 默认 128 位加密，可选 40 位
- **💡 中英双语注释** — 代码注释同时包含中文和英文，方便学习

## 📦 安装

### 1. 安装 Python 3

确保你的系统已安装 Python 3.7 或更高版本：

```bash
python3 --version
```

### 2. 安装依赖

只需要一个依赖库 `pypdf`（PyPDF2 的现代继任者）：

```bash
pip install pypdf
```

如果遇到权限问题，尝试：

```bash
pip install --user pypdf
```

### 3. 下载脚本

```bash
curl -O https://raw.githubusercontent.com/mengyuxin/EncryptPDF/master/EncryptPDF.py
```

## 🚀 快速上手

### 基本用法 — 加密一个 PDF

```bash
python EncryptPDF.py -i 文件.pdf
```

加密完成后，会在同目录下生成 `文件_encrypted.pdf`，**并在终端显示密码**。

### 自定义密码

```bash
python EncryptPDF.py -i 文件.pdf -p 我的密码123
```

### 加密后替换原文件（自动备份）

```bash
python EncryptPDF.py -i 文件.pdf --replace
```

原始文件会自动备份为 `文件_backup.pdf`。

### 批量加密所有 PDF

```bash
python EncryptPDF.py -i "*.pdf"
```

### 禁止打印和复制

```bash
python EncryptPDF.py -i 文件.pdf --no-print --no-copy
```

这样即使用户密码打开后，也无法打印或复制内容（Acrobat Reader 中会显示为灰色）。

### 完整参数列表

| 参数 | 说明 |
|------|------|
| `-i, --input` | **必需**。输入 PDF 文件，支持通配符（如 `*.pdf`） |
| `-p, --password` | 指定用户密码。不指定则自动生成 32 位随机密码 |
| `--owner-password` | 所有者密码（用于修改权限）。不指定则与用户密码相同 |
| `--password-length` | 自动生成密码的长度，默认 32 |
| `--replace` | 加密后替换原文件（自动创建 `.bak` 备份） |
| `--40bit` | 使用 40 位加密（默认使用更安全的 128 位） |
| `--no-print` | 禁止打印文档 |
| `--no-copy` | 禁止复制文档内容 |
| `--allow-modify` | 允许修改文档（默认禁止） |
| `-q, --quiet` | 静默模式，只输出密码信息 |

## 📖 原理说明

PDF 加密通过 **pypdf** 库实现，支持两种密码：

1. **用户密码（User Password）**
   - 打开 PDF 文件时需要输入的密码
   - 也就是最常见的"打开密码"
   - 如果只设置用户密码，任何人都可以用它打开并查看内容

2. **所有者密码（Owner Password）**
   - 控制权限修改的密码
   - 设置了所有者密码但没有用户密码时：**打开不需要密码**，但打印、复制等操作受限制（保护模式）
   - 典型场景：把 PDF 发布到网站上，任何人都可以阅读，但不能打印或复制

> 本工具默认行为：自动生成一个随机密码，同时作为用户密码和所有者密码。这样打开文件需要密码，且无法自由修改权限。可以用 `--owner-password` 单独设置。

## 📋 使用场景

- **保护合同/协议** — 加密后发给客户，防止被篡改
- **个人文档备份** — 敏感文件加密存储
- **发布受控文档** — 禁止读者打印或复制内容
- **批量处理** — 一次加密整个文件夹的所有 PDF

## 🛠️ 技术栈

| 组件 | 说明 |
|------|------|
| Python 3 | 脚本语言 |
| pypdf | 纯 Python PDF 处理库（PyPDF2 的继任者） |
| argparse | 命令行参数解析 |
| glob | 批量文件通配符匹配 |
| random.SystemRandom | 操作系统级随机数生成（更安全的随机密码） |

## 📄 许可证

本项目基于 MIT 许可证开源。

## 👤 作者

**Meng Yuxin**

- GitHub: [@mengyuxin](https://github.com/mengyuxin)

## ⭐ 欢迎贡献

觉得好用的话，点个 Star 吧！发现 Bug 或有改进建议，欢迎提交 Issue 或 Pull Request。
