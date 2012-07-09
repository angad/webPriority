'''
@author: angadsingh
'''
from HTMLParser import HTMLParser
import urllib
from operator import itemgetter

"""
TODO: 
Parse Javascript for external content (embed, object)
Parse CSS for background images
"""

class PagePriority(HTMLParser):
    
    elements = []
    SCRIPT = 1
    STYLESHEET = 2
    IMAGE = 3
    EMBED = 4
    IFRAME = 5
    
    def handle_starttag(self, tag, attrs):
        #import pdb; pdb.set_trace()    
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
                    self.add_element(tag, self.IMAGE, attrs)
                return
            
    
    def add_element(self, tag, priority, attrs):
        attrs.insert(0, ('tag', tag))
        attrs.insert(0, ('priority', priority))
        self.elements.append(attrs)

    def handle_endtag(self, tag):
        pass
    
    def handle_data(self, data):
#        print data
        pass
    
    def print_list(self):
        self.elements.sort(key=itemgetter(0))
        for element in self.elements:
            print element

def main():
    parser = PagePriority()
    f = urllib.urlopen("http://techcrunch.com")
    s = f.read()
    f.close()
    
    parser.feed(s)
    parser.print_list()

if __name__ == '__main__':
    main()