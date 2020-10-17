

class SkipBlock:

    stack = []

    @staticmethod
    def step_into(uid, cond):
        SkipBlock.stack.append((uid, cond))
        return cond

    @classmethod
    def end(cls, *args):
        uid, cond = SkipBlock.stack.pop()
        # serialize args



