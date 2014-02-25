import socket
import httplib2
import json
import struct
from threading import Thread

class Address:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        
    def to_str(self):
        return self.host + ':' + str(self.port)

CLIENT = httplib2.Http()

SIMULATOR_ADDRESS = Address('localhost', 9080)
MEASURE_BUFFER_ADDRESS = Address('localhost', 9090)

STATUS = {'OK' : 200}

# when there is no expected structure to receive
DEFAULT_MESSAGE_SIZE = 100
# server sends 16-bit integers
SINGLE_NUMBER_SIZE = 2

expected_data = []



def run():
    print ('Angel Simulator client.', 'Type help for options')
    while True:
        cmd = input()
        
        if cmd == 'exit':
            break
        
        elif cmd == 'help':
            print_menu()
            
        elif cmd.startswith('simulator address'):
            params = cmd[len('simulator address'):].split(':')
            if len(params) > 1:
                SIMULATOR_ADDRESS.host = params[0].strip()
                SIMULATOR_ADDRESS.port = int(params[1].strip())
                
            print ('Simulator address set at', SIMULATOR_ADDRESS.to_str())
            
        elif cmd == 'detect':
            resp, content = send_simulator_request('/name')
            if resp.status != STATUS['OK']:
                print('could not detect an angle simulator running at', SIMULATOR_ADDRESS.to_str())
            else:
                resp_str = content.decode('UTF-8')
                resp_data = json.loads(resp_str)
                simulator_name = resp_data['name']
                print('angel simulator:', simulator_name)
        
        elif cmd == 'data':
            resp, content = send_simulator_request('/data')
            if resp.status != STATUS['OK']:
                print('could not retrieve available data from simulator')
            else:
                resp_str = content.decode('UTF-8')
                resp_data = json.loads(resp_str)
                data_measures = resp_data['measures']
                print('available measures:', data_measures)
                
        elif cmd == 'connect':
            socket_thread = Thread(target = open_socket)
            socket_thread.setDaemon(True)
            socket_thread.start()
                
            resp, content = send_simulator_request("/connect?host=%s&port=%d" % (MEASURE_BUFFER_ADDRESS.host, MEASURE_BUFFER_ADDRESS.port))
            if resp.status != STATUS['OK']:
                print('could not connect to simulator')
            else:
                resp_str = content.decode('UTF-8')
                resp_data = json.loads(resp_str)
                resp_stat = resp_data['connect']
                if resp_stat != 'OK':
                    print('could not connect to simulator')                        
        
        elif cmd == 'disconnect':
            send_simulator_request('/disconnect')
            
        elif cmd.startswith('subscribe'):
            params = cmd[len('subscribe'):].split(',')
            if len(params) == 0:
                print('no data measures selected')
            else:
                param_str = ''
                for param in params:
                    param_str += param.strip()
                    param_str += ','
                # remove last ','
                param_str = param_str[0:len(param_str)-1].replace(' ', '+')
                
            resp, content = send_simulator_request('/subscribe?measures=' + param_str)
            if resp.status != STATUS['OK']:
                print('could not connect to simulator')
            else:
                resp_str = content.decode('UTF-8')
                resp_data = json.loads(resp_str)
                if 'missing' in resp_data:
                    print('no valid measures received, not sending data')
                else:
                    subscribed_types = resp_data['subscribed']
                    print('subscribed to', subscribed_types)
                    expected_data.clear()
                    for measure in subscribed_types:
                        expected_data.append(measure)
        
        else:
            print(cmd, 'is not a recognized command.', 'Type help for options')

def print_menu():
    print('simulator address [address : port]:', 'prints or sets the target address for communicating with the simulator')
    print('detect:', 'probes the configured address for a running simulator and prints the simulators name')
    print('data:', 'prints the available measures by the simulator')
    print('connect:', 'connects to the simulator', 'opens a socket connection to transmit measures')
    print('disconnect:', 'disconnects from the simulator')
    print('subscribe <measure1>, <measure2>, ...', 'subscribe to recieve measures from the simulator')
    print('exit:', 'quits the program')

def send_simulator_request(req_path):
    url = 'http://' + SIMULATOR_ADDRESS.host + ':' + str(SIMULATOR_ADDRESS.port) + req_path
    return CLIENT.request(url, 'GET')

def open_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((MEASURE_BUFFER_ADDRESS.host, MEASURE_BUFFER_ADDRESS.port))
    print('Waiting for connections')
    sock.listen(1)
    conn, addr = sock.accept()
    print('Connected by', addr)
    while True:
        rcv_data = receive(conn)
        if not rcv_data:
            break
        for part in rcv_data:
            print(part, rcv_data[part])
    
    print('Disconnected')
    conn.close()
    
def receive(conn):
    if len(expected_data) > 0:
        msg_size = len(expected_data) * SINGLE_NUMBER_SIZE
        msg = conn.recv(msg_size)
        if not msg:
            return None
        ret = {}
        idx = 0
        while (idx * SINGLE_NUMBER_SIZE) < len(msg):
            ret[expected_data[idx]] = struct.unpack("!h", msg[idx * SINGLE_NUMBER_SIZE : (idx+1) * SINGLE_NUMBER_SIZE])[0]
            idx += 1 
            
        return ret
    
    else:
        msg = conn.recv(DEFAULT_MESSAGE_SIZE)
        if not msg:
            return None
        return {'text' : msg}
    
if __name__ == "__main__":
    run()