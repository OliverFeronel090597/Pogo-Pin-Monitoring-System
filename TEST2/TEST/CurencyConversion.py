import requests

# API endpoint
url = "https://open.er-api.com/v6/latest/EUR"

# Send GET request
response = requests.get(url)

# Print status and raw response
# print("Status Code:", response.status_code)
# print("Raw Response:", response.text)

# Process JSON data
if response.status_code == 200:
    data = response.json()
    if data["result"] == "success":
        rate_php = data["rates"]["PHP"]
        print("\nFinal Results:")
        print("1 EUR = {:.4f} PHP".format(rate_php))

    else:
        print("API Error:", data.get("error-type", "Unknown error"))
else:
    print("HTTP Error:", response.status_code)
