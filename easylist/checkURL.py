'''
@author:angadsingh
'''

def check_if_ad(url):
    adFile = open("easylist/easylist_adservers.txt")
    t = adFile.read()
    print t

def main():
    url = ""
    check_if_ad(url)
    
if __name__ == '__main__':
    main()
