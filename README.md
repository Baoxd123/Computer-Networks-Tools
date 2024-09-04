# Computer-Networks-Tools
This repository includes some computer networks tools from UGA computer networks course projects.

Traceroute tool usage: trstats.py [-h] [-n NUM_RUNS] [-d RUN_DELAY] [-m MAX_HOPS]
                    -o OUTPUT -g GRAPH [-t TARGET] [--test TEST_DIR]

Run traceroute multiple times towards a given target host

optional arguments:
  -h, --help       show this help message and exit
  -n NUM_RUNS      Number of times traceroute will run
  -d RUN_DELAY     Number of seconds to wait between two consecutive runs
  -m MAX_HOPS      Number of max hops per traceroute run
  -o OUTPUT        Path and name of output JSON file containing the stats 
  -g GRAPH         Path and name of output PDF file containing stats graph
  -t TARGET        A target domain name or IP address (required if --test 
                   is absent)
  --test TEST_DIR  Directory containing num_runs text files, each of which
                   contains the output of a traceroute run. If present, this
                   will override all other options and traceroute will not be
                   invoked. Stats will be computed over the traceroute output
                   stored in the text files

Example for how to produce the test directory and files to be used with the --test command line option:

$ mkdir test_files; N=5; for i in $(seq $N); do traceroute -m 10 www.google.com > test_files/tr_run-$i.out; done 

After running your traceroute wrapper program, write a similar program to run ping, instead of traceroute:




Ping tool usage: pingstats.py [-h] [-m MAX_PINGS] [-d DELAY] [-m MAX_HOPS]

Run ping towards a given target host

optional arguments:
  -h, --help       show this help message and exit
  -d DELAY         Number of seconds to wait between two consecutive ping packets
  -m MAX_PINGS     Number of max ping packets to send
  -o OUTPUT        Path and name of output JSON file containing the stats 
  -g GRAPH         Path and name of output PDF file containing stats graph
