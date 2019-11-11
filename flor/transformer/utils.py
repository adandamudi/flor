import ast

class False_Break(ValueError): pass

def node_eq(node1, node2):
    """
    TODO: Testing
    :param node1:
    :param node2:
    :return:
    """
    for (field1, value1), (field2, value2) in zip(ast.iter_fields(node1), ast.iter_fields(node2)):
        if field1 == 'ctx' and field2 == 'ctx':
            continue
        if field1 != field2:
            raise False_Break()
        if type(value1) != type(value2):
            raise False_Break()
        if isinstance(value1, list):
            if len(value1) != len(value2):
                raise False_Break()
            for item1, item2 in zip(value1, value2):
                if type(item1) != type(item2):
                    raise False_Break()
                if isinstance(item1, ast.AST):
                    node_eq(item1, item2)
                else:
                    if item1 != item2:
                        raise False_Break()
        elif isinstance(value1, ast.AST):
            node_eq(value1, value2)
        else:
            if value1 != value2:
                raise False_Break()

def node_equals(node1, node2):
    try:
        node_eq(node1, node2)
        return True
    except False_Break:
        return False

def node_in_nodes(node, nodes):
    for other in nodes:
        if node_equals(node, other):
            return True
    return False

def set_union(nodes1, nodes2):
    output = [n for n in nodes1]
    for node2 in nodes2:
        if not node_in_nodes(node2, nodes1):
            output.append(node2)
    return output

def set_intersection(nodes1, nodes2):
    output = []
    for node1 in nodes1:
        for node2 in nodes2:
            if node_equals(node1, node2) and not node_in_nodes(node1, output):
                output.append(node1)
    return output