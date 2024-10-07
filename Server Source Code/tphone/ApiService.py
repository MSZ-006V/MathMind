from flask import Flask, request
from PIL import Image
from datetime import datetime
import subprocess
import os
import json
import configparser
import socket

# curl -X POST -F "image=@/path/to/image.jpg" -F "param=value" http://172.30.128.229:8800/pictotext
# curl -X POST -F "image=@H:\\Python_Project\\tphone\\testpic1.png" -F "mode=1200" http://172.30.128.229:8883/pictotext
app = Flask(__name__)

def Read_Config():
    config = configparser.ConfigParser()
    config.read('./config.ini')
    server_ip = config.get('Server', 'ip')

    return server_ip

def available_address():
    ip = Read_Config()

    start_port = 8880
    end_port = 8884

    for port in range(start_port, end_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((ip, port))
                return ip, port
        except OSError:
            print(f"Port {port} is occupied, trying another port...")
            pass
    raise OSError("No available port in the range {}-{}".format(start_port, end_port))

def Pic_recognition_result_handler(output):
    start_index = output.find("Text recognition START") + len("Text recognition START")
    end_index = output.find("Text recognition END")
    result_part = output[start_index:end_index].strip()

    return result_part

def Latex_code_save(latex_code):
    base_path = "/ToRA-master/src/data/testdata/" # You can change this path, just a path which save the Latex code
    data = {
        "problem": latex_code,
        "level": "Level 1",
        "type": "Algebra",
        "solution": "",
        "idx": 0,
    }
    folder_name = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_path = os.path.join(base_path, folder_name)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file_path = os.path.join(folder_path, "test.jsonl")
    with open(file_path, "w") as json_file:
        json.dump(data, json_file)

    return folder_name

def Read_output_jsonl(folder_name):
    preds_list = []
    codes_list = []
    # print("/home/fymr/Python_Project/ToRA-master/src/output/Python_Project/tora-7b/" + folder_name)

    if os.path.exists(
        "/home/fymr/Python_Project/ToRA-master/src/output/Python_Project/tora-7b/" + folder_name):
        with open(
            "/home/fymr/Python_Project/ToRA-master/src/output/Python_Project/tora-7b/"
            + folder_name
            + "/result_output.jsonl",
            "r",
            encoding="utf-8",
        ) as file:
            for line in file:
                json_data = json.loads(line)
                preds_list.append(json_data["pred"])
                codes_list.append(json_data["code"])
    else:
        print("path no exist!")
        return preds_list, codes_list 

    return preds_list, codes_list

@app.route('/pictotext', methods = ['POST'])
def pictotext():
    image_quality_array = [300, 600, 1200] # 2.300 / 3.600 / 4.1200 / 1.自动 / 5.自定义

    file = request.files['image']
    img_quality = int(request.form['mode']) # 若mode为一个很大的值，则为自定义quality设置，若为1~4，则为档位设置
    if 2 <= img_quality <= 4: # 当为2~4档的时候
        img_quality = image_quality_array[img_quality - 2]

    file_name=datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path="/home/fymr/Python_Project/tphone/picture/"+file_name+".jpg"
    file.save(file_path)

    if(img_quality == 1): #当为自动挡的时候
        width, height = Image.open(file_path).size
        img_quality = height
        print("height: ", height)

    process = subprocess.Popen(
        [
            "bash",
            "./service_pic_to_text.sh",
            file_path, str(img_quality)
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    process.wait()
    output, error = process.communicate()
    output = Pic_recognition_result_handler(output)
    print("image recoginition result is: ", output)

    return output

# Calling format
# curl -X POST -F "text=question_code" -F "model=value" http://IP:PROT/codeinfer
# curl -X POST -F "text=1+1*6=?" -F "model=Tora-Code-7B" http://IP:PROT/codeinfer
# curl -X POST -F "text=1+1*6=?" -F "model=ERNIE-Speed" http://IP:PROT/codeinfer
# curl -X POST -F "text=TEXT -F "model=Model_Name" http://IP:PROT/codeinfer
@app.route('/codeinfer', methods = ['POST'])
def codeinfer():

    ModelArray = {
    "ERNIE-Bot 4.0": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro",
    "ERNIE-Bot": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions",
    "ERNIE-Bot-8k": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie_bot_8k",
    "ERNIE-Speed": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie_speed"
    }

    text = request.form['text']
    model = request.form['model']

    if(model == "Tora-Code-7B"):
        folder_name = "test_pic/" + Latex_code_save(text)
        process = subprocess.Popen(
                    ["bash", "./service_tora_infer.sh", folder_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
        process.wait()
        output, error = process.communicate()
        pred_list, code_list = Read_output_jsonl(folder_name)
        if len(pred_list) == 0 and len(code_list) == 0:
                    error += "No such file or directory! "
        
        return str("Result : " + code_list[0])

    if(model[:5] == "ERNIE"):
        process = subprocess.Popen(
                    ["bash", "./service_ernie.sh", text, model],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
        process.wait()
        output, error = process.communicate()
        print("Output is ",output)
        print("Error is ",error)

        return output

    if(model == "Qwen-Max"):
        process = subprocess.Popen(
                    ["bash", "./service_TongYi_Max.sh", text],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
        process.wait()
        output, error = process.communicate()
        print("Output is ",output)
        print("Error is ",error)

        return output
        
    return ""

if __name__ == '__main__':
    ip, port = available_address()
    app.run(host=ip, port=port)
