'''
@author: angad, chinch
'''

from HTMLParser import HTMLParser
import urllib
from operator import itemgetter
from argparse import ArgumentParser
from HTTPHeader import headerBuilder
from easylist import easylistParser
import json
import urlparse
import os, re

parser = ArgumentParser(description="Web Elements Priority Generator")

parser.add_argument('--url', '-u',
                    dest="url",
                    action="store",
                    help="URL",
                    default=False)

parser.add_argument('--sort', '-s',
                    dest="sort",
                    action='store_true',
                    help="Sort By priority",
                    default=False)

parser.add_argument('--file', '-f',
                    dest="url_list_file",
                    action='store',
                    help="URL file name",
                    default=False)

parser.add_argument('--ad', '-a',
                    dest="ad",
                    action='store_true',
                    help="Check resources for Ads",
                    default=False)


args = parser.parse_args()

def purge(direc, pattern):
    for f in os.listdir(direc):
        if re.search(pattern, f):
            os.remove(os.path.join(direc, f))

class PagePriority(HTMLParser):
    
    elements = []
    SCRIPT = 1
    STYLESHEET = 2
    IMAGE = 3
    EMBED = 4
    IFRAME = 5
    AD = 6
    
    def change_img_priority(self, h, w, old_priority):
    
        WIDTH_AVG = 250
        HEIGHT_AVG = 250
        PRIORITY_ADJUST = 1
        
        # compare area to avg area, if much higher, lower adjust priority
        # by PRIORITY_ADJUST 
        w = float(w)
        h = float(h)    
        
        if( (h!= 0) and (w!= 0) ):
            area_ratio = (w*h)/(WIDTH_AVG * HEIGHT_AVG)
            if ( area_ratio > 1.25):
                # a large image, thus priority remains the same
                new_priority = old_priority
            elif (area_ratio < .75):
                # small image, priority numeric value increased
                new_priority = old_priority + PRIORITY_ADJUST
            else:
                new_priority = old_priority
        else:
            new_priority = old_priority
        return new_priority
    
    
    def handle_starttag(self, tag, attrs):
        # external stylesheets and icons from <link>
        if(tag == 'link'):
            for attr in attrs:
                if(attr[1] == 'stylesheet'):
                    self.add_element(tag, self.STYLESHEET, attrs)
                    return
                if(attr[1] == 'icon'):
                    self.add_element(tag, self.IMAGE, attrs)
                    return
                    
                    
        # object, embed tag used for flash players
        if(tag == 'embed' or tag == 'object'):
            attrs.insert(0, ('tag', tag))
            self.add_element(tag, self.EMBED, attrs)
            return
        
        # iframe used for advertisements
        if(tag == 'iframe'):
            self.add_element(tag, self.IFRAME, attrs)
            return
        
        # external stylesheets, scripts and 
        # images using 'src' attribute
        for attr in attrs:
            if(attr[0]=='src'):
                if(tag == 'script'):
                    self.add_element(tag, self.SCRIPT, attrs)
                if(tag == 'img'):
                    w = 0.
                    h = 0.
                    for att in attrs:
                        if(att[0] == 'width'):
                            w = att[1]
                        if(att[0] == 'height'):
                            h = att[1]
                    img_priority = self.change_img_priority(w, h, self.IMAGE)
                    self.add_element(tag, img_priority, attrs)
                return
    
    def add_element(self, tag, priority, attrs):
        attrs.insert(0, ('tag', tag))
        attrs.insert(0, ('priority', priority))
        self.elements.append(attrs)
    
    def handle_endtag(self, tag):
        pass
    
    def handle_data(self, data):
        pass
    
    def print_list(self):
        count = 0
        if args.sort:
            self.elements.sort(key=itemgetter(0))
        for element in self.elements:
            print element
            count += 1
        print 'Number of Elements: ' + str(count)
    
    def create_headers(self, outFile, base_url):
        ads = easylistParser.EasyListParser()
        ads.start()
        count = 0
        json_elements = []
        
        # sort by priority
        if args.sort:
            self.elements.sort(key=itemgetter(0))
        
        for element in self.elements:
            url = [a[1] for a in element if a[0] == 'href' or a[0] == 'src']
            # check if the URL is valid
            if len(url) is not 0:
                url = url[0].encode('ascii', 'ignore')
                url_parsed = urlparse.urlparse(url)
                hostname = url_parsed.hostname
                if hostname is None: # its a relative url
                    url = "http:// " + base_url + url
                
                # check for duplicate url
                flag = 0
                for e in json_elements:
                    if e['url'] == url:
                        flag = 1    
                if flag == 1:
                    continue

                # get the priority
                priority = [a[1] for a in element if a[0] == 'priority']
                priority = priority[0]
                
                # construct the get request for the URL
                get_request = headerBuilder.construct(url)
                
                # construct a JSON row
                json_element = {'id': count,  'priority': priority,
                                "request": get_request, 'url': url}
                json_elements.append(json_element)
                count += 1


        if(args.ad):
            print "Checking each URL for ad. This is gonna be slow :("
            ads.adjustPriority(json_elements)
        json_content = json.dumps(json_elements)
        
#        print json_content
        outFile.write(json_content)
        print 'Number of Requests: ' + str(count)
        self.elements = []

def main():
    direc = os.path.dirname(os.path.realpath(__file__))
    purge(direc, r'(.*).com(\.*)')
    purge(direc, r'(.*)request(\.*)')

    url_id = 0
    parser = PagePriority()
    
    if (args.url != False):
        f = urllib.urlopen(args.url)
        s = f.read()
        f.close()
        s = s.decode('utf-8')
        parser.feed(s)
        # parser.print_list()
        url = args.url
        # create a new requests file
        url = re.sub("http://", "", url)
        url = re.sub("www.", "", url)
        url = re.sub("(\/)", "-", url)
        file_name = "request 0 " + url + ".txt"
        
        outFile = open(file_name, 'w')
        base_url = urlparse.urlparse(url).hostname
        parser.create_headers(outFile, base_url)
        outFile.close()
    
    if(args.url_list_file != False):
        for line in open(args.url_list_file, 'r'):

            # call the parser on this url
            f = urllib.urlopen(line)
            s = f.read()
            f.close()
            s = s.decode('utf-8')
            parser.feed(s)
            
            # create a new requests file            
            url_parsed = urlparse.urlparse(line)
            host = url_parsed.hostname

            line = re.sub("http://", "", line)
            line = re.sub("www.", "", line)
            line = re.sub("(\/)", "-", line)
            file_name = "request " + str(url_id) + " " + line + ".txt"
            
            outFile = open(file_name, 'w')
            parser.create_headers(outFile, host)
            outFile.close()
            url_id += 1


if __name__ == '__main__':
    main()
