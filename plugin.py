"""
<plugin key="Domoticz-SolaxCloud-Plugin" name="Domoticz SolaxCloud Plugin" author="Mark Heinis" version="0.0.4" wikilink="http://www.domoticz.com/wiki/plugins/plugin.html" externallink="https://github.com/galadril/Domoticz-SolaxCloud-Plugin">
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

STALE_THRESHOLD_MINUTES = 10  # Allow override via plugin params if needed

class SolaxPlugin:
    def __init__(self):
        self.token = ""
        self.wifi_sn = ""
        self.api_url = ""
        self.lastPollCounter = 0

    def onStart(self):
        Domoticz.Log("SolaxPlugin: onStart called")
        Domoticz.Debugging(int(Parameters["Mode6"]))

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
        self.lastPollCounter += 1
        if self.lastPollCounter < 5:
            return

        self.lastPollCounter = 0
        self.updateDevices()

    def fetchRealtimeData(self):
        headers = {
            "tokenId": self.token,
            "Content-Type": "application/json"
        }
        payload = {
            "wifiSn": self.wifi_sn
        }

        try:
            response = requests.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            if not data.get("success"):
                Domoticz.Error("SolaxPlugin: API Error - " + data.get("exception", "Unknown"))
                return None
            return data["result"]
        except Exception as e:
            Domoticz.Error(f"SolaxPlugin: Exception occurred while fetching data: {str(e)}")
            return None

    def updateDevices(self):
        result = self.fetchRealtimeData()
        if not result:
            return

        upload_time_str = result.get("uploadTime")
        if not upload_time_str:
            Domoticz.Error("SolaxPlugin: No uploadTime found in response.")
            return

        upload_time = datetime.datetime.strptime(upload_time_str, "%Y-%m-%d %H:%M:%S")
        current_time = datetime.datetime.now()
        if current_time - upload_time > datetime.timedelta(minutes=STALE_THRESHOLD_MINUTES):
            Domoticz.Debug("SolaxPlugin: Skipping stale data")
            return

        # Extract core values
        ac_power = result.get("acpower", 0)
        yield_today = result.get("yieldtoday", 0)  # kWh
        yield_total = result.get("yieldtotal", 0)  # kWh

        # Update devices
        self.updateDeviceValue(1, 0, f"0;{yield_total:.2f}")              # Total Energy Yield
        self.updateDeviceValue(2, 0, f"{ac_power};{yield_total:.2f}")    # AC Power + Total
        self.updateDeviceValue(3, 0, result.get("powerdc1", 0))
        self.updateDeviceValue(4, 0, result.get("powerdc2", 0))
        self.updateDeviceValue(5, 0, result.get("soc", 0))
        self.updateDeviceValue(6, 0, result.get("inverterStatus", 0))
        self.updateDeviceValue(7, 0, f"0;{yield_today:.2f}")             # Today's Yield

        Domoticz.Log("SolaxPlugin: Data updated")

    def createDevices(self):
        device_definitions = [
            (1, "Total Energy Yield",     'kWh',     {'Switchtype': 4}),
            (2, "AC Power + YieldTotal",  'kWh',     {'Switchtype': 4}),
            (3, "PV1 Power",              'Usage',   {}),
            (4, "PV2 Power",              'Usage',   {}),
            (5, "Battery SoC",            'Custom',  {'Options': {'ValueQuantity': 'Percentage', 'ValueUnits': '%'}}),
            (6, "Inverter Status Code",   'Text',    {}),
            (7, "Today's Yield",          'kWh',     {'Switchtype': 4}),
        ]

        for unit, name, typename, kwargs in device_definitions:
            if unit not in Devices:
                Domoticz.Device(Name=name, Unit=unit, TypeName=typename, **kwargs).Create()

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
