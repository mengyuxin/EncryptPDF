#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# ==============================================================================
# EncryptPDF.py — PDF 文件加密工具 / PDF Encryption Tool
#
# 功能 / Features:
#   1. 为 PDF 文件添加随机密码（防止被修改）/ Add a random password to PDF
#   2. 支持自定义密码 / Support custom passwords
#   3. 支持批量处理多个 PDF / Batch process multiple PDFs
#   4. 支持替换原文件或保留副本 / Overwrite original or keep a copy
#   5. 支持设置权限（禁止打印/复制等）/ Set PDF permissions
#
# 作者 / Created by: Meng Yuxin
# 创建日期 / Created on: 2017-12-24
# 最后更新 / Last updated: 2026-05-17
# ==============================================================================
#
# 依赖安装 / Installation:
#   pip install pypdf
#
# 使用示例 / Usage Examples:
#   1. 加密单个 PDF（自动生成密码）/ Encrypt single PDF (auto password):
#      python EncryptPDF.py -i sample.pdf
#
#   2. 加密并设置自定义密码 / Encrypt with custom password:
#      python EncryptPDF.py -i sample.pdf -p mypassword
#
#   3. 加密并替换原文件 / Encrypt and overwrite original:
#      python EncryptPDF.py -i sample.pdf --replace
#
#   4. 批量加密所有 PDF / Batch encrypt all PDFs:
#      python EncryptPDF.py -i "./docs/*.pdf"
#
#   5. 设置权限（禁止打印和复制）/ Restrict permissions:
#      python EncryptPDF.py -i sample.pdf --no-print --no-copy
#
# 参考文献 / References:
#   - pypdf: https://pypi.org/project/pypdf/
#   - pypdf 文档: https://pypdf.readthedocs.io/
# ==============================================================================

import os           # 文件路径处理 / File path handling
import sys          # 系统退出 / System exit
import random       # 随机密码生成 / Random password generation
import glob         # 批量文件匹配 / Batch file matching (wildcard)
import argparse     # 命令行参数解析 / Command-line argument parsing
from datetime import datetime  # 记录操作时间 / Record operation timestamp

# 尝试导入 pypdf（PyPDF2 的现代继任者）
# Try to import pypdf (the modern successor of PyPDF2)
try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("【错误 / Error】请先安装 pypdf 库: pip install pypdf")
    print("        Please install pypdf first: pip install pypdf")
    sys.exit(1)


def generate_password(length: int = 32) -> str:
    """
    生成随机密码 / Generate a random password

    从字母、数字和特殊符号的混合字符集中随机选取，
    确保密码强度足够用于 PDF 加密保护。
    Selects random characters from a mix of letters, digits,
    and special symbols to ensure strong PDF encryption.

    参数 / Args:
        length: 密码长度，默认32位 / Password length, default 32

    返回 / Returns:
        生成的随机密码字符串 / Generated random password string
    """
    # 字符集：数字 + 大小写字母 + 常用特殊符号
    # Character set: digits + uppercase/lowercase letters + common symbols
    chars = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()'
    # 用 random.SystemRandom（基于系统随机源，比 random 更安全）
    # Use SystemRandom (based on OS randomness source, more secure than random)
    secure_rand = random.SystemRandom()
    password = ''.join(secure_rand.sample(chars, length))
    return password


def get_output_path(input_path: str, suffix: str = "_encrypted") -> str:
    """
    生成加密后的输出文件路径 / Generate output file path after encryption

    策略 / Strategy:
      - 如果 input 是 "xxx.pdf"，输出为 "xxx_encrypted.pdf"
      - If input is "xxx.pdf", output becomes "xxx_encrypted.pdf"

    参数 / Args:
        input_path:  原文件路径 / Original file path
        suffix:      文件名后缀，默认 "_encrypted" / Filename suffix

    返回 / Returns:
        加密后的文件路径 / Path for the encrypted file
    """
    base, ext = os.path.splitext(input_path)
    return f"{base}{suffix}{ext}"


