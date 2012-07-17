'''
@author: angadsingh
'''
from HTMLParser import HTMLParser
import urllib
from operator import itemgetter
from argparse import ArgumentParser
from HTTPHeader import headerBuilder
import json
import urlparse
import unicodedata

parser = ArgumentParser(description="Web Page Parser")
parser.add_argument('--url', '-u',
                    dest="url",
                    action="store",
                    help="URL",
                    required=True)

args = parser.parse_args()

def change_img_priority(h,w, old_priority):    
    
    WIDTH_AVG = 250
    HEIGHT_AVG = 250
    PRIORITY_ADJUST = .5
    
    # compare area to avg area, if much higher, lower adjust priority
    # by PRIORITY_ADJUST
 
    w = float(w)
    h = float(h)    
 
    
    if( (h!= 0) and (w!= 0) ):
        
        area_ratio = (w*h)/(WIDTH_AVG * HEIGHT_AVG)
        
        if ( area_ratio > 1.25):
            # have large image
            new_priority = old_priority - PRIORITY_ADJUST
        elif (area_ratio < .75):
            new_priority = old_priority + PRIORITY_ADJUST
        else:
            new_priority = old_priority
    else:
        new_priority = old_priority
    
    #print "height. width, priority are %f, %f, %f " %(h,w,new_priority)
    
        
    return new_priority











class PagePriority(HTMLParser):
    
    elements = []
    SCRIPT = 1
    STYLESHEET = 2
    IMAGE = 3
    EMBED = 4
    IFRAME = 5
    
    def handle_starttag(self, tag, attrs):
        # external stylesheets and icons from <link>
        if(tag == 'link'):
#            import pdb; pdb.set_trace()
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
                # sandeep edit    
                
                if(tag == 'img'):
                    w = 0.
                    h = 0.
                    for att in attrs:
                        if(att[0] == 'width'):
                            w = att[1]
                        
                        if(att[0] == 'height'):
                            h = att[1]
 
                        
                    
                    img_priority = change_img_priority(w,h,self.IMAGE)
#                    print tag + ", Img Priority: "
#                    print img_priority
                    
                        
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
        self.elements.sort(key=itemgetter(0))
        for element in self.elements:
            print element
            count += 1
        print 'Number of Elements: ' + str(count)
    
                
    def create_headers(self, outFile):
        default_hostname = urlparse.urlparse(args.url).hostname 
        count = 0
        json_elements = []
        self.elements.sort(key=itemgetter(0))
        for element in self.elements:
            #print element
            url = [a[1] for a in element if a[0] == 'href' or a[0] == 'src']
            if len(url) is not 0:
                url = url[0].encode('ascii', 'ignore')
                url_parsed = urlparse.urlparse(url)
                hostname = url_parsed.hostname
                if hostname is None:
                    url = "http:// " + default_hostname + url
                priority = [a[1] for a in element if a[0] == 'priority']
                priority = priority[0]
                get_request = headerBuilder.construct(url)
                json_element = {'id': count,  'priority': priority, 
                                "request": get_request}
                json_elements.append(json_element)
                count += 1

        json_content = json.dumps(json_elements)
        print json_content
        outFile.write(json_content)            
        print 'Number of Requests: ' + str(count)

def main():
    parser = PagePriority()
    f = urllib.urlopen(args.url)
    s = f.read()
    f.close()
    s = s.decode('utf-8')
    parser.feed(s)

    # parser.print_list()
    outFile = open('requests', 'w')
    parser.create_headers(outFile)
    outFile.close()

if __name__ == '__main__':
    main()
