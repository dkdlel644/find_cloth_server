from flask import Flask, render_template, request
# import pymysql
from PIL import Image, ImageFile
import io
from similarity.naverAPI import searchNaverShop
from similarity.makeUrl import imgToUrl
from similarity.Similarity import compare
import urllib.request
import torch
import json
import os
from glob import glob
ImageFile.LOAD_TRUNCATED_IMAGES = True
import time

app = Flask(__name__)

@app.route("/")
def main():
    return ""

@app.route("/detect" , methods=['GET','POST'])
def test():
    # 문자열로 받은 byteArray를 bytes로 변환
    binImage = request.form["binImage"]
    strImage= binImage[1:-2].split(",")
    bytelist = []
    for ImageB in strImage:
        bytelist.append(int(ImageB))
    data = bytes(bytelist)

    # Target이미지 객체 검출
    OrigintargetPath = "images\\target\\target.jpeg"
    bytesToImagePath(data, OrigintargetPath)
    global ditectTarget
    ditectTarget=exportModel(OrigintargetPath, "images\\target")

    result = ""
    try:
        for key in ditectTarget.keys():
            result = result + "&" +key
        result = result[1:]
    except:
        print("No detected")
    print(result)

    return result

@app.route("/search" , methods=['GET','POST'])
def search():
    start = time.time()
    selectedClass = request.form["selectedClass"]
    productDict = searchNaver(selectedClass, "images")

    
    inputOriginPaths = productDict["image"]

    inputImgPaths = []
    i = 0
    for inputOriginPath in inputOriginPaths:
        try:
            detectedPath = exportModel(inputOriginPath, "images")[selectedClass]
            inputImgPaths.append(detectedPath)
            i = i + 1
        except:
            del productDict["title"][i]
            del productDict["link"][i]
            del productDict["lprice"][i]

    global ditectTarget
    compareDict = compare(ditectTarget[selectedClass], inputImgPaths)

    for i, row in enumerate(compareDict.items()):
        compareDict[row[0]] = row[1] + ">" + productDict["title"][i] + ">" + productDict["link"][i]+ ">" + productDict["lprice"][i]
    sortedDict = dict(sorted(compareDict.items(), reverse=True))

    result=""
    for i, row in enumerate(sortedDict.items()):
        print(i)
        text = row[1].split(">")
        url = imgToUrl(text[0])
        result = result + "&" + text[1] + ">" + text[2] + ">" + str(row[0]) + ">" + url + ">" + text[3]
        i = i + 1
        if (i == 10): break
    result = result[1:]
    print(result)

    [os.remove(f) for f in glob(r"images\*.jpeg")]
    print(selectedClass)
    print("time :", time.time() - start)
    return result

if __name__ == "__main__":
    ditectTarget = dict()

    # 학습모델 가져오기
    model_path = torch.hub.load('ultralytics/yolov5', 'custom', path='weights/best.pt')
 
    # database에 접근 (시간 부족으로 미구현)
    # db= pymysql.connect(host='localhost',
    #                     port=3306,
    #                     user='root',
    #                     passwd='123456789',
    #                     db='userinfo',
    #                     charset='utf8')

    # database를 사용하기 위한 cursor를 세팅합니다.
    # cursor= db.cursor()

    # bytes를 path경로에 파일로 저장
    def bytesToImagePath(byte, path):
        with open(path, "wb") as f:
            f.write(byte)
        image1 = Image.open(path)
        image1 = image1.convert('RGB')
        image1_re = image1.resize((800,800))
        image1_re.save(path)

    # NaverAPI를 이용해서 title로 검색 후 savePath에 차례대로 저장 후 각 파일별 경로 LIST 반환
    def searchNaver(title, savePath):
        productDict = searchNaverShop(title)
        input_image_urls = productDict["image"]
        input_img_paths = []
        for i, url in enumerate(input_image_urls):
            if len(url) > 0:
                path = savePath + "\\input_img%d.jpeg" % (i+1)
                urllib.request.urlretrieve(url, path)
                image1 = Image.open(path)
                image1 = image1.convert('RGB')
                image1_re = image1.resize((800,800))
                image1_re.save(path)
                input_img_paths.append(path)
        productDict["image"] = input_img_paths
        return productDict

    # 의상 카테고리 검출
    def exportModel(img_input_path, img_output_path):
        # initialize
        model = model_path
        model.eval()
        
        if(img_input_path.split(".").pop(1) == "jpeg"):
            with open(img_input_path,'rb') as f:
                data = f.read()
            img_bytes = io.BytesIO(data)
            target_img = Image.open(img_bytes)
            results = model(target_img,size=640)
            data = results.pandas().xyxy[0].to_json(orient="index") 
            data_json = json.loads(data)
            dict_result = dict()
            

            # save detected result
            for k in data_json:
                label = data_json[k]['name']
                target_area = (data_json[k]['xmin'], data_json[k]['ymin'], data_json[k]['xmax'], data_json[k]['ymax']) # find coordinate for crop target image
                save_image_path = img_output_path + "\\" + img_input_path.split("\\").pop(-1).split(".").pop(0) + label + ".jpeg"
                target_img.crop(target_area).save(save_image_path)
                dict_result[label]=save_image_path

        return dict_result  # output ex) {'Jeans': 'img_path', 'Coat': 'img_path'}

    app.run(host='0.0.0.0', debug=True)
    

