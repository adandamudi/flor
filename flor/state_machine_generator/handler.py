import ast
import astor
from flor.utils import is_valid_python

from flor.complete_capture.trace_generator.log_stmts.log_stmt import LogStmt

class Handler:

    def __init__(self, node : ast.AST):
        self.node = node

    def is_flog_write(self):
        return LogStmt.is_instance(self.node)

    def is_highlight(self):
        # TODO: This is where we will want to be able to read a broad set of HIGHLIGHTS
        """
        For now, we are hardcoding two types of highlights:
            - GET(name, expression)
            - GET(name, expression, predicate)
        Predicates can either be a Python expression or in a string.
        """
        if not isinstance(self.node, ast.Call):
            return False

        func = self.node.func
        args = self.node.args

        if (not isinstance(func, ast.Name)) \
                or func.id != 'GET'\
                or (len(args) not in [2, 3])\
                or self.node.keywords\
                or (not isinstance(args[0], ast.Str)):
            return False

        # Check if predicate is valid
        if len(args) == 3 and \
                not (isinstance(args[2], ast.Compare) or isinstance(args[2], ast.Str)):
            return False

        return True


    def fetch_highlight_name(self):
        assert self.is_highlight(), "{} is not a valid highlight.".format(astor.to_source(self.node).strip())
        return self.node.args[0].s


    def fetch_highlight_pred(self):
        assert self.is_highlight(), "{} is not a valid highlight.".format(astor.to_source(self.node).strip())
        if len(self.node.args) < 3:
            return None
        pred = self.node.args[-1]
        if isinstance(pred, ast.Str):
            pred_str = pred.s
        elif isinstance(pred, ast.Compare):
            pred.left.id = 'self.ns.' + pred.left.id
            pred_str = astor.to_source(pred).strip()
        else:
            pred_str = astor.to_source(pred).strip()
        assert is_valid_python(pred_str), "{} is not a valid Python expression.".format(pred_str)
        return pred_str


    def fetch_lsn(self):
        assert LogStmt.is_instance(self.node)
        dc = self.node.value.values[1].args[0]
        for i, astree in enumerate(dc.keys):
            if isinstance(astree, ast.Str) and astree.s == 'lsn':
                return dc.values[i].n
        raise RuntimeError()
