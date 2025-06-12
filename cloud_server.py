#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)

# Ubuntu服务器的DDNS域名
UBUNTU_SERVER_HOST = "android.gofoyi.shop"
UBUNTU_PORT = 5000

# Windows主机的MAC地址
WINDOWS_MAC = "74:56:3C:CF:61:00"

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/wake', methods=['POST'])
def wake_windows():
    """唤醒Windows主机"""
    try:
        # 向Ubuntu服务器发送唤醒请求
        url = f"http://{UBUNTU_SERVER_HOST}:{UBUNTU_PORT}/wake"
        payload = {"mac_address": WINDOWS_MAC}
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            return jsonify(result)
        else:
            return jsonify({
                "success": False,
                "message": f"Ubuntu server returned status {response.status_code}"
            }), 500
            
    except requests.exceptions.Timeout:
        return jsonify({
            "success": False,
            "message": "Timeout connecting to Ubuntu server"
        }), 500
    except requests.exceptions.ConnectionError:
        return jsonify({
            "success": False,
            "message": "Cannot connect to Ubuntu server"
        }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

@app.route('/sleep', methods=['POST'])
def sleep_windows():
    """使Windows主机进入睡眠状态"""
    try:
        url = f"http://{UBUNTU_SERVER_HOST}:{UBUNTU_PORT}/sleep"
        
        response = requests.post(url, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            return jsonify(result)
        else:
            return jsonify({
                "success": False,
                "message": f"Ubuntu server returned status {response.status_code}"
            }), 500
            
    except requests.exceptions.Timeout:
        return jsonify({
            "success": False,
            "message": "Timeout connecting to Ubuntu server"
        }), 500
    except requests.exceptions.ConnectionError:
        return jsonify({
            "success": False,
            "message": "Cannot connect to Ubuntu server"
        }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

@app.route('/status', methods=['GET'])
def check_status():
    """检查Ubuntu服务器状态"""
    try:
        url = f"http://{UBUNTU_SERVER_HOST}:{UBUNTU_PORT}/health"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            return jsonify({"ubuntu_server": "online"})
        else:
            return jsonify({"ubuntu_server": "error"})
    except:
        return jsonify({"ubuntu_server": "offline"})

@app.route('/win_status', methods=['GET'])
def win_status():
    """获取Windows主机状态（通过Ubuntu服务器转发）"""
    try:
        url = f"http://{UBUNTU_SERVER_HOST}:{UBUNTU_PORT}/win_status"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"online": False})
    except:
        return jsonify({"online": False})

if __name__ == '__main__':
    # 在IPv4和IPv6上都监听
    app.run(host='0.0.0.0', port=80, debug=False)
