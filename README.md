## raspiot-server
#### IoT device manager, the core component of raspiot.

As an IoT device manager, raspiot-server supports communication with IoT devices using HTTP, TCP, UDP, and BLE protocols, 
and periodically polls to synchronize the status of the IoT devices. 

It also provides REST APIs for UI or app integration, allowing users to conveniently manage IoT devices through the interface. 
IoT devices only need to implement two simple interfaces, `get_device_attrs` and `set_device_attr`, to connect to raspiot-server. 

The UI can build dedicated operation pages based on the attribute types returned by the devices.