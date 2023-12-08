#!/usr/bin/python3

from ebc import EBC, ChargeMode

def disconnect(e, args):
   e.disconnect()

def stop(e, args):
   e.stop()

def ccv(e, args):
   e.charge(ChargeMode.ccv, u=args.u, i=args.i, istop=args.cut)
   e.wait()


if __name__ == '__main__':
   from argparse import ArgumentParser
   arg = ArgumentParser(prog='EBC')
   arg.add_argument('--port', '-p', required=False, default='/dev/ttyUSB0')
   subparsers = arg.add_subparsers(dest='cmd')
   parser_ccv = subparsers.add_parser('ccv', help="Charge CV help")
   parser_ccv.add_argument('u', help="Target voltage (mV)", type=int)
   parser_ccv.add_argument('i', help="Target current (mA)", type=int)
   parser_ccv.add_argument('cut', help="Cut-off current (mA)", type=int)
   parser_ccv.add_argument('to', nargs='?', help="Timeout (minutes)", type=int)
   parser_ccv.set_defaults(func=ccv)
   parser_disconnect = subparsers.add_parser('disconnect', help="Disconnect")
   parser_disconnect.set_defaults(func=disconnect)
   parser_stop = subparsers.add_parser('stop', help="Stop")
   parser_stop.set_defaults(func=stop)
   args = arg.parse_args()
   e = EBC(args.port)
   e.connect()
   args.func(e, args)
