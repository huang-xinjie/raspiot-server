import sys
import json
import socket
import threading

from api import service
from common import constants
from config import user
from kernel.iot_manager import IotManager


def relay_by_cloud_server(cmd_parser):
    # for CloudServer authorized
    rasp_server_identity_json = json.dumps({'identity': user.ACCOUNT})
    while True:
        sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sc.connect(user.CLOUD_SERVER_ADDRESS)
            sc.sendall(rasp_server_identity_json.encode())
            print('Connect cloud server successfully.')
        except Exception as e:
            print('****************************************************')
            print('* Error: Connect cloud server exception.           *')
            print('* Reason: %-40s *' % str(e).strip())
            print('****************************************************')
            return
        recv_json = sc.recv(constants.BUFF_SIZE).decode()
        if recv_json == 'Connect finished.' or recv_json == '':
            continue
        elif recv_json == 'Heartbeat detection.':
            sc.sendall('Roger.'.encode())
            continue
        elif recv_json == 'You need to log in.':
            print('From raspCloud: ', recv_json)
            return
        print('From cloud: ', recv_json)
        try:
            recv_data = json.loads(recv_json)
            cmd_parser.command_parser(sc, recv_data)
        except Exception:
            sc.sendall('Invalid json!'.encode())
            sc.close()


def house_keeper(cmd_parser):
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        ss.bind(("0.0.0.0", 22015))
        ss.listen(5)
    except OSError:
        sys.exit('rasp_server has started, please check.')

    while True:
        conn, addr = ss.accept()
        print("connected by ", addr)
        try:
            recv_json = conn.recv(constants.BUFF_SIZE).decode()
            recv_data = json.loads(recv_json)
            print(recv_data)
            cmd_parser.command_parser(conn, recv_data)
        except ValueError:
            print('Json data error, connection is close.')
            conn.close()
        except KeyboardInterrupt:
            print('KeyboardInterrupt~')
            ss.close()
            break


if __name__ == '__main__':
    print('raspServer is running.')
    iot_manager = IotManager()
    cmd_parser = iot_manager.get_cmd_parser()
    threading.Thread(target=relay_by_cloud_server, args=(cmd_parser,)).start()
    threading.Thread(target=house_keeper, args=(cmd_parser,)).start()

    api = service.create('default')
    api.run(host='0.0.0.0', port=80)
