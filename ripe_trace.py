#!/usr/bin/python

""" Python code to start a RIPE Atlas UDM (User-Defined
Measurement) and display new and archived data in human readable format.
This one is for running IPv4 or IPv6 traceroute queries
to analyze routing

Now displays results.

You'll need an API key in ~/.atlas/auth.

*Credit to the RIPE community for writing the core of this code*
*Modified by Thomren Boyd*
"""

import json
import time
import os
import string
import sys
import time
import getopt
import socket
import urllib2

import RIPEAtlas

# Default values
country = None # World-wide
asn = None # All
area = None # World-wide
old_measurement = None
verbose = False
requested = 5 # Probes
protocol = "UDP"
percentage_required = 0.9
show_measurement = False

def is_ip_address(str):
    try:
        addr = socket.inet_pton(socket.AF_INET6, str)
    except socket.error: # not a valid IPv6 address
        try:
            addr = socket.inet_pton(socket.AF_INET, str)
        except socket.error: # not a valid IPv4 address either
            return False
    return True

def get_results(m_num):
    print '\nShowing results for MSMID #' + str(m_num)
    url = 'https://atlas.ripe.net/api/v1/measurement/'+ str(m_num) +'/result/'
    my_json =  json.loads(urllib2.urlopen(url).read())
    for my_trace in my_json:
        src_ip = my_trace["src_addr"]
	prb_id = my_trace["prb_id"]
        print "\nSource IP : " + str(src_ip) + "\tProbe ID  : " + str(prb_id)
        print "**** Hop Number : Hop IP : Avg RTT\n"
        for curr_hop in my_trace["result"]:
            hop_dict = dict()
            hop_rtt_dict = dict()
            hop_num = curr_hop["hop"]
            for result in curr_hop["result"]:
                if "x" in result:
                    hop_ip = "Timeout"
                    hop_rtt = 0
                else:
                    hop_ip = result["from"]
                    hop_rtt = result["rtt"]
                if hop_ip in hop_dict:
                    hop_dict[hop_ip] += 1
                    hop_rtt_dict[hop_ip] += float(hop_rtt)
                else:
                    hop_dict[hop_ip] = 1
                    hop_rtt_dict[hop_ip] = float(hop_rtt)
            hop_dict_flag = True
            for curr_ip in hop_dict:
                avgrtt = float(hop_rtt_dict[curr_ip]) / hop_dict[curr_ip]
                if hop_dict_flag == True:
                    print "**** {0} : {1} : {2}".format(hop_num,curr_ip,avgrtt)
                else:
                    print " \-- {0} : {1} : {2}".format(hop_num,curr_ip,avgrtt)
                hop_dict_flag = False
    print ''
    print 'Download json: ' + str(url)
		

def usage(msg=None):
    if msg:
        print >>sys.stderr, msg
    print >>sys.stderr, "Usage: %s target-IP-address" % sys.argv[0]
    print >>sys.stderr, """Options are:
    -v 		--verbose 		: makes the program more talkative
    -h 		--help 			: this message
    -c 2LTRCODE --country=2LTRCODE	: limits the measurements to one country (default is world-wide)
    -a AREACODE --area=AREACODE 	: limits the measurements to one area such as North-Central (default is world-wide)
    -n ASnumber --asn=ASnumber 		: limits the measurements to one AS (default is all)
    -o MSMID 	--old_measurement MSMID : uses the same probes of a previous measurement
    -r N 	--requested=N 		: requests N probes (default is %s)
    -p X 	--percentage=X 		: stops the program as soon as X %% of the probes reported a result (default is %2.2f)
    -s   	--show 			: displays measurement results upon completion
    -m MSMID	--archive=MSMID 	: displays results of a previous measurement
    """ % (requested, percentage_required)