def encrypt_pdf(
    input_path: str,
    output_path: str,
    user_password: str = "",
    owner_password: str = "",
    use_128bit: bool = True,
    allow_print: bool = True,
    allow_copy: bool = True,
    allow_modify: bool = False,
) -> bool:
    """
    加密 PDF 文件 / Encrypt a PDF file

    使用 pypdf 的加密功能给 PDF 添加密码保护。
    支持分别设置用户密码（打开密码）和所有者密码（权限密码）。
    Uses pypdf's encryption to password-protect a PDF file.
    Supports separate user password (open password) and
    owner password (permissions password).

    参数 / Args:
        input_path:   输入文件路径 / Input file path
        output_path:  输出文件路径 / Output file path
        user_password:  用户密码（打开文件需要）/ User password (to open the file)
        owner_password: 所有者密码（修改权限需要）/ Owner password (to change permissions)
        use_128bit:     是否使用128位加密（否则40位）/ Use 128-bit encryption (else 40-bit)
        allow_print:    是否允许打印 / Allow printing
        allow_copy:     是否允许复制内容 / Allow copying content
        allow_modify:   是否允许修改 / Allow modifications

    返回 / Returns:
        True 表示成功 / True on success, False on failure
    """
    try:
        # ----- 第一步：读取原 PDF / Step 1: Read the original PDF -----
        print(f"  📖 读取文件 / Reading file: {input_path}")
        reader = PdfReader(input_path)

        # 检查 PDF 是否已被加密
        # Check if the PDF is already encrypted
        if reader.is_encrypted:
            print("  ⚠️  该 PDF 已经加密，跳过 / This PDF is already encrypted, skipping")
            return False

        total_pages = len(reader.pages)
        print(f"  📄 共 {total_pages} 页 / Total {total_pages} pages")

        # ----- 第二步：创建写入器并逐页复制 / Step 2: Create writer & copy pages -----
        writer = PdfWriter()

        for page_num in range(total_pages):
            writer.add_page(reader.pages[page_num])
            # 超过 10 页时显示进度 / Show progress for PDFs with >10 pages
            if total_pages > 10 and (page_num + 1) % 10 == 0:
                print(f"  ⏳ 进度 / Progress: {page_num + 1}/{total_pages} 页")

        # ----- 第三步：设置加密 / Step 3: Apply encryption -----
        """
        关于 PDF 加密 / About PDF encryption:
        - 用户密码 (user_password): 打开 PDF 时需要输入的密码
        - 所有者密码 (owner_password): 修改权限时需要的密码
          如果设置了所有者密码但用户密码为空，则打开时无需密码，
          但修改/打印等操作受权限限制（即"保护模式"）。
        - 128位加密 比 40位加密 更安全

        - User password: required to OPEN the PDF
        - Owner password: required to CHANGE permissions
          If owner password is set but user password is empty,
          the PDF opens without a password but operations like
          printing/editing are restricted ("protected mode").
        - 128-bit is more secure than 40-bit encryption
        """
        writer.encrypt(
            user_password=user_password,
            owner_password=owner_password,
            use_128bit=use_128bit,
            permissions_flag=(
                (0b0100 if allow_print else 0) |     # 打印权限 / Print permission
                (0b0001 if allow_copy else 0) |       # 复制权限 / Copy permission
                (0b1000 if allow_modify else 0)        # 修改权限 / Modify permission
            ),
        )

        # ----- 第四步：写入加密后的文件 / Step 4: Write encrypted file -----
        print(f"  💾 写入加密文件 / Writing encrypted file: {output_path}")
        with open(output_path, "wb") as f:
            writer.write(f)

        # 验证文件是否成功创建且大小合理
        # Verify the file was created successfully with reasonable size
        file_size = os.path.getsize(output_path)
        if file_size == 0:
            print("  ❌ 错误：输出文件为空 / Error: output file is empty")
            return False

        print(f"  ✅ 加密成功！文件大小 / File size: {file_size:,} 字节/bytes")
        return True

    except FileNotFoundError:
        print(f"  ❌ 错误：找不到文件 / File not found: {input_path}")
        return False
    except PermissionError:
        print(f"  ❌ 错误：没有权限读取或写入 / Permission denied")
        return False
    except Exception as e:
        print(f"  ❌ 加密失败 / Encryption failed: {e}")
        return False


