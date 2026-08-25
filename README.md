# 🚀 Delta OS Pro Enterprise Firmware

Official Firmware Release Repository for **Delta OS Pro** running on MikroTik RouterBOARD SXT 5nD r2 (Atheros AR9344).

---

## 📦 Latest Release Files

* ⚡ **Firmware Sysupgrade Image:** `sysupgrade.bin`
* 📑 **Version Metadata:** `version.json`
* 🌐 **TFTP Netinstall Image:** `openwrt.bin`

---

## 🔄 Automatic Cloud Update Endpoint

Routers running Delta OS Pro fetch live updates directly from this repository:
* **Update Manifest:** `https://raw.githubusercontent.com/lawin115/delta-os/main/version.json`
* **Firmware Binary:** `https://raw.githubusercontent.com/lawin115/delta-os/main/sysupgrade.bin`

---

## 🛠 Features

* 🚀 **MIPS Exception Vector Handling & Custom Kernel Task Scheduler**
* ⚡ **Dynamic Heap Memory Allocator (`kmalloc`/`kfree`)**
* 📊 **Real-Time Live Noise Floor (`-96 dBm`) & CCQ Quality (`98%`) Engine**
* 🔐 **WebFig DeltaOS Web Interface with Mobile Client Portal**
* 📡 **Custom EEPROM Atheros Radio Patch for 5GHz Channels**
