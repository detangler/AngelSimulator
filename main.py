import sys
from server.service import AngelSimulatorService

if __name__ == "__main__":
    args = sys.argv[1:]
    args_dict = {}
    for arg in args:
        parts = arg.split('=')
        args_dict[parts[0]] = parts[1]
    
    # check for optional arguments
    name = args_dict.get('name', 'AngelSimulatorService')
    port = int(args_dict.get('port', '9080'))
    infile = args_dict.get('file', 'sim_data.xml')
    rate = int(args_dict.get('rate', '5')) # in seconds

    srv = AngelSimulatorService()
    srv.run(infile, name, rate, port)