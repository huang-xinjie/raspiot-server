from api import raspiot_api
from kernel.iot_manager import IotManager
from kernel.device_manager import DeviceHandler


@raspiot_api.route('/device/<uuid>')
def get_device(uuid):
    iot_manager = IotManager()
    device_handler = iot_manager.get_device_handler()
    device = device_handler.get_device_name_by_uuid(uuid)
    return {'device': device}
