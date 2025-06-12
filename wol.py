#!/usr/bin/env python3
import socket
import struct
import sys
import json
import paramiko
from flask import Flask, request, jsonify

app = Flask(__name__)

# Windows主机SSH连接配置
WINDOWS_HOST_IP = "192.168.124.2"  # 请替换为实际IP
WINDOWS_SSH_USER = "zzz81"  # 请替换为实际用户名
WINDOWS_SSH_PASSWORD = "810520440+"  # 请替换为实际密码
WINDOWS_SSH_PORT = 22

def send_magic_packet(mac_address, broadcast_ip='255.255.255.255', port=9):
    """发送Magic包唤醒设备"""
    # 移除MAC地址中的分隔符
    mac_address = mac_address.replace(':', '').replace('-', '')
    
    # 验证MAC地址格式
    if len(mac_address) != 12:
        return False, "Invalid MAC address format"
    
    try:
        # 创建Magic包
        # Magic包格式: 6个0xFF + 16次重复的MAC地址
        magic_packet = b'\xff' * 6
        mac_bytes = bytes.fromhex(mac_address)
        magic_packet += mac_bytes * 16
        
        # 发送UDP包
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(magic_packet, (broadcast_ip, port))
        sock.close()
        
        return True, "Magic packet sent successfully"
    except Exception as e:
        return False, f"Error sending magic packet: {str(e)}"

def check_windows_status():
    """检查Windows主机是否在线"""
    try:
        import subprocess
        cmd = ['ping', '-c', '1', '-W', '1', WINDOWS_HOST_IP]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def sleep_windows_via_ssh():
    """通过SSH使Windows主机进入睡眠状态(使用优化的PowerShell命令)"""
    try:
        # 创建SSH客户端
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # 连接到Windows主机
        ssh.connect(
            hostname=WINDOWS_HOST_IP,
            port=WINDOWS_SSH_PORT,
            username=WINDOWS_SSH_USER,
            password=WINDOWS_SSH_PASSWORD,
            timeout=10
        )
        
        # 使用您提供的优化命令：直接进入睡眠模式，无需禁用休眠
        # SetSuspendState参数说明:
        # - PowerState.Suspend: 睡眠模式
        # - $false: 不强制关闭应用程序
        # - $false: 允许唤醒事件
        powershell_sleep_cmd = '''powershell.exe -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Application]::SetSuspendState([System.Windows.Forms.PowerState]::Suspend, $false, $false)"'''
        
        # 备用命令列表（按优先级排序）
        backup_commands = [
            # 备用方法1: 使用强制参数
            '''powershell.exe -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Application]::SetSuspendState([System.Windows.Forms.PowerState]::Suspend, $true, $false)"''',
            # 备用方法2: 使用rundll32（如果PowerShell方法失败）
            'rundll32.exe powrprof.dll,SetSuspendState 0,1,0'
        ]
        
        try:
            # 首先尝试主要的睡眠命令
            stdin, stdout, stderr = ssh.exec_command(powershell_sleep_cmd, timeout=5)
            # 不等待命令完成，因为主机会立即进入睡眠
            ssh.close()
            return True, "Sleep command sent successfully."
            
        except Exception as e:
            # 如果主命令失败，尝试备用命令
            for i, backup_cmd in enumerate(backup_commands):
                try:
                    stdin, stdout, stderr = ssh.exec_command(backup_cmd, timeout=3)
                    ssh.close()
                    return True, f"Sleep command sent successfully (backup method {i+1})"
                except:
                    continue
            
            # 所有方法都失败
            ssh.close()
            return False, f"All sleep methods failed. Last error: {str(e)}"
        
    except paramiko.AuthenticationException:
        return False, "SSH authentication failed"
    except paramiko.SSHException as e:
        return False, f"SSH connection error: {str(e)}"
    except Exception as e:
        return False, f"Error sending sleep command: {str(e)}"

@app.route('/wake', methods=['POST'])
def wake_device():
    """接收来自云服务器的唤醒请求"""
    try:
        data = request.get_json()
        mac_address = data.get('mac_address')
        
        if not mac_address:
            return jsonify({"success": False, "message": "MAC address required"}), 400
        
        success, message = send_magic_packet(mac_address)
        
        return jsonify({
            "success": success,
            "message": message
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500

@app.route('/sleep', methods=['POST'])
def sleep_device():
    """使Windows主机进入睡眠状态"""
    try:
        # 首先检查Windows主机是否在线
        if not check_windows_status():
            return jsonify({
                "success": False,
                "message": "Windows主机离线或无法访问"
            })
        
        success, message = sleep_windows_via_ssh()
        
        return jsonify({
            "success": success,
            "message": message
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Server error: {str(e)}"
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({"status": "healthy"})

@app.route('/win_status', methods=['GET'])
def win_status():
    """获取Windows主机状态"""
    try:
        windows_online = check_windows_status()
        
        return jsonify({
            "win_status": "online" if windows_online else "offline"
        })
    except Exception as e:
        return jsonify({
            "win_status": "unknown",
            "error": str(e)
        })

if __name__ == '__main__':
    # 在IPv6地址上监听
    app.run(host='::', port=5000, debug=False)
