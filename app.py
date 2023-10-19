from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
import paramiko
import uvicorn
import threading
import time
import logging
from fastapi import FastAPI

logging.basicConfig(filename="app.log",   # 日志文件名
                    level=logging.ERROR,   # 记录ERROR级别以上的日志
                    format="%(asctime)s - %(levelname)s - %(message)s")  # 日志格式


app = FastAPI()

logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("starlette").setLevel(logging.WARNING)

# 添加CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://192.168.0.35:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

server_ips = ['192.168.0.240', '192.168.0.242',
              '192.168.0.243', '192.168.0.248', '192.168.0.35']
ssh_port = 18518
username = 'chenqiyuan'  # 监控服务器的用户名
password = 'CQYcqy20011012'  # 监控服务器的密码

ssh_clients = {server: None for server in server_ips}


def connect_ssh(server):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server, port=ssh_port, username=username, password=password)
    print(f"connect to {server} success!")
    return ssh



def close_ssh_clients():
    for ssh in ssh_clients.values():
        if ssh:
            ssh.close()

app.add_event_handler("shutdown", close_ssh_clients)



results = {}


def query_gpu_info():
    while True:
        for server in server_ips:
            try:
                results[server] = get_server_gpu_info(server)
            except Exception as e:
                logging.error(
                    f"Error fetching GPU info for {server}: {str(e)}")
        time.sleep(1)


def get_server_gpu_info(server):
    
    try:
        ssh = connect_ssh(server)
    except:
        logging.error(f"Error connecting to {server}")
    try:
        _, stdout, _ = ssh.exec_command(
            "nvidia-smi --query-gpu=gpu_name,memory.total,memory.used --format=csv,noheader,nounits")
        gpu_info = stdout.read().decode().strip().split("\n")
        _, stdout, _ = ssh.exec_command("nvidia-smi pmon -c 1")
        process_info = stdout.read().decode().strip().split("\n")[2:]

        _, stdout, _ = ssh.exec_command(
            "nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits")
        utilization_info = stdout.read().decode().strip().split("\n")

        pid_user_dict = {}
        for line in process_info:
            parts = line.split()
            if len(parts) >= 4:
                gpu_id, pid = parts[0], parts[1]
                if pid != '-':
                    _, user_out, _ = ssh.exec_command(f"ps -o user= -p {pid}")
                    user = user_out.read().decode().strip()
                    _, memory_out, _ = ssh.exec_command(
                        f"nvidia-smi -i {gpu_id} --query-compute-apps=pid,used_memory --format=csv | grep {pid}")
                    memory_info = memory_out.read().decode().strip().split("\n")[
                        0].split(", ")[1].split(" ")[0]
                    if gpu_id not in pid_user_dict:
                        pid_user_dict[gpu_id] = [{user: memory_info}]
                    else:
                        pid_user_dict[gpu_id].append({user: memory_info})
        result = []

        for idx, info in enumerate(gpu_info):
            user_memory = {}
            name, mem_total, mem_used = info.split(", ")
            # rates = str(int((int(mem_used) / int(mem_total)) * 100))+"%"
            rates = utilization_info[idx]+"%"
            user_data = pid_user_dict.get(str(idx))
            if user_data:
                for u in user_data:
                    current_user = next(iter(u.keys()))
                    current_memory = int(next(iter(u.values())))
                    user_memory[current_user] = user_memory.get(
                        current_user, 0) + current_memory

            user = list(user_memory.keys())
            result.append({
                "name": name,
                "memory_total": mem_total,
                "memory_used": mem_used,
                "Usage_rate": rates,
                "user": user,
                "user_display": ", ".join(user) if len(user) != 0 else "None",
                "user_memory": user_memory if len(user) != 0 else None
            })
            
    finally:
        ssh.close()
    return result


user_sorted_data = []


def sort_by_gpu_usage(data):
    user_gpu_count = {}
    for server, gpus in data.items():
        for gpu in gpus:
            user = gpu["user"]
            if len(user) != 0:
                for u in user:
                    user_gpu_count[u] = user_gpu_count.get(u, 0) + 1

    # 根据使用的显卡数量对用户进行排序
    sorted_users = sorted(user_gpu_count.keys(),
                          key=lambda u: user_gpu_count[u], reverse=True)

    sorted_data = []
    for user in sorted_users:
        user_data = {
            "user": user,
            "gpu_count": user_gpu_count[user],
            "details": []
        }
        for server, gpus in data.items():
            for gpu in gpus:
                for u in gpu["user"]:
                    if u == user:
                        user_data["details"].append({
                            "server": server,
                            "gpu_name": gpu["name"],
                            "memory_total": gpu["memory_total"],
                            "memory_used": gpu["user_memory"][u],
                            "usage_rate": gpu["Usage_rate"]
                        })
        sorted_data.append(user_data)

    return sorted_data


def query_user_info():
    global user_sorted_data
    while True:
        user_sorted_data = sort_by_gpu_usage(results)
        time.sleep(0.1)


@app.get("/sort-by-user")
def get_all_user_info():
    return sort_by_gpu_usage(results)


@app.get("/gpu-monitor")
def get_all_gpu_info():
    return results


def is_ssh_connected(ssh):
    try:
        ssh.get_transport().send_ignore()
        return True
    except:
        return False





threading.Thread(target=query_gpu_info, daemon=True).start()

uvicorn.run(app, host="192.168.0.35", port=8000)
