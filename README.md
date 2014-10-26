RIPE-Trace
==========

Mass traceroute using RIPE API

Python code to start a RIPE Atlas UDM (User-Defined
Measurement) and display new and archived data.
This one is for running IPv4 or IPv6 traceroute queries
to analyze routing

You'll need an API key in ~/.atlas/auth.

New:
 - displays human readable results.
 - can call archived measurements

*Credit to the RIPE community for writing the core of this code*
*Modified by Thomren Boyd*


Usage: ripe_trace.py target-IP-address
Options are:
    -v 		--verbose 		: makes the program more talkative
    -h 		--help 			: this message
    -c 2LTRCODE --country=2LTRCODE	: limits the measurements to one country (default is world-wide)
    -a AREACODE --area=AREACODE 	: limits the measurements to one area such as North-Central (default is world-wide)
    -n ASnumber --asn=ASnumber 		: limits the measurements to one AS (default is all ASes)
    -o MSMID 	--old_measurement MSMID : uses the probes of measurement #MSMID
    -r N 	--requested=N 		: requests N probes (default is 5)
    -p X 	--percentage=X 		: stops the program as soon as X % of the probes reported a result (default is 0.90)
    -s   	--show 			: displays measurement results upon completion.
    -m MSMID	--archive=MSMID 	: displays results of measurement #MSMID
    
