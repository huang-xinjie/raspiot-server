import multiprocessing

import log
from api import service
from iot.api import DeviceManagerApi
from iot.manager import DeviceManager


def start_device_manager(manager_pipe):
    log.info('start device manager.')
    device_manager = DeviceManager(manager_pipe)
    device_manager.run()


if __name__ == '__main__':
    parent_conn, child_conn = multiprocessing.Pipe()
    iot_device_manager = multiprocessing.Process(target=start_device_manager, args=(child_conn,))
    iot_device_manager.start()

    device_manager_api = DeviceManagerApi(parent_conn)
    flask_api = service.create(external_config={'device_manager_api': device_manager_api})

    log.info('raspiot-server is running.')
    flask_api.run(host='0.0.0.0', port=80, threaded=True)
