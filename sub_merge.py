import os
import base64
import requests
import json

NAME = "订阅合并"

# 定义需要替换的关键字列表
replace_keywords = [
    "xxxxx",
    "xxxxx"
]

# 定义你的订阅链接列表
subscription_urls = [
    "https://abcd.com/sub1",
    "https://abcd.com/sub2"
]

# 获取和处理每个订阅链接的内容
def fetch_and_process_subscriptions(urls):
    all_contents = []

    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            content = response.text
            if is_base64_encoded(content):
                decoded_content = base64.b64decode(content).decode('utf-8')
                processed_content = process_content(decoded_content)
                all_contents.append(processed_content)
            else:
                processed_content = process_content(content)
                all_contents.append(processed_content)
        else:
            print(f"Failed to fetch content from {url}")

    combined_content = "\n".join(all_contents)
    final_encoded_content = base64.b64encode(combined_content.encode('utf-8')).decode('utf-8')
    return final_encoded_content

# 检查内容是否为base64编码
def is_base64_encoded(data):
    try:
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        elif isinstance(data, bytes):
            data_bytes = data
        else:
            raise ValueError("Input must be a string or bytes")

        return base64.b64encode(base64.b64decode(data_bytes)) == data_bytes
    except Exception:
        return False

# 处理解码后的内容，只修改指定信息
def process_content(content):
    lines = content.splitlines()
    processed_lines = []

    for line in lines:
        if line.startswith("vmess://"):
            vmess_encoded_part = line[len("vmess://"):]

            # 调整Base64字符串长度为4的倍数
            vmess_encoded_part = fix_base64_padding(vmess_encoded_part)

            vmess_decoded = base64.b64decode(vmess_encoded_part).decode('utf-8')
            vmess_dict = json.loads(vmess_decoded)

            # 只修改'ps'字段，保留其余内容
            vmess_dict['ps'] = replace_specified_info(vmess_dict.get('ps', ''))

            vmess_encoded_modified = base64.b64encode(json.dumps(vmess_dict).encode('utf-8')).decode('utf-8')
            processed_lines.append(f"vmess://{vmess_encoded_modified}")
        else:
            # 对非vmess协议的内容，替换指定的关键字
            processed_line = replace_specified_info(line)
            processed_lines.append(processed_line)

    return "\n".join(processed_lines)

# 替换指定信息的函数
def replace_specified_info(text):
    for keyword in replace_keywords:
        text = text.replace(keyword, NAME)
    return text

# 修正Base64字符串长度
def fix_base64_padding(data):
    missing_padding = len(data) % 4
    if missing_padding != 0:
        data += '=' * (4 - missing_padding)
    return data

final_content = fetch_and_process_subscriptions(subscription_urls)

# 将结果写入sub.txt文件
with open('sub.txt', 'w') as file:
    file.write(final_content)

print("总订阅节点已写入sub.txt文件")