def process_single_file(
    input_path: str,
    replace: bool = False,
    user_password: str = "",
    owner_password: str = "",
    use_128bit: bool = True,
    allow_print: bool = True,
    allow_copy: bool = True,
    allow_modify: bool = False,
) -> bool:
    """
    处理单个 PDF 文件 / Process a single PDF file

    根据参数决定是替换原文件还是创建副本。
    Decides whether to replace the original or create a copy.

    参数 / Args:
        input_path: PDF 文件路径 / PDF file path
        replace: 是否替换原文件 / Whether to replace the original file
        user_password:  用户密码 / User password
        owner_password: 所有者密码 / Owner password
        use_128bit:     是否128位加密 / Use 128-bit encryption
        allow_print:    允许打印 / Allow printing
        allow_copy:     允许复制 / Allow copying
        allow_modify:   允许修改 / Allow modifications

    返回 / Returns:
        True 表示成功 / True on success
    """
    # 检查文件是否存在 / Check if file exists
    if not os.path.isfile(input_path):
        print(f"  ❌ 文件不存在 / File does not exist: {input_path}")
        return False

    # 检查是否为 PDF 文件 / Check if it's a PDF file
    if not input_path.lower().endswith('.pdf'):
        print(f"  ⚠️  跳过非 PDF 文件 / Skipping non-PDF file: {input_path}")
        return False

    print(f"\n{'='*60}")
    print(f"🔐 处理 / Processing: {input_path}")

    # 确定输出路径 / Determine output path
    if replace:
        # 如果要替换原文件，先生成临时文件，加密成功后再替换
        # If replacing, encrypt to a temp file first, then swap
        temp_output = get_output_path(input_path, suffix="_temp_encrypted")
        final_output = input_path
        print(f"  🔄 将替换原文件 / Will replace the original file")
    else:
        temp_output = get_output_path(input_path)
        final_output = temp_output
        print(f"  📁 将创建副本 / Will create a copy: {temp_output}")

    # 执行加密 / Execute encryption
    success = encrypt_pdf(
        input_path=input_path,
        output_path=temp_output,
        user_password=user_password,
        owner_password=owner_password,
        use_128bit=use_128bit,
        allow_print=allow_print,
        allow_copy=allow_copy,
        allow_modify=allow_modify,
    )

    if not success:
        # 清理临时文件 / Clean up temp file
        if os.path.exists(temp_output):
            os.remove(temp_output)
        return False

    # 如果需要替换原文件，执行替换操作
    # If replacing, perform the swap
    if replace and success:
        import shutil
        # 备份原文件，以防万一 / Backup just in case
        backup_path = get_output_path(input_path, suffix="_backup")
        print(f"  💾 备份原文件 / Backing up original to: {backup_path}")
        shutil.copy2(input_path, backup_path)
        # 用加密后的文件覆盖原文件 / Replace original with encrypted version
        shutil.move(temp_output, input_path)
        print(f"  🔄 已替换原文件 / Original file replaced")
        print(f"  📦 备份保存于 / Backup saved at: {backup_path}")

    return True


