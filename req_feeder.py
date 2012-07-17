#!/usr/bin/env python
import sys
import getopt
import json
import socket

# Basic script to read json file and feed this
# output to another program via a TCP connection.

##Print usage guide
def usage():
    """Display usage
    """
    print "Usage "+sys.argv[0]+" [options] filename"
    print "\tRequest feeder"
    print  "Options:"
    print "-h/--help\n\tPrint this usage guide"
    print "--proxy\n\tSpecify proxy [Default: localhost]"
    print "-p/--port\n\tSpecify port [Default: 8080]"

if __name__ == "__main__":
    #Get options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hp:",
                                   ["help","proxy","port"])
    except getopt.GetoptError:
        print "Option error!"
        usage()
        sys.exit(2)

    proxy = "localhost"
    port = 8080
    for opt,arg in opts:
        if (opt in ("-h","--help")):
            usage()
            sys.exit(0)
        elif (opt in ("-p","--port")):
            port = int(arg)
        elif (opt in ("--proxy")):
            proxy = arg
        else:
            print "Unhandled option :"+opt
            sys.exit(2)

    if (len(args) < 1):
        usage()
        sys.exit(2)

    filename = args[0]

    #Read
    fileRef = open(filename)
    content = json.load(fileRef)
    fileRef.close()

    #Open socket and send requests
    print "Feeding %i requests from %s to %s:%i..." % (len(content),
                                                       filename,
                                                       proxy,
                                                       port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((proxy, port))
    except socket.error as err:
        print "Socket failed: [%i] %s" % (err.errno, err.strerror)
        sys.exit(1)

    
    sock.close()


