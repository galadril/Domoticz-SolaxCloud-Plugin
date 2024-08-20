"""
<plugin key="Domoticz-SolaxCloud-Plugin" name="Domoticz SolaxCloud Plugin" author="Mark Heinis" version="0.0.1" wikilink="http://www.domoticz.com/wiki/plugins/plugin.html" externallink="https://github.com/galadril/Domoticz-SolaxCloud-Plugin">
    <description>
        Plugin for retrieving and updating EV Charger data from SolaxCloud.
    </description>
    <params>
        <param field="Username" label="Username" width="200px" required="false" default=""/>
        <param field="Password" label="Password" width="200px" required="false" default="" password="true"/>
        <param field="Mode6" label="Debug" width="200px">
            <options>
                <option label="None" value="0"  default="true" />
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
import time
import datetime

class SolaxPlugin:
    def __init__(self):
        self.token = ""
        self.userId = ""
        self.siteId = ""
        self.solax_site = 'www.solaxcloud.com:6080'
        self.token_url = f'http://{self.solax_site}/proxy/login/login'
        self.mysite_url = f'http://{self.solax_site}/proxy/mysite/mySite'
        self.alldata_url = f'http://{self.solax_site}/proxy/mysite/getInverterInfo'

    def onStart(self):
        Domoticz.Debugging(int(Parameters["Mode6"]))
        Domoticz.Log("SolaxPlugin: onStart called")
        self.createDevices()
        self.login()
        Domoticz.Heartbeat(30)

    def login(self):
        Domoticz.Log("SolaxPlugin: Starting login process")
        username = Parameters["Username"]
        password = Parameters["Password"]
        if not username or not password:
            Domoticz.Error("SolaxPlugin: Username or Password not provided")
            return

        payload = {
            "userName": username,
            "password": password,
            "userType": 5
        }
        try:
            response = requests.post(self.token_url, data=payload)
            response.raise_for_status()
            data = response.json()
            if data.get('success'):
                self.token = data['result']['tokenId']
                self.userId = data['result']['userId']
                Domoticz.Log(f"SolaxPlugin: Login successful. Token: {self.token}, UserId: {self.userId}")
                self.getSiteId()
            else:
                Domoticz.Error("SolaxPlugin: Login failed: " + data.get('exception', 'Unknown error'))
        except requests.RequestException as e:
            Domoticz.Error(f"SolaxPlugin: Login request failed: {str(e)}")

    def getSiteId(self):
        Domoticz.Log("SolaxPlugin: Retrieving Site ID")
        payload = {
            "tokenId": self.token,
            "userId": self.userId,
        }
        try:
            response = requests.post(self.mysite_url, data=payload)
            response.raise_for_status()
            data = response.json()
            if data.get('success'):
                self.siteId = data['result'][0]['siteId']
                Domoticz.Log(f"SolaxPlugin: Site ID retrieved: {self.siteId}")
                self.updateDevice()
            else:
                Domoticz.Error("SolaxPlugin: Failed to get Site ID: " + data.get('exception', 'Unknown error'))
        except requests.RequestException as e:
            Domoticz.Error(f"SolaxPlugin: Get Site ID request failed: {str(e)}")


    def updateDevice(self):
        if not self.token or not self.siteId:
            Domoticz.Error("SolaxPlugin: No token or siteId available")
            return

        Domoticz.Log("SolaxPlugin: Updating device")
        url = f'{self.alldata_url}?siteId={self.siteId}&tokenId={self.token}'
        try:
            response = requests.post(url)
            response.raise_for_status()
            data = response.json()
            Domoticz.Debug(f"SolaxPlugin: Inverter data received: {data}")

            if data.get('success'):
                inverter_data = data['result'][0]
                    
                last_update_time_str = inverter_data['lastUpdateTimes']
                Domoticz.Log(f"SolaxPlugin: Last update time: {last_update_time_str}")

                # Convert last update time to a datetime object
                if last_update_time_str and last_update_time_str != "None":
                    last_update_time = datetime.datetime.strptime(last_update_time_str, '%Y-%m-%d %H:%M:%S')

                    # Calculate the time difference between now and the last update time
                    time_diff = datetime.datetime.now() - last_update_time
                    minutes_diff = time_diff.total_seconds() / 60.0

                    # Set grid_power_w to 0 if the last update was more than 10 minutes ago
                    if minutes_diff > 10:
                        grid_power_w = 0
                    else:
                        grid_power_w = inverter_data['gridPower']

                # Correct the unit conversion
                total_yield_kwh = inverter_data['totalYield']
                total_yield_wh = total_yield_kwh * 1000
                today_yield_kwh = inverter_data['rgmTodayYield']
                today_yield_wh = today_yield_kwh * 1000

                # Update devices with received data
                self.updateDeviceValue(1, 0, f"0;{total_yield_wh:.4f}")  # Total Energy Yield in kWh
                self.updateDeviceValue(2, 0, f"{grid_power_w};{total_yield_wh:.4f}")  # Grid Power in W and Today's Energy Yield in kWh

                # Update other devices
                self.updateDeviceValue(3, 0, inverter_data['pv1Voltage'])
                self.updateDeviceValue(4, 0, inverter_data['pv1Current'])
                self.updateDeviceValue(5, 0, inverter_data['powerdc1'])
                self.updateDeviceValue(6, 0, inverter_data['vac1'])
                self.updateDeviceValue(7, 0, inverter_data['iac1'])
                self.updateDeviceValue(8, 0, inverter_data['fac1'])
                self.updateDeviceValue(9, 0, inverter_data['temperature'])
            else:
                Domoticz.Error("SolaxPlugin: Failed to retrieve inverter data: " + data.get('exception', 'Unknown error'))
        except requests.RequestException as e:
            Domoticz.Error(f"SolaxPlugin: Update device request failed: {str(e)}")

    def onStop(self):
        Domoticz.Log("SolaxPlugin: Stopped")

    def onHeartbeat(self):
        Domoticz.Log("SolaxPlugin: Heartbeat called")
        if not self.token:
            Domoticz.Log("SolaxPlugin: Token not available, retrying login...")
            self.login()
        else:
            self.updateDevice()

    def createDevices(self):
        Domoticz.Log("SolaxPlugin: Creating devices")

        # Create kWh devices with energy meter mode calculated and switchtype for exporting energy
        if len(Devices) < 1:
            Domoticz.Device(Name="Total Energy Yield", Unit=1, TypeName='kWh', Switchtype=4).Create()
        if len(Devices) < 2:
            Domoticz.Device(Name="Grid Power", Unit=2, TypeName='kWh', Switchtype=4).Create()

        # Create other types of devices
        if len(Devices) < 3:
            Domoticz.Device(Name="PV1 Voltage", Unit=3, TypeName='Voltage').Create()
        if len(Devices) < 4:
            Domoticz.Device(Name="PV1 Current", Unit=4, TypeName='Usage', Options={'ValueQuantity': 'Current', 'ValueUnits': 'A'}).Create()
        if len(Devices) < 5:
            Domoticz.Device(Name="Power DC1", Unit=5, TypeName='Usage').Create()
        if len(Devices) < 6:
            Domoticz.Device(Name="AC Voltage", Unit=6, TypeName='Voltage').Create()
        if len(Devices) < 7:
            Domoticz.Device(Name="AC Current", Unit=7, TypeName='Usage', Options={'ValueQuantity': 'Current', 'ValueUnits': 'A'}).Create()
        if len(Devices) < 8:
            Domoticz.Device(Name="AC Frequency", Unit=8, TypeName='Custom', Options={'ValueQuantity': 'Frequency', 'ValueUnits': 'Hz'}).Create()
        if len(Devices) < 9:
            Domoticz.Device(Name="Inverter Temperature", Unit=9, TypeName='Temperature').Create()

    def updateDeviceValue(self, unit, nValue, sValue):
        try:
            if unit in Devices:
                Domoticz.Log(f"SolaxPlugin: Updating device {unit} - nValue: {nValue}, sValue: {sValue}")
                Devices[unit].Update(nValue=nValue, sValue=str(sValue), TimedOut=0)
            else:
                Domoticz.Error(f"SolaxPlugin: Device with unit {unit} not found.")
        except Exception as e:
            Domoticz.Error(f"SolaxPlugin: Error updating device {unit}: {e}")

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
