import imgbbpy

def imgToUrl(imgPath):
    # img to url
    client = imgbbpy.SyncClient('imgbb-API-KEY')
    image = client.upload(file=imgPath, expiration=120)

    return image.url
