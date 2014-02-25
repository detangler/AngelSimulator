#!/usr/bin/env python
import socketserver
import http.server
import json
from threading import Thread
import time
from simulator import AngelSimulator
from data import xml_reader
from server.streamer import DataStreamer

resources = {}

class AngelSimulatorHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    """Simple HTTP request handler with GET and HEAD commands.

    This serves files from the current directory and any of its
    subdirectories.  The MIME type for files is determined by
    calling the .guess_type() method.

    The GET and HEAD requests are identical except that the HEAD
    request omits the actual contents of the file.

    """
    
    server_version = "AngelSimulatorService"

    def do_GET(self):
        """Serve a GET request."""         
        
        service, params = self.parse_request_path(self.path)
        if service in self.service_map:    
            resp = self.service_map[service](self, **params)
            print('response is', resp)
            self.send_json_response(resp)
        else:
            print('unsupported')

    def send_json_response(self, content):
        resp_bytes = bytearray(content, 'utf-8')
        self.send_response(200)
        self.send_header("Content-Type", 'application/json')
        self.send_header('charset', 'utf-8')
        self.send_header("Content-Length", len(resp_bytes))
        self.end_headers()
        self.wfile.write(resp_bytes)

    def parse_request_path(self, path):
        if '?' in path:            
            delimiter = path.index("?")
            main_path = path[:delimiter]
            params_str = path[delimiter+1:]
            
            params = {}
            for param in params_str.split('&'):
                parts = param.split('=')
                params[parts[0]] = parts[1]
                
            return main_path, params
        else:
            return path, {}
            

    def get_name(self, **kwargs):
        simulator = resources['simulator']
        return json.dumps({'name': simulator.get_name()})
        
    def list_data(self, **kwargs):
        simulator = resources['simulator']
        return json.dumps({'measures': list(simulator.get_data_types())})
    
    def open_conn(self, **kwargs):
        if not 'port' in kwargs:
            return json.dumps[{ 'missing' : 'port'}]
        
        target_port = int(kwargs['port'])
        
        # host can  be ommitted and is then the request source host by default
        if not 'host' in kwargs:
            target_host = self.client_address[0]         
        else:
            target_host = kwargs['host']
        
        if 'streamer' in resources and resources['streamer'].is_connected:
            resources['streamer'].disconnect()
        
        resources['streamer'] = DataStreamer(target_host, target_port)
        resources['streamer'].connect()
        
        return json.dumps({'connect' : 'OK'})
        
    def close_conn(self, **kwargs):
        if not 'streamer' in resources:
            return json.dumps({'error' : 'no connection'})
        
        if 'sender' in resources and resources['sender']:
            resources['sender'].stop()
        
        if resources['streamer'].is_connected:
            resources['streamer'].disconnect()
            
        return json.dumps({'connect' : 'CLOSED'})
        
    def set_send_data(self, **kwargs):
        
        if not 'streamer' in resources:
            return json.dumps({'error' : 'no connection'})
        
        if not 'measures' in kwargs:
            return json.dumps[{ 'missing' : 'measures'}]
        
        measures = set(kwargs['measures'].replace('+',' ').split(','))
        data_types = resources['simulator'].get_data_types()
        valid_requested_types = measures & data_types
        if len(valid_requested_types) > 0:
            # start streaming
            # the list order is important, client is notified of the order in which data shall be sent
            send_list = list(valid_requested_types)
            self.configure_sender(resources['simulator'], send_list, resources['streamer'])
            return json.dumps({'subscribed' : send_list})
        else:
            return json.dumps({'missing' : 'valid measures'})
        
    # mapping the request pattern types to handler functions
    service_map = {'/' : get_name, '/name' : get_name, '/data' : list_data, '/connect' : open_conn, 
                   '/subscribe' : set_send_data, '/disconnect' : close_conn}
    
    def configure_sender(self, simulator, data_types, streamer):
        if 'sender' in resources and resources['sender']:
            resources['sender'].set_data(data_types)
        else:
            sender = Sender(simulator, data_types, streamer)
            resources['sender'] = sender
            sender.send_data()
    
class Sender:
    def __init__(self, simulator, data_types, streamer):
        self.simulator = simulator
        self.streamer = streamer
        self.data_types = data_types
        self.send_rate = simulator.update_rate()
        self.is_stopped = False
        
    def stop(self):
        self.is_stopped = True
        
    def set_data(self, data_types):
        self.data_types = data_types
        
    def send_data(self):
            sender_thread = Thread(target = self.send_loop)
            sender_thread.setDaemon(True)
            sender_thread.start()
                
    
    def send_loop(self):
        while self.is_stopped == False:
            time.sleep(self.send_rate)
            next_measures = self.simulator.get_data(self.data_types)
            out_data = []
            for data_type in self.data_types:
                out_data.append(next_measures[data_type])
            self.streamer.stream_nums(out_data)

class AngelSimulatorService:
    
    def run(self, filename, name, rate, port):
    
        hostname = 'localhost'

        f = open(filename, 'r')
        xml_data = f.read()
        data = xml_reader.read_simulator_data(xml_data)             
        resources['simulator'] = AngelSimulator(data, name, rate)
    
        handler = AngelSimulatorHTTPRequestHandler
        httpd = socketserver.TCPServer((hostname, port), handler)
    
    
        print ("serving at port", port)
        httpd.serve_forever()