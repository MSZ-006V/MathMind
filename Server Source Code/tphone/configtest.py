import configparser

def read_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    return config

config = read_config('./config.ini')

# 读取 Server 部分的参数
server_ip = config.get('Server', 'ip')
server_port = config.getint('Server', 'port')

print(f"ip is {server_ip}")
print(f"port is {server_port}")
