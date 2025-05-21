import requests

url = "https://api.lamatok.com/v1/hashtag/medias"
params = {
    "id": 805098,
    "access_key": "1J3SttXjxlZIekKgvbX9sgyWtDQm8Zxh",
    "count":1
}
headers = {
    "accept": "application/json",
    # "x-access-key":"1J3SttXjxlZIekKgvbX9sgyWtDQm8Zxh"
}

response = requests.get(url, params=params, headers=headers)

# Print the response JSON
print(response.status_code)
print(response.json())