def main():
    """
    主函数：解析命令行参数并执行加密 / Main function: parse args & run encryption

    使用 argparse 解析用户输入的命令行参数，然后调用加密函数。
    Uses argparse to parse CLI arguments, then calls the encryption function.
    """
    # =========================================================================
    # 解析命令行参数 / Parse command-line arguments
    # =========================================================================
    parser = argparse.ArgumentParser(
        description="""
        PDF 文件加密工具 / PDF Encryption Tool
        ------------------------------------------------------------
        给 PDF 文件添加密码保护，防止被修改或未经授权访问。
        Add password protection to PDF files to prevent unauthorized
        modification or access.
        """,
        # 自定义帮助信息的格式 / Customize help text formatting
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        使用示例 / Examples:
        --------------------------------
        # 1. 基本用法：加密单个 PDF
        %(prog)s -i document.pdf

        # 2. 指定自定义密码
        %(prog)s -i document.pdf -p mypass123

        # 3. 加密后替换原文件（自动备份）
        %(prog)s -i document.pdf --replace

        # 4. 批量加密当前目录下所有 PDF
        %(prog)s -i "*.pdf"

        # 5. 禁止打印和复制
        %(prog)s -i document.pdf --no-print --no-copy
        --------------------------------
        作者 / Author: Meng Yuxin
        """,
    )

    # ---- 必需参数 / Required arguments ----
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="输入 PDF 文件（支持通配符 *.pdf）/ Input PDF file (supports wildcards)",
    )

    # ---- 密码选项 / Password options ----
    parser.add_argument(
        "-p", "--password",
        default="",
        help="指定用户密码（不指定则随机生成）/ Custom user password (auto-generated if empty)",
    )
    parser.add_argument(
        "--owner-password",
        default="",
        help="所有者密码，控制权限修改（不指定则与用户密码相同）"
             "/ Owner password (defaults to user password if not set)",
    )
    parser.add_argument(
        "--password-length",
        type=int,
        default=32,
        help="自动生成密码的长度（默认32位）/ Auto-generated password length (default: 32)",
    )

    # ---- 输出选项 / Output options ----
    parser.add_argument(
        "--replace",
        action="store_true",
        help="加密后替换原文件（自动创建备份）/ Replace original file after encryption (auto backup)",
    )

    # ---- 加密选项 / Encryption options ----
    parser.add_argument(
        "--40bit",
        action="store_true",
        help="使用 40 位加密（默认 128 位）/ Use 40-bit encryption (default is 128-bit)",
    )

    # ---- 权限选项 / Permission options ----
    parser.add_argument(
        "--no-print",
        action="store_true",
        help="禁止打印 / Disallow printing",
    )
    parser.add_argument(
        "--no-copy",
        action="store_true",
        help="禁止复制内容 / Disallow copying content",
    )
    parser.add_argument(
        "--allow-modify",
        action="store_true",
        help="允许修改文档（默认禁止）/ Allow modifications (disabled by default)",
    )

    # ---- 其它选项 / Other options ----
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="静默模式，只输出密码 / Quiet mode, only show the password",
    )

    # =========================================================================
    # 开始处理 / Start processing
    # =========================================================================
    args = parser.parse_args()

    # 确定密码 / Determine passwords
    if args.password:
        # 用户指定了密码 / User specified a password
        user_password = args.password
        # 如果未指定所有者密码，默认与用户密码相同
        # If owner password not specified, default to user password
        owner_password = args.owner_password if args.owner_password else user_password
        password_was_auto_generated = False
    else:
        # 自动生成密码 / Auto-generate password
        user_password = generate_password(args.password_length)
        # 如果未指定所有者密码，也自动生成（区别于用户密码）
        owner_password = args.owner_password if args.owner_password else user_password
        password_was_auto_generated = True

    # 权限设置 / Permission settings
    allow_print = not args.no_print
    allow_copy = not args.no_copy
    allow_modify = args.allow_modify
    use_128bit = not getattr(args, '40bit')

    # 使用 glob 展开输入路径（支持 *.pdf 等通配符）
    # Expand input path (support wildcards like *.pdf)
    input_files = glob.glob(args.input, recursive=False)

    # 如果 glob 没匹配到任何文件，尝试当作精确文件名
    # If glob didn't match anything, try as exact filename
    if not input_files:
        if os.path.isfile(args.input):
            input_files = [args.input]
        else:
            print(f"❌ 没有找到匹配的文件 / No matching files found: {args.input}")
            sys.exit(1)

    # =========================================================================
    # 输出概要信息 / Print summary info
    # =========================================================================
    if not args.quiet:
        print(f"\n{'='*60}")
        print(f"🔒 PDF 加密工具 / PDF Encryption Tool")
        print(f"{'='*60}")
        print(f"📂 待处理文件 / Files to process: {len(input_files)} 个")
        print(f"🔐 加密强度 / Encryption: {'128-bit' if use_128bit else '40-bit'}")
        print(f"🖨️  打印权限 / Print: {'✅ 允许/Allowed' if allow_print else '❌ 禁止/Denied'}")
        print(f"📋 复制权限 / Copy: {'✅ 允许/Allowed' if allow_copy else '❌ 禁止/Denied'}")
        print(f"✏️  修改权限 / Modify: {'✅ 允许/Allowed' if allow_modify else '❌ 禁止/Denied'}")
        print(f"{'='*60}\n")

    # =========================================================================
    # 逐个处理文件 / Process each file
    # =========================================================================
    success_count = 0
    fail_count = 0

    for file_path in sorted(input_files):
        result = process_single_file(
            input_path=file_path,
            replace=args.replace,
            user_password=user_password,
            owner_password=owner_password if args.owner_password else user_password,
            use_128bit=use_128bit,
            allow_print=allow_print,
            allow_copy=allow_copy,
            allow_modify=allow_modify,
        )
        if result:
            success_count += 1
        else:
            fail_count += 1

    # =========================================================================
    # 输出最终结果 / Print final results
    # =========================================================================
    print(f"\n{'='*60}")
    print(f"📊 处理完成 / Processing complete:")
    print(f"   ✅ 成功 / Success: {success_count} 个文件")
    if fail_count > 0:
        print(f"   ❌ 失败 / Failed: {fail_count} 个文件")
    print(f"{'='*60}")

    # 输出密码信息（非常重要！用户需要记下来）
    # Print password info (very important! User needs to save this)
    print(f"\n{'🔑'*30}")
    print(f"🔑=============  密码信息 / PASSWORD INFORMATION  =============🔑")
    print(f"{'🔑'*30}")
    if password_was_auto_generated or args.password:
        if user_password:
            print(f"   用户密码 / User password: {user_password}")
    if args.owner_password:
        print(f"   所有者密码 / Owner password: {owner_password}")
    print(f"\n   ⚠️  请务必保存好以上密码！")
    print(f"   ⚠️  Please save these passwords securely!")
    print(f"   ⚠️  密码不会存储在文件中 / Passwords are NOT stored in the files.")
    print(f"{'🔑'*30}\n")


# ==============================================================================
# 程序入口 / Program Entry Point
# ==============================================================================
if __name__ == "__main__":
    main()
