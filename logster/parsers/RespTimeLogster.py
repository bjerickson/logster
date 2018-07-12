'''
Calculates the average response time of a given apache host

The parser is specific to our apache log lines and relies on syslog-ng for the hostname of the apache server. Logging
to a central log server for apache, we add the hostname to the log. The last element of the log line is time taken in
microseconds. You can adjust depending on the position of the time taken in your log line.  eg.

http://httpd.apache.org/docs/current/mod/mod_log_config.html
%D	The time taken to serve the request, in microseconds.

Log line sample

hostname.example.com   ... 17635
'''
import optparse
from logster.logster_helper import MetricObject, LogsterParser
from logster.logster_helper import LogsterParsingException


class RespTimeLogster(LogsterParser):

    def __init__(self, option_string=None):
        '''Initialize the data structures used by the parser. In our case we have a hash with the hostname as the key
        and the value is the response time in microseconds. '''
        self.metrics = {}
        if option_string:
            options = option_string.split(' ')
        else:
            options = []

        optparser = optparse.OptionParser()
        optparser.add_option('--log-filters', '-l', dest='filters', default='/cgi-bin/status.py,server-status',
                             help='Comma-separated list of filters to exclude: (default: "/cgi-bin/status.py,server-status"')

        opts, args = optparser.parse_args(args=options)
        self.filters = opts.filtes.split(',')

    def parse_line(self, line):
        '''Split the hostname and get the last element'''
        try:
            count=0
            for filter in self.filters:
                if filter in line:
                    count=1
            if count == 0:
                line_split = line.split('\t')
                hostname = line_split[0]
                time_taken_microseconds = float(line_split[len(line_split)-1])

                if hostname in self.metrics:
                    total_time_taken = self.metrics[hostname]['total_time_taken']
                    total_time_taken += time_taken_microseconds
                    count = self.metrics[hostname]['count']
                    count += 1
                    self.metrics[hostname] = {'total_time_taken': total_time_taken, 'count': count}
                else:
                    self.metrics[hostname] = {'total_time_taken': time_taken_microseconds, 'count': 1}
        except Exception as e:
            raise LogsterParsingException("Unable to parse {}".format(line))

    def get_state(self, duration):
        metric_objects = []

        for metric in self.metrics:
            hostname = metric
            total_time_taken = self.metrics[metric]['total_time_taken']
            count = self.metrics[metric]['count']
            total_time_taken_milliseconds = self._microseconds_to_milliseconds(total_time_taken)
            #Drop the decimals, not needed for our metrics
            avg_time_taken_milliseconds = int((total_time_taken_milliseconds / count))
            metric_objects.append(MetricObject(hostname, avg_time_taken_milliseconds, "apache_avg_resp_time"))

        return metric_objects

    def _microseconds_to_milliseconds(self, number):
        return (number/1000)
