from logster.logster_helper import LogsterOutput
from logster.logster_helper import LogsterParsingException
import signalfx


class SignalfxOutput(LogsterOutput):
    shortname = 'signalfx'

    @classmethod
    def add_options(cls, parser):
        parser.add_option('--signalfx-token', action='store',
                          help='Signalfx token, used to connect to the signalfx api')
        parser.add_option('--signalfx-metric-type', action='store',
                          help='Metric type to send to signalfx. eg. guage, counter')

    def __init__(self, parser, options, logger):
        super(SignalfxOutput, self).__init__(parser, options, logger)
        if not options.signalfx_token:
            parser.print_help()
            parser.error("You must supply --signalfx-token when using 'signalfx as your output source")
        if not options.signalfx_metric_type:
            self.signalfx_metric_type = 'gauge'
        else:
            self.signalfx_metric_type = options.signalfx_metric_type

        self.signalfx_host = options.signalfx_host
        self.signalfx_token = options.signalfx_token

    def submit(self, metrics):


        if (not self.dry_run):
            sfx = signalfx.SignalFx().ingest(self.signalfx_token)

        for metric in metrics:
            hostname = self.get_metric_name(metric)
            metric_value = metric.value
            metric_units = metric.units

            sfx_data = [
                {
                    'metric': metric_units,
                    'value': metric_value,
                    'dimensions': {
                        'host': hostname
                    }
                }
            ]

            if (not self.dry_run):
                try:
                    if (self.signalfx_metric_type == 'gauge'):
                        sfx.send(
                            gauges = sfx_data
                        )
                    if (self.signalfx_metric_type == 'counter'):
                        sfx.send(
                            counters = sfx_data
                        )
                except Exception as e:
                    raise LogsterParsingException("Unable to send metric: {}".format(sfx_data))
                finally:
                    sfx.stop()
            else:
                print("Hostname: {}, Metric Name: {}, Metric Value: {}".format(hostname, metric_units, metric_value))
