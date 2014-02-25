Content
--------
This file contains instructions on using AngelSimulator

Running the server:
-----------------

simply invoke main.py through the interpreter
this starts a HTTP server which serves the following requests:

* detect - returns the simulator name
* data - returns available measures
* connect host=<hostname> port=<port> - sets up a connection with a socket specified by the parameters, to which data is sent
* subscribe measures=<measure1>+<measure2>+...+<measure n> - subscribes to accepting measures of types specified by the parameters
* disconnect - closes the connection

the main module accepts 4 optional command line arguments: (default)
port=<port> (9080) - the port on which the http server is launched
file=<path> (./sim_data.xml) - the data file from which measures are read
name=<name> (AngelSimulator) - the device name displayed when invoking detect
rate=<rate> (5) - the rate at which data is sent, in seconds

Sample Client
-------------
this package also contains a sample client, showing simulator usage
the client is located at client/sample_simulator_client.py and is an interactive command line app
the client has a help option stating available commands, and should typically be used as follows:
(optional) detect - checks if a simulator exists
connect - connects to the simulator
subscribe <type1>, <type2>,... - chooses what measures to receive

and now the client should retrieve data and print it to the display

Known Issues
-------------
It seems that connecting for the seconds time after disconnect was invoked prevents the cleint from receiving data
The client is prone to crashes when simulator address is not properly configured