'''
@author: angad
'''

import urllib2
import urlparse

def add_header(send, header, value):
    # if its the end of the request, then append \r\n
    if(header == None and value == None):
        send += '\r\n'
    # error cases
    elif(header == None and value != None):
        print "Error"
    elif(header != None and value == None):
        print "Error"
    else:
        # add header : value \r\n
        send += header + ": " + value + '\r\n'
    return send

def construct(url, default_host=None, user_agent=None, accept=None, 
              accept_lang=None, accept_encoding=None, connection=None):
    
    if url is None or url is '':
        return 'Error: Invalid URL'
    # if the values are not set, use default values
    if user_agent is None:
        user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:13.0) Gecko/20100101 Firefox/13.0.1'
    if accept is None:
        accept = '*/*'
    if accept_lang is None:
        accept_lang = 'en-us,en;q=0.5'
    if accept_encoding is None:
        accept_encoding = 'gzip, deflate'
    if connection is None:
        connection = 'keep-alive'
        
    # get host name
    url_parsed = urlparse.urlparse(url)
    host = url_parsed.hostname
    if host is None:
        host = default_host
    
    # get path of the element relative to the host name
    path = url_parsed[2]
    
    # construct the header
    send = 'GET ' + path + ' HTTP/1.1\r\n'
    send = add_header(send, 'Host', host)
    send = add_header(send, 'User-Agent', user_agent)
    send = add_header(send, 'Accept', accept)
    send = add_header(send, 'Accept-Language', accept_lang)
    send = add_header(send, 'Accept-Encoding', accept_encoding)
    send = add_header(send, 'Connection', connection)
    send = add_header(send, None, None) #end
    return send

def main():
    url = 'http://techcrunch.com/2012/07/12/bing-fund-microsoft-launches-its-own-angel-fund-and-incubator-program/'
    print construct(url)

    # Sample header test
#    req = urllib2.Request(url)
#    req.add_header('User-Agent', user_agent)
#    req.add_header('Accept-Encoding', accept_encoding)
#    req.add_header('Host', host)
#    print req.headers

#    opener = urllib2.build_opener(urllib2.HTTPHandler(debuglevel=1))
#    opener.open('http://techcrunch.com/2012/07/12/bing-fund-microsoft-launches-its-own-angel-fund-and-incubator-program/')


if __name__ == '__main__':
    main()
