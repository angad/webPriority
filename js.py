'''
Created on Jul 5, 2012

@author: angadsingh
'''
import jsparser
from collections import defaultdict

class Visitor(object):

    CHILD_ATTRS = ['thenPart', 'elsePart', 'expression', 'body', 'initializer']

    def __init__(self, filepath):
        self.filepath = filepath
        #List of functions by line # and set of names
        self.functions = defaultdict(set)
        with open(filepath) as myFile:
            self.source = myFile.read()

        self.root = jsparser.parse(self.source, self.filepath)
        self.visit(self.root)


    def look4Childen(self, node):
        for attr in self.CHILD_ATTRS:
            child = getattr(node, attr, None)
            if child:
                self.visit(child)

    def visit_NOOP(self, node):
        pass

    def visit_FUNCTION(self, node):
        # Named functions
        if node.type == "FUNCTION" and getattr(node, "name", None):
            print str(node.lineno) + " | function " + node.name + " | " + self.source[node.start:node.end]


    def visit_IDENTIFIER(self, node):
        # Anonymous functions declared with var name = function() {};
        try:
            if node.type == "IDENTIFIER" and hasattr(node, "initializer") and node.initializer.type == "FUNCTION":
                print str(node.lineno) + " | function " + node.name + " | " + self.source[node.start:node.initializer.end]
        except Exception as e:
            pass

    def visit_PROPERTY_INIT(self, node):

        # Anonymous functions declared as a property of an object
        try:
            if node.type == "PROPERTY_INIT" and node[1].type == "FUNCTION":
                print str(node.lineno) + " | function " + node[0].value + " | " + self.source[node.start:node[1].end]
        except Exception as e:
            pass


    def visit(self, root):

        call = lambda n: getattr(self, "visit_%s" % n.type, self.visit_NOOP)(n)
        call(root)
        self.look4Childen(root)
        for node in root:
            self.visit(node)

filepath = r"/Users/angadsingh/w.js"
outerspace = Visitor(filepath)