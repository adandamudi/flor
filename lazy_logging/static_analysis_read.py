import sys
import ast

importLibs = {}
whitelistedFunc = set()
nodeInfoTable = {}


def main():
    if len(sys.argv) < 2:
        raise Exception("Please specify the name of the test file.")

    # Loads all the whitelisted functions from the libraries of interests.
    # Each library has its own sub-file that specifies its whitelisted functions.
    # These sub-file names are specified in whitelisted/whitelisted_func.txt
    get_whitelisted_func("./whitelisted/whitelisted_func.txt")

    for i in range(1, len(sys.argv)):
        print("The test file name is " + sys.argv[i] + " .....")
        with open("./tests/" + sys.argv[i], 'r') as source:
            tree = ast.parse(source.read())
        CustomNodeVisitor().visit(tree)


def get_whitelisted_func(filename):
    with open(filename, 'r') as fp:
        subfilename = fp.readline().strip()
        with open("./whitelisted/" + subfilename, 'r') as sp:
            func_name = sp.readline().strip()
            while func_name:
                whitelistedFunc.add(func_name[:func_name.index('(')])
                func_name = sp.readline().strip()
            sp.close()
    fp.close()


class CustomNodeVisitor(ast.NodeVisitor):
    ###########################################################################
    ##### 				         Statement visit methods	   		 	  #####
    ###########################################################################

    def visit_Import(self, node):
        # print("\n[[[...Import...]]]")
        # print(node.__dict__)

        for fieldname, fieldvalue in ast.iter_fields(node):
            if fieldvalue[0].asname is not None:
                importLibs[fieldvalue[0].asname] = fieldvalue[0].name
            else:
                importLibs[fieldvalue[0].name] = fieldvalue[0].name

    def visit_ImportFrom(self, node):
        # print("\n[[[...Import From...]]]")
        # print(node.__dict__)

        name = ""
        for fieldname, fieldvalue in ast.iter_fields(node):
            if fieldname == "module":
                name += fieldvalue
            elif fieldname == "names":
                name += "." + fieldvalue[0].name
                if fieldvalue[0].asname is not None:
                    importLibs[fieldvalue[0].asname] = name
                else:
                    importLibs[name] = name


    def visit_Call(self, node):
        # print("\n[[[...Call...]]]")
        # print(node.__dict__)

        func_name = ""

        for fieldname, fieldvalue in ast.iter_fields(node):
            if fieldname == "func":
                # The fieldvalue can either be an ast.Attribute or ast.Name
                # You either have Attribute.value or Name.id
                while type(fieldvalue) is ast.Attribute:
                    func_name = fieldvalue.attr if func_name == "" else fieldvalue.attr + "." + func_name
                    fieldvalue = fieldvalue.value
                if type(fieldvalue) is ast.Name:
                    func_name = fieldvalue.id + "." + func_name if func_name != "" else fieldvalue.id

                expanded = ""

                if "." in func_name:
                    i = func_name.index(".")
                    if func_name.split(".")[0] in importLibs.keys():
                        expanded = importLibs[func_name.split(".")[0]]

                expanded_func_name = expanded + "." + func_name[i+1:] if expanded is not "" else func_name

                if expanded_func_name is not "" and expanded_func_name not in whitelistedFunc:
                    target_id = func_name + "@" + str(fieldvalue.lineno) \
                                          + "_" + str(fieldvalue.col_offset)
                    nodeInfoTable[target_id] = True


if __name__ == "__main__":
    main()
    print("\nHere are the imported libraries:")
    print(importLibs)
    # print("\nHere are the whitelisted functions:")
    # print(whitelistedFunc)
    print("\nHere is the static analysis info:")
    print(nodeInfoTable)
