import requests
from bs4 import BeautifulSoup

def get_company_website(company_name):
    # 定义 Google 搜索的 URL，附加查询参数
    search_url = "https://www.google.com/search"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    }
    params = {
        "q": company_name + " official website",  # 搜索关键词
        "hl": "en",  # 搜索语言（英文提高官网匹配率）
    }

    try:
        # 发起 GET 请求
        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()

        # 解析 HTML 内容
        soup = BeautifulSoup(response.text, "html.parser")

        # 找到搜索结果中第一个链接
        search_results = soup.find_all("div", class_="tF2Cxc")  # Google 搜索结果的 CSS 类
        if search_results:
            first_result = search_results[0].find("a")  # 找到第一个搜索结果的链接
            if first_result:
                return first_result["href"]  # 提取链接

        return "No website found"
    except Exception as e:
        return f"Error: {e}"

# 示例用法
if __name__ == "__main__":
    company_name = "blackbird vc"
    website = get_company_website(company_name)
    print(f"The official website for {company_name} is: {website}")
