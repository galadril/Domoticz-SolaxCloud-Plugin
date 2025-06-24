
# ☀️ Domoticz SolaxCloud Plugin

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)  [![GitHub issues](https://img.shields.io/github/issues/galadril/Domoticz-SolaxCloud-Plugin)](https://github.com/galadril/Domoticz-SolaxCloud-Plugin/issues) [![Last commit](https://img.shields.io/github/last-commit/galadril/Domoticz-SolaxCloud-Plugin)](https://github.com/galadril/Domoticz-SolaxCloud-Plugin/commits/main) [![Stars](https://img.shields.io/github/stars/galadril/Domoticz-SolaxCloud-Plugin?style=social)](https://github.com/galadril/Domoticz-SolaxCloud-Plugin/stargazers) [![Pull Requests](https://img.shields.io/github/issues-pr/galadril/Domoticz-SolaxCloud-Plugin)](https://github.com/galadril/Domoticz-SolaxCloud-Plugin/pulls) ![Python](https://img.shields.io/badge/Python-3.4+-blue.svg)

🔌 *Monitor your Solax inverter using SolaxCloud API v2 from within Domoticz.*

This plugin retrieves and displays **real-time data** from your **Solax solar inverter** using the official SolaxCloud API.

📘 More about SolaxCloud:\
🌐 [https://global.solaxcloud.com](https://global.solaxcloud.com)\
📄 [SolaxCloud API Documentation (PDF)](https://global.solaxcloud.com/green/user_api/SolaXCloud_User_API.pdf)

---

## 🚀 Features

- Live solar inverter data: AC power, DC channels, total yield, and battery SoC
- Uses **SolaxCloud v2 API**
- Designed for Domoticz 🏠
- Easy setup, auto device creation
- Open-source and extensible

---

## 📦 Installation

> Requires:\
> 🐍 Python 3.4+\
> 🏠 Domoticz 3.87xx or later

1. Open a terminal and go to your Domoticz `plugins` directory:

   ```bash
   cd /path/to/domoticz/plugins
   ```

2. Clone the plugin:

   ```bash
   git clone https://github.com/galadril/Domoticz-SolaxCloud-Plugin.git
   ```

3. Restart Domoticz.

---

## ⚙️ Configuration

1. In Domoticz, go to `Setup` → `Hardware`.
2. Add a new hardware of type **SolaxCloud**.
3. Fill in:
   - API address (default: `global.solaxcloud.com`)
   - API token
   - Wifi SN
4. Select the desired Debug level (optional).
5. Click **Add** to save.

---

## 🖥️ Devices Created

> The plugin auto-creates devices like:

| Device Name           | Type   | Description                         |
| --------------------- | ------ | ----------------------------------- |
| Total Energy Yield    | kWh    | Lifetime energy exported            |
| AC Power + YieldTotal | kWh    | Live power (W) + total yield (kWh)  |
| PV1 / PV2 Power       | Usage  | DC input from individual PV strings |
| Battery SoC           | Custom | Battery state of charge in %        |
| Inverter Status Code  | Text   | Raw inverter state                  |
| Today's Yield         | kWh    | Energy generated today              |

📷 Example screenshots:

![image](https://github.com/user-attachments/assets/19ddc61a-a7b6-4e25-a71e-10b47ea92146)

![image](https://github.com/user-attachments/assets/68311361-522f-4e82-ab99-3943a27b83b9)

---

## 🔁 Updating

To update the plugin:

```bash
cd /path/to/domoticz/plugins/Domoticz-SolaxCloud-Plugin
git pull
```

Then restart Domoticz.

---

## 🛠️ Debugging

Enable debugging under `Setup → Hardware → SolaxCloud`:

| Level Name          | Value |
| ------------------- | ----- |
| None                | 0     |
| Python Only         | 2     |
| Basic Debugging     | 62    |
| Basic + Messages    | 126   |
| Connections Only    | 16    |
| Connections + Queue | 144   |
| All                 | -1    |

---

## 📝 Changelog

| Version | Notes                                            |
| ------- | ------------------------------------------------ |
| 0.0.1   | Initial release                                  |
| 0.0.3   | Migrated to official SolaxCloud API (v2)         |
| 0.0.4   | Fixes for AC power values; improved device logic |

---

## ☕ Support / Donate

If you like this plugin, feel free to support future development:
[![PayPal donate button](https://img.shields.io/badge/paypal-donate-yellow.svg)](https://www.paypal.me/markheinis)

Thanks for your support! ❤️

