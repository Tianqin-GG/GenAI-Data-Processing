import openai
import os

# 设置 OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

def filter_linkedin_via_api_bulk(linkedin_urls, target_name, target_company_description):
    """
    Use OpenAI API to filter a list of LinkedIn URLs based on the target name and company description.

    Args:
        linkedin_urls (list): List of LinkedIn profile URLs.
        target_name (str): The name of the person to filter.
        target_company_description (str): Keywords or phrases describing the company.

    Returns:
        list: Filtered LinkedIn URLs matching the criteria.
    """
    # 构造 prompt，将所有 URL 一次性传入
    prompt = (
        f"Here is a list of LinkedIn URLs:\n{', '.join(linkedin_urls)}\n\n"
        f"Check each profile against the following criteria:\n"
        f"1. The person's name matches '{target_name}'.\n"
        f"2. The company description matches '{target_company_description}'.\n\n"
        f"For each URL, return 'MATCH' if both criteria are satisfied; otherwise, return 'NO MATCH'. "
        f"Provide the result in JSON format with keys as URLs and values as 'MATCH' or 'NO MATCH'."
    )
    
    try:
        # 调用 OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert at analyzing LinkedIn profiles."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # 获取 API 的返回内容
        result = response['choices'][0]['message']['content'].strip()
        print("Raw API Response:", result)  # 可用于调试
        
        # 解析 JSON 格式的结果
        import json
        matched_urls = []
        try:
            results_json = json.loads(result)
            matched_urls = [url for url, status in results_json.items() if status == "MATCH"]
        except json.JSONDecodeError:
            print("Failed to parse API response as JSON. Please check the raw result.")
        
        return matched_urls

    except Exception as e:
        print(f"Error during API call: {e}")
        return []

# 示例调用
linkedin_urls = [
    "https://www.linkedin.com/in/example1",
    "https://www.linkedin.com/in/example2",
    "https://www.linkedin.com/in/example3"
]
target_name = "John Doe"
target_company_description = "Venture capital firm focusing on early-stage technology startups"

# 批量过滤 LinkedIn URLs
filtered_urls = filter_linkedin_via_api_bulk(linkedin_urls, target_name, target_company_description)

print("Filtered LinkedIn URLs:")
for url in filtered_urls:
    print(url)
