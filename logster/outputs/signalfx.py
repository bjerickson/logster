from logster.logster_helper import LogsterOutput
import re
import socket


class SignalfxOutput(LogsterOutput):
    shortname = 'signalfx'

    @classmethod
    def add_options(cls, parser):
        parser.add_option('--sigalfx-host', action='store',
                          help='Hostname and port for the signalfx proxy server, eg. signalfx.example.com:2033')
        parser.add_option('--signalfx-token', action='store',
                          help='Signalfx token, used to connect to the signalfx api')
        parser.add_option('--metric-type', action='store',
                          help='Metric type to send to signalfx. eg. guage, counter')

    def __init__(self, parser, options, logger):
        super(SignalfxOutput, self).__init__(parser, options, logger)
        if not options.signalfx_host:
            parser.print_help()
            parser.error("You musst supply --signalfx-host when useing 'signalfx' as an output type.")

    def submit(self, metrics):

        for metric in metrics:
            print(metric)