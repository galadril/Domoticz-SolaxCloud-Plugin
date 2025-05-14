"""
<plugin key="Domoticz-SolaxCloud-Plugin" name="Domoticz SolaxCloud Plugin" author="Mark Heinis" version="0.0.3" wikilink="http://www.domoticz.com/wiki/plugins/plugin.html" externallink="https://github.com/galadril/Domoticz-SolaxCloud-Plugin">
    <description>
        Plugin for retrieving and updating inverter data from SolaxCloud (API v2).
    </description>
    <params>
        <param field="Address" label="API Address" width="200px" required="true" default="global.solaxcloud.com"/>
        <param field="Mode1" label="API Token" width="300px" required="true" default=""/>
        <param field="Mode2" label="Wifi SN" width="300px" required="true" default=""/>
        <param field="Mode6" label="Debug" width="200px">
            <options>
                <option label="None" value="0" default="true"/>
                <option label="Python Only" value="2"/>
                <option label="Basic Debugging" value="62"/>
                <option label="Basic+Messages" value="126"/>
                <option label="Connections Only" value="16"/>
                <option label="Connections+Queue" value="144"/>
                <option label="All" value="-1"/>
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
import requests
import datetime

class SolaxPlugin:

    def __init__(self):
        self.token = ""
        self.wifi_sn = ""
        self.api_url = ""
        self.lastPollCounter = 0

    def onStart(self):
        Domoticz.Log("SolaxPlugin: onStart called")
        Domoticz.Debugging(int(Parameters["Mode6"]))
        
        # Log the initial parameters
        Domoticz.Debug(f"API Address: {Parameters['Address']}")
        Domoticz.Debug(f"API Token: {Parameters['Mode1']}")
        Domoticz.Debug(f"Wifi SN: {Parameters['Mode2']}")
        
        self.token = Parameters["Mode1"]
        self.wifi_sn = Parameters["Mode2"]
        self.api_url = f"https://{Parameters['Address']}/api/v2/dataAccess/realtimeInfo/get"
        
        if not self.token or not self.wifi_sn:
            Domoticz.Error("SolaxPlugin: Missing token or wifiSn. Please configure in settings.")
            
        self.createDevices()
        Domoticz.Heartbeat(30)

    def onStop(self):
        Domoticz.Log("SolaxPlugin: Stopped")

    def onHeartbeat(self):
        Domoticz.Log("SolaxPlugin: onHeartbeat called")
        self.lastPollCounter += 1
        if self.lastPollCounter < 5:
            return

        self.lastPollCounter = 0
        self.updateDevice()

    def updateDevice(self):
        Domoticz.Log("SolaxPlugin: updateDevice called")
        headers = {
            "tokenId": self.token,
            "Content-Type": "application/json"
        }
        payload = {
            "wifiSn": self.wifi_sn
        }

        try:
            Domoticz.Log(f"SolaxPlugin: Sending POST request to {self.api_url} with payload {payload}")
            response = requests.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            if data.get("success"):
                result = data["result"]

                # Parse uploadTime
                upload_time_str = result.get("uploadTime")
                if not upload_time_str:
                    Domoticz.Error("SolaxPlugin: No uploadTime found in response.")
                    return

                upload_time = datetime.datetime.strptime(upload_time_str, "%Y-%m-%d %H:%M:%S")
                current_time = datetime.datetime.now()

                # Compare the upload time with the current time (optional: threshold of 10 minutes)
                time_diff = current_time - upload_time
                if time_diff > datetime.timedelta(minutes=10):  # Only accept data within the last 10 minutes
                    Domoticz.Debug(f"SolaxPlugin: Data is older than 10 minutes. Skipping update.")
                    return

                # Core values
                ac_power = result.get("acpower", 0)
                yield_today = result.get("yieldtoday", 0)
                yield_total = result.get("yieldtotal", 0)

                # Convert to Wh for compatibility
                yield_today_wh = yield_today * 1000
                yield_total_wh = yield_total * 1000

                self.updateDeviceValue(1, 0, f"0;{yield_total_wh:.2f}")
                self.updateDeviceValue(2, 0, f"{ac_power};{yield_today_wh:.2f}")

                # Optional devices, add safety .get() checks
                self.updateDeviceValue(3, 0, result.get("powerdc1", 0))
                self.updateDeviceValue(4, 0, result.get("powerdc2", 0))
                self.updateDeviceValue(5, 0, result.get("soc", 0))
                self.updateDeviceValue(6, 0, result.get("inverterStatus", 0))

                Domoticz.Log("SolaxPlugin: Data updated")
            else:
                Domoticz.Error("SolaxPlugin: API Error - " + data.get("exception", "Unknown"))
        except Exception as e:
            Domoticz.Error(f"SolaxPlugin: Exception occurred: {str(e)}")

    def createDevices(self):
        if len(Devices) < 1:
            Domoticz.Device(Name="Total Energy Yield", Unit=1, TypeName='kWh', Switchtype=4).Create()
        if len(Devices) < 2:
            Domoticz.Device(Name="AC Power / Today's Yield", Unit=2, TypeName='kWh', Switchtype=4).Create()
        if len(Devices) < 3:
            Domoticz.Device(Name="PV1 Power", Unit=3, TypeName='Usage').Create()
        if len(Devices) < 4:
            Domoticz.Device(Name="PV2 Power", Unit=4, TypeName='Usage').Create()
        if len(Devices) < 5:
            Domoticz.Device(Name="Battery SoC", Unit=5, TypeName='Custom', Options={'ValueQuantity': 'Percentage', 'ValueUnits': '%' }).Create()
        if len(Devices) < 6:
            Domoticz.Device(Name="Inverter Status Code", Unit=6, TypeName='Text').Create()

    def updateDeviceValue(self, unit, nValue, sValue):
        try:
            if unit in Devices:
                Devices[unit].Update(nValue=nValue, sValue=str(sValue), TimedOut=0)
        except Exception as e:
            Domoticz.Error(f"SolaxPlugin: Failed to update unit {unit}: {e}")

global _plugin
_plugin = SolaxPlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()
