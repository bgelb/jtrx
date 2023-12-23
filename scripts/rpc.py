from argparse import ArgumentParser
from xmlrpc.client import ServerProxy

def argument_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "--phi", dest="phi", type=str, default=None,
        help="Set phi [default=%(default)r]")
    parser.add_argument(
        "--gain", dest="gain", type=str, default=None,
        help="Set gain [default=%(default)r]")
    return parser


options = argument_parser().parse_args()

xmlrpc_control_client = ServerProxy('http://'+'localhost'+':8080')
phi = xmlrpc_control_client.get_phi()
gain = xmlrpc_control_client.get_gain()
print ('old phi:', phi, 'gain:', gain)


if options.gain:
    xmlrpc_control_client.set_gain(float(options.gain))

if options.phi:
    xmlrpc_control_client.set_phi(float(options.phi))

phi = xmlrpc_control_client.get_phi()
gain = xmlrpc_control_client.get_gain()
print ('new phi:', phi, 'gain:', gain)
