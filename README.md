# AngelEye - Emergency Crash Detection & Reporting System

A comprehensive crash detection and emergency reporting system that automatically captures and uploads crash footage to emergency departments.

## 🚨 Features

- **Real-time Crash Detection**: Uses MPU6050 accelerometer to detect sudden impacts
- **Video Buffering**: Continuously records video with 10-second buffer
- **Automatic Upload**: Instantly uploads crash footage to emergency servers
- **Emergency Dashboard**: Web interface for emergency departments to review footage
- **Retry Logic**: Robust upload system with automatic retries
- **Device Identification**: Unique device tracking for multiple vehicles

## 📁 Project Structure

```
AngelEye - Python/
├── main.py                 # Main crash detection program (Raspberry Pi)
├── upload_service.py       # Upload service for emergency servers
├── emergency_server.py     # Emergency department web server
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── templates/
│   └── dashboard.html     # Emergency department web interface
└── README.md             # This file
```

## 🛠️ Installation

### For Raspberry Pi (Client)

1. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Enable I2C interface:**
   ```bash
   sudo raspi-config
   # Interface Options → I2C → Enable
   ```

3. **Install I2C tools:**
   ```bash
   sudo apt-get install i2c-tools
   ```

4. **Connect MPU6050 sensor:**
   - VCC → 3.3V
   - GND → GND
   - SCL → GPIO3 (SCL)
   - SDA → GPIO2 (SDA)

5. **Configure server URL:**
   Edit `config.py` and update `CLIENT_CONFIG['server_url']` with your emergency server address.

### For Emergency Department Server

#### Option 1: Local SQLite Server

1. **Install dependencies:**
   ```bash
   pip3 install flask flask-cors requests
   ```

2. **Configure server settings:**
   Edit `config.py` to set your server preferences.

3. **Run the server:**
   ```bash
   python3 emergency_server.py
   ```

#### Option 2: Supabase Cloud Server

1. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Set up Supabase:**
   ```bash
   python3 setup_supabase.py
   ```

3. **Configure environment variables:**
   ```bash
   # Windows
   set SUPABASE_URL=your-supabase-url
   set SUPABASE_ANON_KEY=your-supabase-anon-key
   
   # Linux/Mac
   export SUPABASE_URL=your-supabase-url
   export SUPABASE_ANON_KEY=your-supabase-anon-key
   ```

4. **Run the Supabase server:**
   ```bash
   python3 emergency_server_supabase.py
   ```

## 🚀 Usage

### Starting the Crash Detection System (Raspberry Pi)

```bash
python3 main.py
```

The system will:
- Start video recording with 10-second buffer
- Monitor accelerometer data
- Save and upload crash footage when impact detected
- Display status messages

### Starting the Emergency Department Server

#### Local SQLite Server
```bash
python3 emergency_server.py
```

#### Supabase Cloud Server
```bash
python3 emergency_server_supabase.py
```

Access the dashboard at: `http://your-server-ip:5000`

## 📊 Emergency Department Dashboard

The web dashboard provides:

- **Real-time crash reports** with video playback
- **Statistics overview** (total crashes, new reports, urgent cases)
- **Status management** (mark as urgent, reviewed, etc.)
- **Device tracking** for multiple vehicles
- **Auto-refresh** every 30 seconds

## ⚙️ Configuration

### Client Settings (`config.py`)

```python
CLIENT_CONFIG = {
    'server_url': 'http://your-server.com:5000',
    'acceleration_threshold': 20,  # Adjust sensitivity
    'frame_rate': 30,
    'buffer_seconds': 10
}
```

### Server Settings (`config.py`)

```python
SERVER_CONFIG = {
    'host': '0.0.0.0',
    'port': 5000,
    'upload_folder': 'crash_videos',
    'max_file_size': 100 * 1024 * 1024  # 100MB
}
```

## 🔧 Hardware Requirements

### Raspberry Pi Setup
- Raspberry Pi 3/4 with camera module
- MPU6050 accelerometer/gyroscope sensor
- MicroSD card (16GB+ recommended)
- Power supply

### Emergency Department Server
- Any computer/server with Python 3.7+
- Internet connection for client uploads
- Storage space for crash videos

## 🔒 Security Considerations

- **API Keys**: Add authentication to `config.py` for production
- **SSL/TLS**: Enable HTTPS for secure communications
- **Firewall**: Configure network access appropriately
- **Data Privacy**: Implement data retention policies

## 🐛 Troubleshooting

### Common Issues

1. **MPU6050 not detected:**
   ```bash
   sudo i2cdetect -y 1
   # Should show device at address 0x68
   ```

2. **Upload failures:**
   - Check network connectivity
   - Verify server URL in config
   - Check server is running

3. **Video not recording:**
   - Ensure camera is connected
   - Check camera permissions
   - Verify storage space

### Debug Mode

Enable debug logging by modifying the upload service:
```python
# In upload_service.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Future Enhancements

- **GPS Integration**: Add location data to crash reports
- **Machine Learning**: Improve crash detection accuracy
- **Mobile App**: Emergency department mobile interface
- **Cloud Storage**: AWS/Azure integration for scalability
- **Real-time Alerts**: SMS/email notifications
- **Analytics**: Crash pattern analysis

## 📞 Support

For technical support or feature requests, please contact the development team.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**⚠️ Important**: This system is designed for emergency response. Ensure proper testing and validation before deployment in production environments. 