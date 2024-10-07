import socket
import json
import os
import subprocess
import threading
import sys
import base64
from datetime import datetime


def send_message(message):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(("172.30.128.229", 8886))  # 替换为你的服务器 IP 地址和端口

        client.send(message.encode("utf-8"))  # 发送消息，假设消息是 utf-8 编码
        response = client.recv(1024).decode("utf-8")  # 接收服务器的响应
        print(f"Server response: {response}")
    except Exception as e:
        print(e)
        sys.exit(0)
    finally:
        client.close()


if __name__ == "__main__":
    # 可发送命令: connect, activate service, stop
    command_list = ["connect", "activate service", "pic_to_text", "tora_infer", "stop"]

    request_id = 0
    request_type = command_list[4]
    latex_code_identification = ""
    latex_code_infer = "Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?"
    latex_code_infer1 = "1+3*6=?"
    parameter = ["Tora-Code-7B", "Latex", "Medium"]
    result = ""

    data = {
        "request_id": 0,
        "request_type": request_type,
        "latex_code_identification": latex_code_identification,
        "latex_code_infer": latex_code_infer,
        "parameter": parameter,
        "result": result,
    }
    message_json = json.dumps(data, indent=2)

    message_json = (message_json + "Separator_IMAGE_BASE64_CODE_Separator" + base64_encoded)

    send_message(message_json)
