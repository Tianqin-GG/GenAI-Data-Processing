import requests
from bs4 import BeautifulSoup
import os

# 获取页面HTML内容
def get_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    return response.text

# 从HTML中提取头像URL
def get_profile_picture_url(html):
    soup = BeautifulSoup(html, "html.parser")
    # 根据页面结构提取头像URL，通常 Facebook 头像会在img标签中
    # 下面的代码是一个示例，需要根据实际页面结构调整
    image_tag = soup.find("img", {"class": "profilePic"})
    if image_tag:
        return image_tag["src"]
    return None

# 下载图片
def download_image(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, "wb") as file:
            file.write(response.content)
        print(f"下载成功: {filename}")
    else:
        print(f"下载失败，状态码: {response.status_code}")

# 主程序
def main(facebook_url):
    html = get_html(facebook_url)
    profile_pic_url = get_profile_picture_url(html)
    if profile_pic_url:
        # 头像文件名
        filename = "profile_picture.jpg"
        download_image(profile_pic_url, filename)
    else:
        print("未能找到头像URL")

# 输入 Facebook 页面 URL
if __name__ == "__main__":
    url = input("请输入 Facebook 个人资料页面 URL: ")
    main(url)
