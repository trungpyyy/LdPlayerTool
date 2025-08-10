# Rise of Kingdoms Tool (LD Tool)

An automation tool for the mobile game "Rise of Kingdoms" that runs on Android devices. Built with Python and uses ADB (Android Debug Bridge) to control Android devices and automate various in-game tasks.

## ✨ Features

### 🎮 **Game Automation**
- **🏠 House Management**: Automates building construction and upgrades
- **🌾 Farming**: Automates resource collection (stone, wood, food, gold)
- **🔍 Exploration**: Automates cloud exploration and cave probing
- **⚔️ Training**: Automates troop training
- **👥 Recruitment**: Automates troop recruitment

### 📱 **Device Management**
- Multi-device support
- Automatic device detection and connection
- Device status monitoring
- Connection error recovery

### 🎛️ **User Interface**
- Clean, modern GUI built with tkinter
- Real-time task status monitoring
- Live log display
- Task pause/resume functionality
- Device selection dropdown

## 🚀 Recent Improvements

### 🔧 **Enhanced Error Handling**
- Comprehensive try-catch blocks throughout the codebase
- Detailed error logging with context information
- Automatic error recovery mechanisms
- User-friendly error messages

### 📊 **Advanced Logging System**
- File-based logging with timestamps
- Console output for real-time monitoring
- Log rotation and management
- Configurable log levels (DEBUG, INFO, WARNING, ERROR)

### ⚙️ **Configuration Management**
- Centralized configuration file (`config.py`)
- Environment variable support
- Configurable delays, timeouts, and thresholds
- Easy customization without code changes

### 🛡️ **Robust ADB Integration**
- Connection testing and validation
- Timeout handling for ADB operations
- Automatic screenshot capture with error handling
- Device connection monitoring

## 📋 Requirements

- Python 3.7+
- Android Debug Bridge (ADB)
- Connected Android device(s)
- Required Python packages (see `requirements.txt`)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ld_tool
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup ADB**
   - Ensure ADB is installed and accessible
   - Connect your Android device(s) via USB
   - Enable USB debugging on your device(s)

4. **Run the tool**
   ```bash
   python main.py
   ```

## ⚙️ Configuration

The tool is highly configurable through the `config.py` file:

### **ADB Settings**
```python
ADB_PATH = "adb/adb.exe"
ADB_TIMEOUT = 15  # seconds
ADB_RETRY_ATTEMPTS = 3
```

### **Image Recognition**
```python
TEMPLATE_MATCHING_THRESHOLD = 0.9  # 0.0 to 1.0
IMAGE_CAPTURE_DELAY = 1.0  # seconds
TEMPLATE_SEARCH_TIMEOUT = 10  # seconds
```

### **Task Delays**
```python
FARM_DELAY = 2.0
EXPLORE_DELAY = 3.0
TRAIN_DELAY = 1.5
RECRUITMENT_DELAY = 2.0
```

### **Environment Variables**
You can also override settings using environment variables:
```bash
export LD_TOOL_ADB_PATH="/custom/path/to/adb"
export LD_TOOL_THRESHOLD="0.85"
export LD_TOOL_LOG_LEVEL="DEBUG"
```

## 📱 Usage

1. **Launch the tool**
   - Run `python main.py`
   - The GUI will appear with device selection

2. **Connect devices**
   - Click "🔄 Refresh Devices" to detect connected devices
   - Select your device from the dropdown

3. **Configure tasks**
   - Check the tasks you want to automate:
     - ☑️ Thu hoạch (Farming)
     - ☑️ Dò mây (Cloud Exploration)
     - ☑️ Dò hang (Cave Probing)
     - ☑️ Huấn luyện lính (Troop Training)

4. **Monitor and control**
   - Use "⏸ Tạm dừng" to pause/resume tasks
   - View real-time logs in the text area
   - Click "🏠 Quản lý nhà" for house management

## 📁 Project Structure

```
ld_tool/
├── main.py                 # Main application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── utils/                # Utility modules
│   ├── AdbProcess.py     # ADB communication
│   ├── Detect.py         # Image recognition
│   ├── error_handler.py  # Error handling utilities
│   └── HouseManager.py   # House management logic
├── task/                 # Task automation modules
│   ├── farm.py          # Farming automation
│   ├── explore.py       # Exploration automation
│   ├── train.py         # Training automation
│   └── requirement.py   # Recruitment automation
├── images/               # Template images for recognition
└── logs/                 # Log files (created automatically)
```

## 🔍 Troubleshooting

### **Common Issues**

1. **"ADB executable not found"**
   - Verify ADB path in `config.py`
   - Ensure ADB is installed and accessible

2. **"No devices found"**
   - Check USB connection
   - Enable USB debugging on device
   - Run `adb devices` in terminal to verify

3. **Image recognition not working**
   - Adjust `TEMPLATE_MATCHING_THRESHOLD` in config
   - Verify template images exist in `images/` folder
   - Check device screen resolution compatibility

4. **Tasks not executing**
   - Check device selection
   - Verify task checkboxes are enabled
   - Check log messages for errors

### **Debug Mode**
Enable verbose logging by setting in `config.py`:
```python
LOG_LEVEL = "DEBUG"
ENABLE_VERBOSE_LOGGING = True
```

## 📝 Logging

The tool creates detailed logs in the `logs/` directory:
- **File logs**: Timestamped log files with full details
- **Console logs**: Real-time output during execution
- **GUI logs**: Live display in the application window

Log files are automatically created with timestamps:
```
logs/ld_tool_20241201_143022.log
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add error handling and logging
5. Test thoroughly
6. Submit a pull request

## 📄 License

This project is for educational and personal use only. Please respect the terms of service of "Rise of Kingdoms" game.

## ⚠️ Disclaimer

This tool is designed for educational purposes and personal automation. Use at your own risk and in accordance with the game's terms of service. The developers are not responsible for any consequences of using this tool.

## 🔄 Version History

### v2.0.0 (Current)
- ✨ Comprehensive error handling and logging
- ⚙️ Centralized configuration management
- 🛡️ Robust ADB integration
- 📊 Advanced logging system
- 🎨 Improved user interface

### v1.0.0
- 🎮 Basic game automation features
- 📱 Multi-device support
- 🖥️ Simple GUI interface

---

**Happy gaming! 🎮✨**
