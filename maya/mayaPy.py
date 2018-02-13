from petitBloc import block
from maya import cmds


class MayaPyLs(block.Block):
    def __init__(self):
        super(MayaPyLs, self).__init__()

    def initialize(self):
        ## in my enviroment(maya2018 osx)
        ## an error occurs when passing boolean parameter to ls
        self.addParam(str, "pattern")
        self.addParam(str, "type")
        self.addParam(str, "optionsDict")
        self.addOutput(str, "result")

    def run(self):
        nodes = []
        kwargs = {}

        option_str = self.param("optionsDict").get()
        if option_str:
            try:
                arg = eval(option_str)
                if isinstance(arg, dict):
                    kwargs = arg
            except:
                pass

        node_type = self.param("type").get()
        if node_type:
            kwargs["type"] = node_type

        pattern = self.param("pattern").get()

        if pattern:
            nodes = cmds.ls(pattern, **kwargs)
        else:
            nodes = cmds.ls(**kwargs)

        out = self.output("result")

        for n in nodes:
            out.send(n)


class MayaPyExist(block.Block):
    def __init__(self):
        super(MayaPyExist, self).__init__()

    def initialize(self):
        self.addInput(str, "name")
        self.addOutput(bool, "exist")

    def process(self):
        name_p = self.input("name").receive()
        if name_p.isEOP():
            return False

        name = name_p.value()
        name_p.drop()

        self.output("exist").send(cmds.objExists(name))

        return True
