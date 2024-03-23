def read_markdown_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        print(f"文件未找到： {file_path}")
    except Exception as e:
        print(f"读取文件时发生错误： {e}")

# 使用函数读取Markdown文件
file_path = './files\\Newtest_translated.md'  # 替换为您的Markdown文件路径
markdown_content = read_markdown_file(file_path)

if markdown_content:
    print(markdown_content)

print(file_path.replace('\\','/'))