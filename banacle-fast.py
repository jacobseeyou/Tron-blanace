import requests
import pandas as pd
import time
from tqdm import tqdm
import logging
import concurrent.futures

# 配置日志
logging.basicConfig(filename='.venv/error.log', level=logging.ERROR)


def make_api_request(api_key, address=None):
    try:
        # 构建HTTP请求标头
        headers = {
            'TRON-PRO-API-KEY': api_key
        }

        # 如果提供了地址，则构建API请求URL
        if address:
            url = f'https://apilist.tronscanapi.com/api/account/tokens?address={address}&token=USDT'
        else:
            # 否则，获取所有地址的数据
            url = 'https://apilist.tronscanapi.com/api/block'

        # 发送HTTP GET请求
        response = requests.get(url, headers=headers)

        # 检查响应状态码
        if response.status_code == 200:
            # 如果响应成功，则返回响应的JSON数据
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except requests.RequestException as e:
        # 记录错误到日志文件
        logging.error(f"Error making API request: {e}")
        return None


def process_address(api_key, address):
    # 调用函数执行API请求并获取响应
    response = make_api_request(api_key, address)
    if response:
        # 查找指定tokenId的quantity值
        quantity = 0
        for token in response['data']:
            if token['tokenId'] == 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t':
                quantity = token['quantity']
                break

        return quantity
    else:
        return None


# 替换为您的API密钥
api_key = 'a60ba654-6d8d-4886-8f9d-4b437a42bf36'

# 读取包含批量地址的表格，假设为Excel文件
df = pd.read_excel('/Users/apple/Desktop/test.xlsx')

# 设置并发查询的最大线程数
max_workers = 4

# 使用concurrent.futures进行并发查询
with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
    # 提交每个地址的查询任务
    future_to_address = {executor.submit(process_address, api_key, row['Address']): row for index, row in df.iterrows()}

    # 遍历查询结果
    for future in tqdm(concurrent.futures.as_completed(future_to_address), total=len(future_to_address), desc="Processing", unit="row"):
        row = future_to_address[future]
        try:
            # 获取查询结果
            quantity = future.result()

            # 将结果存储在表格中相应的位置
            df.at[row.name, 'Quantity'] = quantity
        except Exception as exc:
            # 处理异常情况
            print(f'Address {row["Address"]} encountered an error: {exc}')

# 将带有quantity值的表格保存为新的Excel文件
df.to_excel('/Users/apple/Desktop/output.xlsx', index=False)

# 打印结果
print("Output Excel file saved successfully!")
