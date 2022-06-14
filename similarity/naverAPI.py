import requests
import urllib
import random
import json

def searchNaverShop(query):
    query = urllib.parse.quote(query)

    display = "100"
    start = str(random.randrange(1, 901))

    url = "https://openapi.naver.com/v1/search/shop?query=" + query + "&display=" + display + "&start="+ start

    request = urllib.request.Request(url)
    request.add_header('X-Naver-Client-Id', "Your_ID")
    request.add_header('X-Naver-Client-Secret', "Your_Secret")

    response = urllib.request.urlopen(request)
    itemList = json.loads(response.read().decode('utf-8'))["items"]

    productDict = {"title":[], "link":[], "image":[], "lprice":[]}
    for item in itemList:
        title = item["title"].replace('<b>', '')
        title = title.replace('</b>', '')
        productDict["title"].append(title)
        productDict["link"].append(item["link"])
        productDict["image"].append(item["image"])
        productDict["lprice"].append(item["lprice"])
    return productDict
