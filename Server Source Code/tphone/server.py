import socket
import subprocess
import threading
import sys
import base64
import json
import os
import re
import configparser
from datetime import datetime
from PIL import Image

exit_signal = threading.Event()
TORA_SRC_PATH = ""
TPHONE_PATH = ""

def Read_Config():
    global TORA_SRC_PATH, TPHONE_PATH 
    config = configparser.ConfigParser()
    config.read('./config.ini')
    server_ip = config.get('Server', 'ip')
    TORA_SRC_PATH = config.get('Paths', 'tora_src_path')
    TPHONE_PATH = config.get("Paths", 'Tphone_path')

    return server_ip

def Latex_code_save(latex_code):
    base_path = TORA_SRC_PATH + "data/testdata/"
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

    if os.path.exists(
        TORA_SRC_PATH + "output/tora-7b/" + folder_name):
        with open(
            TORA_SRC_PATH + "output/tora-7b/"
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


def Pic_recognition_result_handler(output):
    start_index = output.find("Text recognition START") + len("Text recognition START")
    end_index = output.find("Text recognition END")
    result_part = output[start_index:end_index].strip()

    return result_part


def Handle_Message(request_str):
    separator_index = request_str.find("Separator_IMAGE_BASE64_CODE_Separator")
    if separator_index != -1:
        # 获取 json_data 和 image_base64Code
        json_data = request_str[:separator_index]
        image_base64Code = request_str[separator_index + len("Separator_IMAGE_BASE64_CODE_Separator"):]

        return json_data, image_base64Code
    else:
        return None


def Message_Generate(request_id, request_type, latex_code_identification, latex_code_infer, result):
    command_list = ["connect", "activate service", "pic_to_text", "tora_infer", "stop"]
    data = {
        "request_id": 0,
        "request_type": command_list[request_type],
        "latex_code_identification": latex_code_identification,
        "latex_code_infer": latex_code_infer,
        "parameter": [],
        "result": result,
    }
    message_json = json.dumps(data, indent=2)
    return message_json

def handle_client(client_socket):
    request_str=""
    process_request_str=None
    json_data=None
    image_code=None
    try:
        while True:
            try:
                data=client_socket.recv(1024)
                request_str+=str(data,'utf-8').strip()
                if data == "" :
                    break
            except socket.timeout:
                break

        # request_str=client_socket.recv(4096).decode("utf-8")
        # print(f"Received message: {request_str}")
        process_request_str=Handle_Message(request_str)

        if process_request_str is not None:
            json_data, image_code=process_request_str
            request_str=""
            process_request_str=""
        else:
            print(f"Received message: Something go wrong!,return is None")

        request = json.loads(json_data)
        print(f"Received Json message: {json_data}")
        print(f"Received Image Code: {image_code}")
    except Exception as e:
        print("Error is ",e)
        request=None

    # 根据接收到的消息，调用服务器上的程序，这里使用 subprocess 模块
    if request["request_type"] == "connect":
        try:
            result = Message_Generate(0,0,"","","Server Connection Successful")
            client_socket.send(result.encode("utf-8"))  # 将程序的输出作为响应发送回客户端
        except Exception as e:
            client_socket.send(str(e).encode("utf-8"))  # 发送异常信息作为响应
    elif request["request_type"] == "activate service":
        try:
            process = subprocess.Popen(
                ["bash", "./service_script.sh"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            output, error = process.communicate()
            result = "Output: " + str(output) + "Error :" + str(error)
            client_socket.send(result.encode("utf-8"))
        except Exception as e:
            client_socket.send(str(e).encode("utf-8"))
    elif request["request_type"] == "pic_to_text":
        try:
            print("ready to process image")
            image_data=base64.b64decode(image_code)
            file_name=datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path=TPHONE_PATH + "picture/"+file_name+".jpg"
            print("image path is ", file_path)

            with open(file_path, "wb") as image_file:
                image_file.write(image_data)

            image_quality = str(request["parameter"][2]) # 当request["parameter"][2]不为0,2,3,4等数字的时候，意思是自定义分辨率，直接使用输入的数字作为分辨率
            if(request["parameter"][2] == "0"):
                width, height = Image.open(file_path).size
                image_quality = width
            if(request["parameter"][2] == "2"):
                image_quality = 300
            if(request["parameter"][2] == "3"):
                image_quality = 600
            if(request["parameter"][2] == "4"):
                image_quality = 1200

            process = subprocess.Popen(
                [
                    "bash",
                    "./service_pic_to_text.sh",
                    file_path, str(image_quality),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            process.wait()
            output, error = process.communicate()

            output = Pic_recognition_result_handler(output=output)
            result = Message_Generate(0,2,"","",output)
            client_socket.send(result.encode("utf-8"))

        except Exception as e:
            client_socket.send(str(e).encode("utf-8"))
    elif request["request_type"] == "tora_infer":
        try:
            if(request["parameter"][0] == "Tora-Code-7B"):
                folder_name = "testdata/" + Latex_code_save(request["latex_code_infer"])
                process = subprocess.Popen(
                    ["bash", "./service_tora_infer.sh", folder_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                process.wait()
                output, error = process.communicate()
                print("Output is ",output)
                print("Error is ",error)
                pred_list, code_list = Read_output_jsonl(folder_name)
                print("Pred is ",pred_list)
                print("Code is ",code_list)
                if len(pred_list) == 0 and len(code_list) == 0:
                    error += "No such file or directory! "
                # result = "Output: " + str(pred_list) + "Error :" + str(error)

                result = Message_Generate(0,3,"","",str(pred_list[0])+"////"+str(code_list[0]))

                client_socket.send(result.encode("utf-8"))
            if(request["parameter"][0][:5] == "ERNIE"):
                question = request["latex_code_infer"]
                process = subprocess.Popen(
                    ["bash", "./service_ernie.sh", question, request["parameter"][0]],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                process.wait()
                output, error = process.communicate()
                print("Output is ",output)
                print("Error is ",error)

                result = Message_Generate(0,3,"","",output)

                client_socket.send(result.encode("utf-8"))
            if(request["parameter"][0] == "通义千问-Max"):
                question = request["latex_code_infer"]
                process = subprocess.Popen(
                    ["bash", "./service_TongYi_Max.sh", question],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                process.wait()
                output, error = process.communicate()
                print("Output is ",output)
                print("Error is ",error)

                result = Message_Generate(0,3,"","",output)

                client_socket.send(result.encode("utf-8"))
        except Exception as e:
            client_socket.send(str(e).encode("utf-8"))
    elif request["request_type"] == "stop":
        try:
            output = "Stop command received. Stopping server..."
            client_socket.send(output.encode("utf-8"))
            exit_signal.set()
        except Exception as e:
            client_socket.send(str(e).encode("utf-8"))

    client_socket.close()


def run_server():
    ip = Read_Config()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    start_port = 8885
    end_port = 8890
    for port in range(start_port, end_port + 1):
        try:
            server.bind((ip, port))
            break
        except OSError:
            if port == end_port:
                raise RuntimeError(f"Failed to bind to any port from {start_port} to {end_port}")
            print(f"Port {port} is occupied, trying another port...")

    #server.bind(("IP", PORT))  

    server.listen(5)

    print(f"Server listening on port {port}...")

    while not exit_signal.is_set():
        try:
            client_socket, addr = server.accept()
            client_socket.settimeout(5)
            print(f"Accepted connection from {addr[0]}:{addr[1]}")

            client_handler = threading.Thread(
                target=handle_client, args=(client_socket,)
            )
            client_handler.start()
            client_handler.join()

            if exit_signal.is_set():
                break
        except socket.error as e:
            client_socket.send(str(e).encode("utf-8"))
            pass

    print("Server is stopping...")
    server.close()


if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    server_thread.join()
