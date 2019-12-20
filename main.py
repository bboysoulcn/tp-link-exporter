import requests
import prometheus_client
from prometheus_client import CollectorRegistry,Gauge,generate_latest
import time
import json
import configparser
import logging

# 读取配置
conf = configparser.ConfigParser()
conf.read("./config.ini",encoding="utf-8")
items = conf.items("conf")
port = items[4][1]
router_ip = items[3][1]
password_hash = items[2][1]
login_name = items[1][1]
sleep_time = items[0][1]

# 日志
logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_route_base_information():
    # 登陆要post的数据
    data = {
        "data": "{\"method\":\"login\",\"params\":{\"username\":\""+ login_name + "\",\"password\":\"" + password_hash + "\"}}"
    }
    # 登陆之后要post的数据
    data2 = {
        "data": "{\"method\":\"get\"}"
    }
    # 登陆前的header
    header = {
        "Host": router_ip,
        "Proxy-Connection": "keep-alive",
        "Content-Length": "35",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Origin": "http://" + router_ip,
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": "http://"+ router_ip + "/webpages/login.html",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en,zh-CN;q=0.9,zh;q=0.8",
        "Cookie": "sysauth=03c8aa5433568e2c3fec4d802fc16a82"
    }
    # 登陆获取cookie和stok
    res = requests.post("http://"+ router_ip +"/cgi-bin/luci/;stok=/login?form=login",headers=header,data=data)
    cookie = res.headers["Set-Cookie"].split(";")[0]
    stok =json.loads(res.text)["result"]["stok"]
    # 登陆之后的header
    header2 = {
        "Host": router_ip,
        "Proxy-Connection": "keep-alive",
        "Content-Length": "35",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Origin": "http://"+router_ip,
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": "http://"+router_ip+ "/webpages/index.html",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en,zh-CN;q=0.9,zh;q=0.8",
        "Cookie": cookie
    }
    # 请求获取cpu内存网络信息
    cpu_usage_res = requests.post("http://"+router_ip+"/cgi-bin/luci/;stok=" + stok + "/admin/sys_status?form=cpu_usage",
                      headers=header2, data=data2)
    mem_usage_res = requests.post("http://"+router_ip+"/cgi-bin/luci/;stok=" + stok + "/admin/sys_status?form=mem_usage",
                      headers=header2, data=data2)
    ifstat_res = requests.post("http://"+router_ip+"/cgi-bin/luci/;stok=" + stok + "/admin/ifstat?form=list",
                                  headers=header2, data=data2)
    # 格式化结果
    ifstat = json.loads(ifstat_res.text)["result"]
    mem_usage = json.loads(mem_usage_res.text)["result"]
    cpu_usage = json.loads(cpu_usage_res.text)["result"]
    result = []
    result.append(ifstat)
    result.append(mem_usage)
    result.append(cpu_usage)
    return result



if __name__ == '__main__':
    prometheus_client.start_http_server(int(port))
    cpu_usage_prom = Gauge("CPU", "TL-ER5120G cpu value", ["cpunum"])
    mem_usage_prom = Gauge("MEM", "TL-ER5120G mem value", ["mem"])
    speed_prom = Gauge("interface", "TL-ER5120G interface value", ["interface"])
    print("Powered by Bboysoul \nTPlink exporter Server is up at port " + port + " !!!!!")
    count = 0
    while True:
        count = count + 1
        content = get_route_base_information()
        # 获取内存
        mem_usage = content[1]["mem"]
        # 获取cpu
        cpu1_usage = content[2]["core1"]
        cpu2_usage = content[2]["core2"]
        cpu3_usage = content[2]["core3"]
        cpu4_usage = content[2]["core4"]
        # 获取网络
        net_usage = content[0]
        for i in range(len(net_usage)):
            interface = net_usage[i]
            send_speed = interface["tx_bps"]
            receive_speed = interface["rx_bps"]
            speed_prom.labels(interface["interface"] + "_send_speed").set(send_speed)
            speed_prom.labels(interface["interface"] + "_receive_speed").set(receive_speed)
        # 内存
        mem_usage_prom.labels("mem").set(mem_usage)
        # cpu
        cpu_usage_prom.labels("cpu1").set(cpu1_usage)
        cpu_usage_prom.labels("cpu2").set(cpu2_usage)
        cpu_usage_prom.labels("cpu3").set(cpu3_usage)
        cpu_usage_prom.labels("cpu4").set(cpu4_usage)
        logger.info("第"+str(count)+"次获取数据成功 cpu1_usage: " + str(cpu1_usage) + " cpu2_usage: " + str(cpu2_usage) + " cpu3_usage: "
                    + str(cpu3_usage) + " cpu4_usage: " + str(cpu4_usage) + "mem_usage: " + str(mem_usage) )
        time.sleep(int(sleep_time))



