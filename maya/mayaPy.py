from petitBloc import block
from maya import cmds
from maya import utils


class MayaPyLs(block.Block):
    def __init__(self):
        super(MayaPyLs, self).__init__()

    def initialize(self):
        self.addParam(str, "pattern")
        self.addParam(str, "type")
        self.addParam(str, "optionDict")
        self.addOutput(str, "result")

    def run(self):
        nodes = []
        args = tuple()
        kwargs = {}

        pattern = self.param("pattern").get()

        if pattern:
            args = (pattern, )

        node_type = self.param("type").get()
        if node_type:
            kwargs["type"] = node_type

        try:
            option_str = self.param("optionDict").get()
            if option_str:
                option_dict = eval(option_str)
                if isinstance(option_dict, dict):
                    kwargs.update(option_dict)
        except:
            pass

        nodes = utils.executeInMainThreadWithResult(cmds.ls, *args, **kwargs)

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


class MayaPyListAttr(block.Block):
    def __init__(self):
        super(MayaPyListAttr, self).__init__()

    def initialize(self):
        self.addInput(str, "object")
        self.addOutput(str, "attr")
        self.addParam(bool, "keyable")
        self.addParam(bool, "userDefined")
        self.addParam(str, "optionDict")

    def process(self):
        obj_p = self.input("object").receive()
        if obj_p.isEOP():
            return False

        kwargs = {}

        kwargs["keyable"] = self.param("keyable").get()
        kwargs["userDefined"] = self.param("userDefined").get()

        obj = obj_p.value()
        obj_p.drop()

        out = self.output("attr")
        if utils.executeInMainThreadWithResult(cmds.objExists, *(obj,)):
            for attr in utils.executeInMainThreadWithResult(cmds.listAttr, *(obj,), **kwargs) or []:
                out.send(attr)

        return True


class MayaPyAttr(block.Block):
    def __init__(self):
        super(MayaPyAttr, self).__init__()

    def initialize(self):
        self.addInput(str, "object")
        self.addInput(str, "attrName")
        self.addOutput(str, "attr")

    def run(self):
        self.__obj_eop = False
        self.__attr_eop = False
        self.__obj_dump = None
        self.__attr_dump = None
        super(MayaPyAttr, self).run()

    def process(self):
        if not self.__obj_eop:
            obj = self.input("object").receive()
            if obj.isEOP():
                self.__obj_eop = True
            else:
                self.__obj_dump = obj.value()

        if self.__obj_dump is None:
            return False

        if not self.__attr_eop:
            att = self.input("attrName").receive()
            if att.isEOP():
                self.__attr_eop = True
            else:
                self.__attr_dump = att.value()

        if self.__attr_dump is None:
            return False

        if self.__obj_eop and self.__attr_eop:
            return False

        self.output("attr").send("{}.{}".format(self.__obj_dump, self.__attr_dump))

        return True


class MayaPyGetAttr(block.Block):
    Numeric = ["doubleLinear", "doubleAngle", "double", "long", "short", "byte", "enum", "float"]
    Boolean = ["bool"]
    String = ["string"]

    def __init__(self):
        super(MayaPyGetAttr, self).__init__()

    def initialize(self):
        self.addInput(str, "attr")
        self.addParam(bool, "type")
        self.addOutput(bool, "bool")
        self.addOutput(str, "str")
        self.addOutput(float, "float")

    def process(self):
        attr_p = self.input("attr").receive()
        if attr_p.isEOP():
            return False

        attr = attr_p.value()
        attr_p.drop()

        attr_type = utils.executeInMainThreadWithResult(cmds.getAttr, *(attr,), type=True)

        if self.param("type").get():
            self.output("str").send(attr_type)

            return True

        if attr_type in MayaPyGetAttr.Numeric:
            self.output("float").send(utils.executeInMainThreadWithResult(cmds.getAttr, *(attr,)))

            return True

        if attr_type in MayaPyGetAttr.Boolean:
            self.output("bool").send(utils.executeInMainThreadWithResult(cmds.getAttr, *(attr,)))

            return True

        if attr_type in MayaPyGetAttr.String:
            self.output("str").send(utils.executeInMainThreadWithResult(cmds.getAttr, *(attr,)))

            return True

        return True