try:
    optlist, args = getopt.getopt (sys.argv[1:], "r:c:a:n:o:t:p:m:vhs",
                               ["requested=", "country=", "area=", "asn=", "percentage=",
                                "protocol=", "old_measurement=", "verbose", "help", "show", "archive="])
    for option, value in optlist:
        if option == "--country" or option == "-c":
            country = value
        elif option == "--area" or option == "-a":
            area = value
        elif option == "--asn" or option == "-n":
            asn = value
        elif option == "--old_measurement" or option == "-o":
            old_measurement = value
        elif option == "--protocol" or option == "-t":
            if value.upper() != "UDP" and value.upper() != "ICMP":
                usage("Protocol must be UDP or ICMP")
                sys.exit(1)
            protocol = value.upper()
        elif option == "--percentage" or option == "-p":
            percentage_required = float(value)
        elif option == "--requested" or option == "-r":
            requested = int(value)
        elif option == "--verbose" or option == "-v":
            verbose = True
        elif option == "--help" or option == "-h":
            usage()
            sys.exit(0)
        elif option == "--show" or option == "-s":
            show_measurement = True
	elif option == "--archive" or option == "-m":
            msmid = value
	    get_results(msmid)
	    sys.exit(1)
        else:
            # Should never occur, it is trapped by getopt
            usage("Unknown option %s" % option)
            sys.exit(1)
except getopt.error, reason:
    usage(reason)
    sys.exit(1)

if len(args) != 1:
    usage()
    sys.exit(1)
target = args[0]
if not is_ip_address(target):
    print >>sys.stderr, ("Target must be an IP address, NOT AN HOST NAME")
    sys.exit(1)

data = { "definitions": [
           { "target": target, "description": "Traceroute %s" % target,
           "type": "traceroute", "is_oneoff": True, "protocol": protocol} ],
         "probes": [
             { "requested": requested} ] }
if country is not None:
    if asn is not None or area is not None or old_measurement is not None:
        usage("Specify country *or* area *or* ASn *or* old measurement")
        sys.exit(1)
    data["probes"][0]["type"] = "country"
    data["probes"][0]["value"] = country
    data["definitions"][0]["description"] += (" from %s" % country)
elif area is not None:
        if asn is not None or country is not None or old_measurement is not None:
            usage("Specify country *or* area *or* ASn *or* old measurement")
            sys.exit(1)
        data["probes"][0]["type"] = "area"
        data["probes"][0]["value"] = area
        data["definitions"][0]["description"] += (" from %s" % area)
elif asn is not None:
        if area is not None or country is not None or old_measurement is not None:
            usage("Specify country *or* area *or* ASn *or* old measurement")
            sys.exit(1)
        data["probes"][0]["type"] = "asn"
        data["probes"][0]["value"] = asn
        data["definitions"][0]["description"] += (" from AS #%s" % asn)
elif old_measurement is not None:
        if area is not None or country is not None or asn is not None:
            usage("Specify country *or* area *or* ASn *or* old measurement")
            sys.exit(1)
        data["probes"][0]["requested"] = 20 # Dummy value, anyway,
                                                # but necessary to get
                                                # all the probes
        # TODO: the huge value of "requested" makes us wait a very long time
        data["probes"][0]["type"] = "msm"
        data["probes"][0]["value"] = old_measurement
        data["definitions"][0]["description"] += (" from probes of measurement #%s" % old_measurement)
else:
    data["probes"][0]["type"] = "area"
    data["probes"][0]["value"] = "WW"
    
if string.find(target, ':') > -1:
    af = 6
else:
    af = 4
data["definitions"][0]['af'] = af
if verbose:
    print data

measurement = RIPEAtlas.Measurement(data)
print "Measurement #%s %s uses %i probes" % (measurement.id,
                                             data["definitions"][0]["description"],
                                             measurement.num_probes)

rdata = measurement.results(wait=True, percentage_required=percentage_required)
print("%s probes reported" % len(rdata))
print ("Test done at %s" % time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

if show_measurement:
    get_results(measurement.id)