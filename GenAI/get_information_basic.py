import os
import pandas as pd
from openai import OpenAI
import asyncio

client = OpenAI()
api_key = os.getenv("OPENAI_API_KEY")

cate = pd.read_csv('./data/part.csv')
# print(category.head())
category = []
for i in cate['name']:
    if i not in category:
        category.append(i)
        
# print(category)

def  get_information_basic(info,category):

    try:
        # Generate completion
        completion =   client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a healthcare startup database manager. You should provide accurate and reliable information from the given content."},
                {
                    "role": "user",
                    "content": f"From the content {info}, provide the following details about the company: \
                                1. Company Name, 2. Industry, 3. Specialties, 4. Founded Year (else return none) , 5.Description\
                                The description should specify the company overview, its products, and services."
                                     
                }
            ]
        )

        # Extract response content
        response_message = completion.choices[0].message.content
        print("Token Consumed", completion.usage.completion_tokens)
        print(response_message)
        
        # Parse the content into structured data (optional step, based on the format of the API response)
        lines = response_message.split("\n")
        company_info = {
            "Company Name": None,
            "Industry": None,
            "Specialties": [],
            "Description": None,
            "Founded": None
        }

        # Parsing logic (basic example for structured responses)
        for i, line in enumerate(lines):
            line = line.strip()
            line = line.replace('*', '').strip()

            # Extract Company Name
            if "Company Name:" in line:
                company_info["Company Name"] = line.split(":")[1].strip()

            # Extract Industry
            elif "Industry:" in line:
                company_info["Industry"] = line.split(":")[1].strip()
            
            elif "Founded Year:" in line:
                company_info["Founded"] = line.split(":")[1].strip()


            # Extract Specialties
            elif "Specialties:" in line:
                specialties = []
                i += 1
                while i < len(lines) and lines[i].strip().startswith("- "):  # Handle bullet points
                    specialties.append(lines[i].strip()[2:].strip())  # Remove bullet point and extra spaces
                    i += 1
                if not specialties:
                    # If specialties are comma-separated instead of a bullet list
                    specialties = [s.strip() for s in line.split(":")[-1].split(",")]
                company_info["Specialties"] = specialties
            # Extract Description
            elif "Description:" in line:
                print(line)
                # description_start = i + 1
                company_info["Description"] = line.split(":")[1].strip()

        print(company_info)
            

        return company_info

    except Exception as e:
        print(f"Error fetching company information: {e}")
        return None
    
# result = get_information_basic("https://marshallhealthnetwork.org/",category)
# print(result)