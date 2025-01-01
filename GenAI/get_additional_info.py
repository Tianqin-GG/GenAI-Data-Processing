import os
import re
from openai import OpenAI

client = OpenAI()
api_key = os.getenv("OPENAI_API_KEY")

def get_investor_information(info):
    try:

        completion = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {
                    "role": "system",
                    "content": "You are a financial and startup investment database manager. You should provide structured, accurate, and reliable information based on provided content."
                },
                {
                    "role": "user",
                    "content": 
                    f"From the content '{info}', provide the following details about the investor/company:\
                    1. Company Name\
                    2. AUM\
                    3. Ticket Size (Investment ranges for Seed, Series A, and Later Stages)\
                    4. Average Cheque Size\
                    5. Preferred Round Type\
                    6. Names of General Partners (with LinkedIn URLs if available)\
                    7. Locations (e.g., company addresses).\
                    if the content is missing, put 'no content availale'."

                }
            ]
        )

        # Extract response content
        print("Token Consumed", completion.usage.completion_tokens)
        response_message = completion.choices[0].message.content
        # print("raw results", response_message)
        
        lines = response_message.split("\n")
        
        investor_info = {
        "Company Name": None,
        "AUM": None,
        "Ticket Size": {"Seed": None, "Series A": None, "Later Stage": None},
        "Average Cheque Size": {"Seed": None, "Series A": None, "Later Stage": None},
        "Preferred Round Type": None,
        "General Partners": [],
        "Locations": []
    }

        # Initialize the dictionary to hold the parsed data
        i = 0  # Index for line iteration
        while i < len(lines):
            line = lines[i].strip()  

            if "Company Name" in line:
                investor_info["Company Name"] = line.split(":")[-1].strip() if "no content available" not in line else None

            elif "AUM" in line:
                investor_info["AUM"] = None if "no content available" in line or "Not explicitly stated" in line else line.split(":")[-1].strip()

            elif "Ticket Size" in line:
                ticket_size = {"Seed": None, "Series A": None, "Later Stage": None}
                i += 1
                while i < len(lines) and lines[i].strip().startswith("-"):
                    ticket_line = lines[i].strip()[2:].strip()  # Remove the bullet point and extra spaces
                    if "Seed" in ticket_line:
                        ticket_size["Seed"] = ticket_line.split(":")[1].strip() if ":" in ticket_line else None
                    elif "Series A" in ticket_line:
                        ticket_size["Series A"] = ticket_line.split(":")[1].strip() if ":" in ticket_line else None
                    elif "Later Stages" in ticket_line:
                        ticket_size["Later Stage"] = ticket_line.split(":")[1].strip() if ":" in ticket_line else None
                    i += 1
                investor_info["Ticket Size"] = ticket_size

            elif "Average Cheque Size" in line:
                cheque_size = {"Seed": None, "Series A": None, "Later Stage": None}
                i += 1
                while i < len(lines) and lines[i].strip().startswith("-"):
                    cheque_line = lines[i].strip()[2:].strip()  # Remove the bullet point and extra spaces
                    if "Seed" in cheque_line:
                        cheque_size["Seed"] = cheque_line.split(":")[1].strip() if ":" in cheque_line else None
                    elif "Series A" in cheque_line:
                        cheque_size["Series A"] = cheque_line.split(":")[1].strip() if ":" in cheque_line else None
                    elif "Later Stages" in cheque_line:
                        cheque_size["Later Stage"] = cheque_line.split(":")[1].strip() if ":" in cheque_line else None
                    i += 1
                investor_info["Average Cheque Size"] = cheque_size

            elif "Preferred Round Type" in line:
                investor_info["Preferred Round Type"] = None if "no content available" in line or "i don't know" in line else line.split(":")[-1].strip()
            elif "Names of General Partners" in line:
                partners = []
                i += 1
                while i < len(lines) and lines[i].strip().startswith("-"):
                    partner_info = lines[i].strip()[2:].strip()  # Remove bullet point
                    partner_name = re.sub(r"\(.*\)", "", partner_info).strip()  # Clean the name
                    linkedin_url = re.search(r"\((https?://[^\)]+)\)", partner_info)
                    linkedin_url = linkedin_url.group(1) if linkedin_url else None
                    partners.append({"name": partner_name, "LinkedIn": linkedin_url})
                    i += 1
                investor_info["General Partners"] = partners

            elif "Locations" in line:
                locations = []
                i += 1
                while i < len(lines) and lines[i].strip().startswith("-"):
                    locations.append(lines[i].strip()[2:].strip())  # Remove bullet point and extra spaces
                    i += 1
                investor_info["Locations"] = locations

            i += 1

        return investor_info

    except Exception as e:
        print(f"Error parsing investor information: {e}")
        return None

    except Exception as e:
        print(f"Error parsing investor information: {e}")
        return None


