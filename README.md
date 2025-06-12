一个基于Web的远程Windows主机电源管理解决方案，支持网络唤醒(WOL)和远程睡眠功能。
A web-based remote Windows host power management solution that supports Wake-on-LAN (WOL) and remote sleep functions.

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ 功能特性

### 🚀 远程唤醒 (Wake-on-LAN)
- 通过Magic Packet技术远程唤醒Windows主机
- 支持IPv4/IPv6双栈网络环境
- 实时监控主机启动状态

### 😴 远程睡眠
- 使用优化的PowerShell方法进入真正的睡眠模式（非休眠）
- 无需修改系统休眠设置
- 通过SSH安全连接执行睡眠命令

### 🌐 Web界面
- 简洁美观的响应式设计
- 实时状态监控
- 移动设备友好

### 🔧 架构特点
- 三层架构：云服务器 ↔ Ubuntu服务器 ↔ Windows主机
- 多重检测机制：SSH、TCP端口、ICMP ping
- 容错处理和自动重试

## 🏗️ 系统架构

```
┌─────────────────┐    IPv6     ┌─────────────────┐    内网     ┌─────────────────┐
│   云服务器       │ ◄────────►  │  Ubuntu服务器     │ ◄────────► │   Windows主机    │
│  (Web界面）      │             │   (中继服务)      │            │   (目标设备)      │
│  Flask + HTML   │             │  Flask + WOL    │             │ SSH + PowerShell│
└─────────────────┘             └─────────────────┘             └─────────────────┘
```

## 📋 系统要求

### 云服务器
- Python 3.7+
- Flask 2.0+
- 公网IPv6地址
- 端口80开放

### Ubuntu服务器  
- Ubuntu 18.04+
- Python 3.7+
- IPv6网络连接
- 与Windows主机在同一内网

### Windows主机
- Windows 10/11
- 启用网络唤醒功能
- OpenSSH Server已安装
- 网卡支持WOL

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/Gofoyi/Wol.git
cd Wol
```

### 2. 配置Windows主机

#### 安装OpenSSH Server
```powershell
# 以管理员身份运行PowerShell
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'

# 配置防火墙
New-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
```

#### 获取MAC地址
```powershell
Get-NetAdapter | Where-Object {$_.Status -eq "Up"} | Select-Object Name, InterfaceDescription, MacAddress
```

### 3. 配置Ubuntu服务器

#### 安装依赖
```bash
sudo apt update
sudo apt install -y python3 python3-pip iputils-ping
pip3 install flask requests paramiko
```

#### 配置服务
```bash
# 复制脚本
sudo cp wol_script.py /home/ubuntu/
sudo chown ubuntu:ubuntu /home/ubuntu/wol_script.py

# 编辑配置
nano /home/ubuntu/wol_script.py
# 修改以下变量：
# WINDOWS_HOST_IP = "192.168.1.100"  # Windows主机内网IP
# WINDOWS_SSH_USER = "your_username"  # SSH用户名
# WINDOWS_SSH_PASSWORD = "your_password"  # SSH密码

# 创建系统服务
sudo bash deploy_updated.sh
```

### 4. 配置云服务器

#### 安装依赖
```bash
pip3 install flask requests
```

#### 配置参数
```bash
nano cloud_server.py
# 修改以下变量：
# UBUNTU_SERVER_IPv6 = "2001:db8::1"  # Ubuntu服务器IPv6地址
# WINDOWS_MAC = "AA:BB:CC:DD:EE:FF"  # Windows主机MAC地址
```

#### 启动服务
```bash
python3 cloud_server.py
```

## ⚙️ 配置详解

### Windows主机配置

1. **网络适配器设置**
   ```
   设备管理器 → 网络适配器 → 属性 → 电源管理
   ✅ 允许此设备唤醒计算机
   ✅ 只允许幻数据包唤醒计算机
   ```

2. **BIOS设置**
   ```
   启用 Wake-on-LAN
   启用 PCI设备唤醒
   ```

3. **电源设置**
   ```powershell
   # 快速启动设置
   powercfg /hibernate off  # 可选：禁用休眠以确保纯睡眠模式
   
   # 网络适配器电源管理
   powercfg /devicedisablewake "网络适配器名称"  # 如需禁用特定设备唤醒
   ```

### Ubuntu服务器配置

1. **网络配置**
   ```bash
   # 确保IPv6连接正常
   ping6 -c 3 2001:4860:4860::8888
   
   # 检查防火墙设置
   sudo ufw status
   sudo ufw allow 5000/tcp  # 如需要
   ```

2. **服务状态检查**
   ```bash
   # 检查服务状态
   sudo systemctl status wol-server
   
   # 查看日志
   sudo journalctl -u wol-server -f
   
   # 重启服务
   sudo systemctl restart wol-server
   ```

### 云服务器配置

1. **网络要求**
   - 公网IPv6地址
   - 端口80开放
   - 与Ubuntu服务器IPv6连通

2. **SSL配置（可选）**
   ```nginx
   # Nginx反向代理配置示例
   server {
       listen 443 ssl;
       server_name your-domain.com;
       
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       
       location / {
           proxy_pass http://127.0.0.1:80;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```


## 运行程序

### 1. 启动本地Ubuntu服务器

```bash
python3 wol.py
```
服务运行在 `http://[::]:5000` (支持IPv4和IPv6)

### 2. 启动云服务器

```bash
sudo python3 cloud_server.py
```
服务运行在 `http://0.0.0.0:80`

## 访问Web界面

打开浏览器访问云服务器地址，即可使用Web界面控制Windows主机。

## 🔧 故障排除

### 常见问题

#### 1. Windows主机无法唤醒
```bash
# 检查Magic Packet发送
sudo tcpdump -i any port 9 -v

# 测试网络连通性
ping 192.168.1.100
```

**解决方案：**
- 检查网卡WOL设置
- 确认BIOS中WOL已启用
- 检查Windows电源计划设置

#### 2. SSH连接失败
```bash
# 测试SSH连接
ssh username@192.168.1.100

# 检查SSH服务状态
ssh username@192.168.1.100 "Get-Service sshd"
```

**解决方案：**
- 确认OpenSSH Server已安装并启动
- 检查Windows防火墙设置
- 验证用户名密码正确

#### 3. 睡眠命令不生效
```powershell
# 测试PowerShell命令
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.Application]::SetSuspendState([System.Windows.Forms.PowerState]::Suspend, $false, $false)
```

**解决方案：**
- 检查用户权限
- 确认电源计划允许睡眠
- 尝试禁用快速启动

#### 4. 状态检测不准确
```bash
# 调试检测功能
curl http://your-server/debug-status
```

**解决方案：**
- 检查各项网络连通性
- 调整检测超时时间
- 查看详细错误日志

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

本项目采用 MIT 许可证。

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者！

---

## 📞 联系方式

如有问题或建议，请通过GitHub Issues联系。

**项目作者**: [Gofoyi](https://github.com/Gofoyi)  
**项目地址**: [https://github.com/Gofoyi/Wol](https://github.com/Gofoyi/Wol)
