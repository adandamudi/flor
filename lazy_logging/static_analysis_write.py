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
    def visit_FunctionDef(self, node):
        print("\n[[[...FunctionDef...]]]")
        print(node.__dict__)
        return False

    def visit_AsyncFunctionDef(self, node):
        print("\n[[[...AsyncFunctionDef...]]]")
        return False

    def visit_ClassDef(self, node):
        print("\n[[[...ClassDef...]]]")
        return False

    def visit_Return(self, node):
        print("\n[[[...Return...]]]")
        print(node.__dict__)

        if node.value is None:
            return False
        return self.visit(node.value)

    def visit_Delete(self, node):
        print("\n[[[...Delete...]]]")
        print(node.__dict__)
        return False

    def visit_Assign(self, node):
        print("\n[[[...Assign...]]]")
        print(node.__dict__)

        toLog = False
        target_ids = []
        for fieldname, fieldvalue in ast.iter_fields(node):
            if fieldname == "targets":
                for value in fieldvalue:
                    target_id = self.visit(value) + "@" + str(value.lineno) \
                                + "_" + str(value.col_offset)
                    target_ids.append(target_id)
            elif fieldname == "value":
                toLog = toLog or self.visit(fieldvalue)

        for target_id in target_ids:
            nodeInfoTable[target_id] = toLog

    def visit_AugAssign(self, node):
        print("\n[[[...AugAssign...]]]")
        print(node.__dict__)

        toLog = False
        target_id = None
        for fieldname, fieldvalue in ast.iter_fields(node):
            if fieldname == "target":
                target_id = self.visit(fieldvalue) + "@" + str(fieldvalue.lineno) \
                            + "_" + str(fieldvalue.col_offset)
            elif fieldname == "op":
                pass
            elif fieldname == "value":
                toLog = toLog or self.visit(fieldvalue)

        nodeInfoTable[target_id] = toLog

    def visit_AnnAssign(self, node):
        print("\n[[[...AnnAssign...]]]")
        print(node.__dict__)

        toLog = False
        target_id = None
        for fieldname, fieldvalue in ast.iter_fields(node):
            if fieldname == "target":
                target_id = self.visit(fieldvalue) + "@" + str(fieldvalue.lineno) \
                            + "_" + str(fieldvalue.col_offset)
            elif fieldname == "op":
                pass
            elif fieldname == "value":
                toLog = toLog or self.visit(fieldvalue)

        nodeInfoTable[target_id] = toLog

    # def visit_For(self, node):
    # 	print("\n[[[...For...]]]")
    # 	print(node.__dict__)

    # def visit_AsyncFor(self, node):
    # 	print("\n[[[...AsyncFor...]]]")
    # 	print(node.__dict__)

    # def visit_While(self, node):
    # 	print("\n[[[...While...]]]")
    # 	print(node.__dict__)

    # def visit_If(self, node):
    # 	print("\n[[[...If...]]]")
    # 	print(node.__dict__)

    # def visit_With(self, node):
    # 	print("\n[[[...With...]]]")
    # 	print(node.__dict__)

    # def visit_AsyncWith(self, node):
    # 	print("\n[[[...AsyncWith...]]]")
    # 	print(node.__dict__)

    # def visit_Raise(self, node):
    # 	print("\n[[[...Raise...]]]")
    # 	print(node.__dict__)

    # def visit_Try(self, node):
    # 	print("\n[[[...Try...]]]")
    # 	print(node.__dict__)

    # def visit_Assert(self, node):
    # 	print("\n[[[...Assert...]]]")
    # 	print(node.__dict__)

    def visit_Import(self, node):
        print("\n[[[...Import...]]]")
        print(node.__dict__)

    def visit_ImportFrom(self, node):
        print("\n[[[...ImportFrom...]]]")
        print(node.__dict__)

    # def visit_Global(self, node):
    # 	print("\n[[[...Global...]]]")
    # 	print(node.__dict__)

    # def visit_Nonlocal(self, node):
    # 	print("\n[[[...Nonlocal...]]]")
    # 	print(node.__dict__)

    # def visit_Expr(self, node):
    # 	print("\n[[[...Expr...]]]")
    # 	print(node.__dict__)

    def visit_Pass(self, node):
        print("\n[[[...Pass...]]]")
        print(node.__dict__)

    def visit_Break(self, node):
        print("\n[[[...Break...]]]")
        print(node.__dict__)

    def visit_Continue(self, node):
        print("\n[[[...Continue...]]]")
        print(node.__dict__)

    ###########################################################################
    ##### 				         Expression visit methods	   		 	  #####
    ###########################################################################
    def visit_BoolOp(self, node):
        print("[[[...BoolOp...]]]")
        print(node.__dict__)

        self.generic_visit(node)

        for fieldname, fieldvalue in ast.iter_fields(node):
            if fieldname == "op" or fieldname == "values":
                return self.visit(fieldvalue)

    def visit_BinOp(self, node):
        print("[[[...BinOp...]]]")
        print(node.__dict__)

        for fieldname, fieldvalue in ast.iter_fields(node):
            if fieldname == "left" or fieldname == "op" or fieldname == "right":
                return self.visit(fieldvalue)

    def visit_UnaryOp(self, node):
        print("[[[...UnaryOp...]]]")
        print(node.__dict__)

        for fieldname, fieldvalue in ast.iter_fields(node):
            if fieldname == "op" or fieldname == "operand":
                return self.visit(fieldvalue)

    def visit_Lambda(self, node):
        print("[[[...Lamdba...]]]")
        print(node.__dict__)

        for fieldname, fieldvalue in ast.iter_fields(node):
            if fieldname == "args":
                return False
            elif fieldname == "body":
                return self.visit(fieldvalue)

    def visit_Call(self, node):
        print("[[[...Call...]]]")
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


    # def visit_If(self, node):
    #     print("[[[...If...]]]")

    def visit_Name(self, node):
        print("[[[...Name...]]]")
        return node.id

    def visit_Num(self, node):
        print("[[[...Num...]]]")
        return False

    ###########################################################################
    ##### 				      Bool operator visit methods				  #####
    ###########################################################################
    def visit_And(self, node):
        print("[[[...And...]]]")
        return False

    def visit_Or(self, node):
        print("[[[...Or...]]]")
        return False

    ###########################################################################
    ##### 				   Binary operator visit methods				  #####
    ###########################################################################
    def visit_Add(self, node):
        print("[[[...Add...]]]")
        return False

    def visit_Sub(self, node):
        print("[[[...Sub...]]]")
        return False

    def visit_Mult(self, node):
        print("[[[...Mult...]]]")
        return False

    def visit_MatMult(self, node):
        print("[[[...MatMult...]]]")
        return False

    def visit_Div(self, node):
        print("[[[...Div...]]]")
        return False

    def visit_Mod(self, node):
        print("[[[...Mod...]]]")
        return False

    def visit_Pow(self, node):
        print("[[[...Pow...]]]")
        return False

    def visit_LShift(self, node):
        print("[[[...LShift...]]]")
        return False

    def visit_RShift(self, node):
        print("[[[...RShift...]]]")
        return False

    def visit_BitOr(self, node):
        print("[[[...BitOr...]]]")
        return False

    def visit_BitXor(self, node):
        print("[[[...BitXor...]]]")
        return False

    def visit_BitAnd(self, node):
        print("[[[...BitAnd...]]]")
        return False

    def visit_FloorDiv(self, node):
        print("[[[...FloorDiv...]]]")
        return False

    ###########################################################################
    ##### 				     Unary operator visit methods	   			  #####
    ###########################################################################
    def visit_Invert(self, node):
        print("[[[...Invert...]]]")
        return False

    def visit_Not(self, node):
        print("[[[...Not...]]]")
        return False

    def visit_UAdd(self, node):
        print("[[[...UAdd...]]]")
        return False

    def visit_USub(self, node):
        print("[[[...USub...]]]")
        return False


if __name__ == "__main__":
    main()
    print("Here is the static analysis info:")
    print(nodeInfoTable)




