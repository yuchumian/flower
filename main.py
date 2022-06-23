#coding=utf-8
import time
import threading
import RPi.GPIO as GPIO
from flask import Flask, jsonify
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from datetime import datetime
from smbus2 import SMBus
# PCF8591
address = 0x48
A0 = 0x40
A1 = 0x41
A2 = 0xA2
A3 = 0xA3
# 浇水阈值百分比
threshold = 38
# 传感器全干值
max_value = 255
# 传感器在水中值
min_value = 45
# 浇水间隔
watering_interval = 15
# app
app = Flask(__name__)
app.config.from_object(__name__)
app.config["JSON_AS_ASCII"] = False
# global
GPIO.setmode(GPIO.BCM)
# DO-土壤传感器GPIO
channel1 = 24  
# 继电器GPIO
channel2 = 18  
GPIO.setup(channel1, GPIO.IN)
# 浇水信息
wateringMap = {"waterTime": 1.5, "loopTime": 2,
               "is_watering": False, "run": False, "status": "干燥", "lastTime": "", "prvWateringTime": 0, "watering": 0,"auto":False,"humidity":0}
# 返回结构体
data = {'status': 'true', 'msg': ''}
# 定义一个线程池
pool = ThreadPoolExecutor(max_workers=1)
'''
读取数字模拟量
'''
def read_bus(chn):
    with SMBus(1) as bus:
        bus.write_byte(address,chn)	
        return bus.read_byte(address,0)
'''
自动浇水模式
'''
def auto():
    global wateringMap
    while wateringMap["run"]:
        wateringMap["auto"]=True
        humPercent = read_hum(A0)
        if humPercent < threshold:
            watering()
        time.sleep(wateringMap["loopTime"])
    wateringMap["auto"] = False
'''
读取湿度并转换百分比
'''
def read_hum(chn):
    b = read_bus(chn)
    humPercent = ((b-max_value)/(min_value-max_value))*100
    deal_status(humPercent)
    if humPercent > 100:
        humPercent = 100
    if humPercent < 0:
        humPercent = 0
    wateringMap['humidity'] = humPercent
    return humPercent 
'''
打开继电器浇水
'''
def watering():
    global wateringMap
    now = datetime.now()
    timelong = time.mktime(now.timetuple())
    if timelong - wateringMap["watering"] < watering_interval:
        return
    on_watering(True)
    GPIO.setup(channel2, GPIO.OUT)  # 继电器
    GPIO.output(channel2, GPIO.HIGH)
    time.sleep(wateringMap["waterTime"])
    wateringMap["prvWateringTime"] = wateringMap["waterTime"]
    GPIO.output(channel2, GPIO.LOW)
    GPIO.cleanup(channel2)
    wateringMap["lastTime"] = now.strftime('%Y-%m-%d %H:%M:%S')
    wateringMap["watering"] = timelong
    on_watering(False)

'''
是否正在浇水
'''
def on_watering(b):
    global wateringMap
    wateringMap["is_watering"] = b

'''
修改自动和停止标识
'''
def run_auto(boo):
    global wateringMap
    wateringMap["run"] = boo
    wateringMap["auto"] = boo
'''
处理湿度状态
'''
def deal_status(humPercent):
    global wateringMap
    if humPercent >= threshold:
        wateringMap["status"] = "潮湿"
    else:
        wateringMap["status"] = "干燥"

@app.route('/api')
def index():
    return ''

'''
关闭自动浇水
'''
@app.route('/api/auto/close')
def close():
    run_auto(False)
    data['msg'] = '关闭成功'
    return jsonify(data)

'''
改变浇水时长
'''
@app.route('/api/auto/time/<float:sec>', methods=['GET'])
def waterTime(sec):
    global wateringMap
    wateringMap["waterTime"] = sec
    data['msg'] = '成功'
    if wateringMap["is_watering"]:
        return jsonify(data)
    if not wateringMap["run"]:
        watering()
    return jsonify(data)

'''
模式切换
'''
@app.route('/api/auto/change/<int:type>', methods=['GET'])
def change_mode(type):
    if type == 1:
        run_auto(False)
    elif not wateringMap["run"] and not wateringMap["auto"]:
        run_auto(True)
        f = pool.submit(auto)
    data['msg'] = '成功'
    return jsonify(data)

'''
浇水信息
'''
@app.route('/api/auto/init', methods=['GET'])
def config():
    humPercent = read_hum(A0)
    deal_status(humPercent)
    wateringMap['humidity'] = humPercent
    wateringMap['prvWateringTime'] = wateringMap["prvWateringTime"] if wateringMap["prvWateringTime"] > 0 else wateringMap["waterTime"]
    return jsonify(wateringMap)


if __name__ == "__main__":
    # flask 官方启动方式参见：http://flask.pocoo.org/docs/0.12/quickstart/#a-minimal-application
    app.run(host='0.0.0.0', debug=False)
