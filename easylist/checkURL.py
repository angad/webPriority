'''
@author:angadsingh
'''

import re, sys

class AdBlockParser():
    
    whitelist = []
    blacklist = []

    count = 0
    blank_count = 0

    # BLOODY REGEX FOR REGEX
    # !  - comments, ignore
    # #  - element hiding, ignore
    # @@ - whitelist
    # |  - begins with
    # || - begins with https?://w?w?w?\d?.?
    # ^(ends with) - ends with a separator (?, /, :)
    # replace . with \.
    # replace ? with \?

    COMMENT = re.compile(r"^!")
    HIDDEN = re.compile(r"^\#\#[^#]")
    WHITELIST = re.compile(r"^@@")
    DOUBLEPIPE = re.compile(r"^\|\|")
    SINGLEPIPE = re.compile(r"^\|[^\|]")
    ENDPIPE = re.compile(r"\|$")
    ENDCARET = re.compile(r"\^$")
    QUESTIONMARK = re.compile(r"\?")
    DOT = re.compile(r"\.")
    BACKSLASH = re.compile(r"\\")
    FORWARDSSLASH = re.compile(r"/")
    DOMAIN = re.compile(r"^\^https\?:\/\/w\?w\?w\?\\d\?.?")
    
    all = open("all_filters.txt", "w")

    def parse_filter(self, filename):
        adFile = open(filename, "r")
        filters = adFile.readlines()
        
                
        for f in filters:
            self.count +=1
#            self.all.write(f)
            
            comments = re.match(self.COMMENT, f)
            hidden = re.match(self.HIDDEN, f)
            type = ""
            
            if hidden or comments:
                self.blank_count +=1
                type = "none"
                continue

            if "$" in f:
                f = f.split("$")[0] + '\n'
                
            f = re.sub(self.DOT, "\.", f)
            f = re.sub(self.QUESTIONMARK, "\?", f)
            f = re.sub(self.ENDCARET, "[\?\/:]", f)
            f = re.sub(self.ENDPIPE, "$", f)
            f = re.sub(self.SINGLEPIPE, "^", f)
            f = re.sub(self.DOUBLEPIPE, "^https?://w?w?w?\d?\.?", f)

            whitelist = re.match(self.WHITELIST, f)
            domain = re.match(self.DOMAIN, f)

#                print "none"
            if whitelist:
                self.whitelist.append(f)
                type = "whitelist"
                self.all.write(type + ": " + f)
#                print "whitelist"
            elif domain:
                self.blacklist.append(f)
                type = "blacklist"
                self.all.write(type + ": " + f) 
#                print "domain"
            else:
#                self.blacklist.append(f)
                type = "unknown"
#                print "blacklist"
            
            

    
    def check_if_ad(self, url):
        for f in self.blacklist:
            print f
            t = re.match(f, url)
            if t:
                print t.group(0)
    
def main():
    parser = AdBlockParser()
    files = ["easylist/easylist_adservers.txt",
             "easylist/easylist_general_block.txt",
             "easylist/easylist_general_hide.txt",
             "easylist/easylist_specific_block.txt",
             "easylist/easylist_specific_hide.txt",
             "easylist/easylist_thirdparty.txt",
             "easylist/easylist_whitelist.txt"]
    for f in files:
        parser.parse_filter(f)
        
    print "Whitelist: " + str(len(parser.whitelist)) + " Bytes: " + str(sys.getsizeof(parser.whitelist))
    print "Blacklist: " + str(len(parser.blacklist)) + " Bytes: " + str(sys.getsizeof(parser.blacklist))
    print "Total: " + str(parser.count)
    print "Blank: " + str(parser.blank_count)
    
#    url = "http://101m3.com"
#    parser.check_if_ad(url)
    
if __name__ == '__main__':
    main()
