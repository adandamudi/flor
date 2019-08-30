import sys
import ast

nodeInfoTable = {}

def main():
    if len(sys.argv) < 2:
        raise Exception("Please specify the name of the test file.")

    for i in range(1, len(sys.argv)):
        print("The test file name is " + sys.argv[i] + " .....")
        with open("./tests/" + sys.argv[i], "r") as source:
            tree = ast.parse(source.read())
        CustomNodeVisitor().visit(tree)

def isRandCall(node):
    "Determines if the called function has non-determinism."
    return False

class CustomNodeVisitor(ast.NodeVisitor):
    ###########################################################################
    ##### 				         Statement visit methods	   		 	  #####
    ###########################################################################
    def visit_Call(self, node):
        print("\n[[[...Call...]]]")
        print(node.__dict__)

        target_id = ""
        for fieldname, fieldvalue in ast.iter_fields(node):
            print(fieldname, fieldvalue)

            if fieldname == "func":
                if type(fieldvalue) == ast.Name:
                    target_id = fieldvalue.id + "@" + str(fieldvalue.lineno) \
                                + "_" + str(fieldvalue.col_offset)
                elif type(fieldvalue) == ast.Attribute:
                    target_id = fieldvalue.attr + "@" + str(fieldvalue.lineno) \
                                + "_" + str(fieldvalue.col_offset)
            elif fieldname == "args":
                for arg in fieldvalue:
                    self.visit(arg)
            elif fieldname == "keywords":
                for keyword in fieldvalue:
                    self.visit(keyword)

        nodeInfoTable[target_id] = True if isRandCall(node) else False


if __name__ == "__main__":
    main()
    print("Here is the static analysis info:")
    print(nodeInfoTable)