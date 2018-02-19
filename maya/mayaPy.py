from petitBloc import block
from maya import cmds
from maya import utils


class MayaUtil:
    Numeric = ["bool", "doubleLinear", "doubleAngle", "double", "long", "short", "byte", "enum", "float"]
    String = ["string"]

    @staticmethod
    def IsNumeric(typeName):
        return typeName in MayaUtil.Numeric

    @staticmethod
    def IsString(typeName):
        return typeName in MayaUtil.String

    @staticmethod
    def Execute(func, *args, **kwargs):
        res = utils.executeInMainThreadWithResult(func, *args, **kwargs)
        return res


class MayaPyLs(block.Block):
    def __init__(self):
        super(MayaPyLs, self).__init__()

    def initialize(self):
        self.addParam(str, "pattern")
        self.addParam(str, "type")
        self.addParam(str, "optionDict")
        self.addOutput(str, "result")

    def __run(self, *args, **kwargs):
        return cmds.ls(*args, **kwargs)

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

        nodes = MayaUtil.Execute(self.__run, *args, **kwargs)

        out = self.output("result")
        for n in nodes:
            out.send(n)


class MayaPyExist(block.Block):
    def __init__(self):
        super(MayaPyExist, self).__init__()

    def initialize(self):
        self.addInput(str, "name")
        self.addOutput(bool, "exist")

    def __run(self, *args, **kwargs):
        results = []
        for name in args[0]:
            a = cmds.objExists(name)
            results.append(a)

        return results

    def run(self):
        names = []

        inp = self.input("name")

        while (True):
            name_p = inp.receive()
            if name_p.isEOP():
                break

            name = name_p.value()
            name_p.drop()

            names.append(name)

        results = []
        oup = self.output("exist")

        results = MayaUtil.Execute(self.__run, *(names,))

        for r in results:
            oup.send(r)


class MayaPyListAttr(block.Block):
    def __init__(self):
        super(MayaPyListAttr, self).__init__()

    def initialize(self):
        self.addInput(str, "object")
        self.addOutput(str, "attr")
        self.addParam(bool, "keyable")
        self.addParam(bool, "userDefined")
        self.addParam(str, "optionDict")

    def __run(self, *args, **kwargs):
        results = []
        for obj in args[0]:
            results += map(lambda x: "{}.{}".format(obj, x), cmds.listAttr(obj, **kwargs) or [])

        return results

    def run(self):
        objs = []
        inp = self.input("object")

        while (True):
            obj_p = inp.receive()
            if obj_p.isEOP():
                break

            obj = obj_p.value()

            obj_p.drop()
            objs.append(obj)

        kwargs = {}

        kwargs["keyable"] = self.param("keyable").get()
        kwargs["userDefined"] = self.param("userDefined").get()
        try:
            option_str = self.param("optionDict").get()
            if option_str:
                option_dict = eval(option_str)
                if isinstance(option_dict, dict):
                    kwargs.update(option_dict)
        except:
            pass

        oup = self.output("attr")
        for r in MayaUtil.Execute(self.__run, *(objs, ), **kwargs):
            oup.send(r)


class MayaPyGetAttrType(block.Block):
    def __init__(self):
        super(MayaPyGetAttrType, self).__init__()

    def initialize(self):
        self.addInput(str, "attr")
        self.addOutput(str, "type")

    def __run(self, *args, **kwargs):
        types = []

        for attr in args[0]:
            types.append(cmds.getAttr(attr, type=True))

        return types

    def run(self):
        attrs = []
        inp = self.input("attr")

        while (True):
            attr_p = inp.receive()
            if attr_p.isEOP():
                break

            attr = attr_p.value()
            attr_p.drop()

            attrs.append(attr)

        types = MayaUtil.Execute(self.__run, *(attrs,))

        oup = self.output("type")
        for t in types:
            oup.send(t)


class MayaPyAttrSelectorNumeric(block.Block):
    def __init__(self):
        super(MayaPyAttrSelectorNumeric, self).__init__()

    def initialize(self):
        self.addInput(str, "attr")
        self.addOutput(str, "numeric")
        self.addOutput(str, "other")

    def __run(self, *args, **kwargs):
        numrics = []
        others = []

        for attr in args[0]:
            type_str = cmds.getAttr(attr, type=True)

            if not MayaUtil.IsNumeric(type_str):
                others.append(attr)
                continue

            numrics.append(attr)

        return (numrics, others)

    def run(self):
        attrs = []
        inp = self.input("attr")

        while (True):
            attr_p = inp.receive()
            if attr_p.isEOP():
                break

            attr = attr_p.value()
            attr_p.drop()

            attrs.append(attr)

        numerics, others = MayaUtil.Execute(self.__run, *(attrs, ))

        out_num = self.output("numeric")
        out_other = self.output("other")

        for n in numerics:
            out_num.send(n)

        for o in others:
            out_other.send(o)


class MayaPyAttrSelectorString(block.Block):
    def __init__(self):
        super(MayaPyAttrSelectorString, self).__init__()

    def initialize(self):
        self.addInput(str, "attr")
        self.addOutput(str, "string")
        self.addOutput(str, "other")

    def __run(self, *args, **kwargs):
        strings = []
        others = []

        for attr in args[0]:
            type_str = cmds.getAttr(attr, type=True)

            if not MayaUtil.IsString(type_str):
                others.append(attr)
                continue

            strings.append(attr)

        return (strings, others)

    def run(self):
        attrs = []
        inp = self.input("attr")

        while (True):
            attr_p = inp.receive()
            if attr_p.isEOP():
                break

            attr = attr_p.value()
            attr_p.drop()

            attrs.append(attr)

        strings, others = MayaUtil.Execute(self.__run, *(attrs, ))

        out_str = self.output("string")
        out_other = self.output("other")

        for n in strings:
            out_str.send(n)

        for o in others:
            out_other.send(o)


class MayaPyGetAttrNumeric(block.Block):
    def __init__(self):
        super(MayaPyGetAttrNumeric, self).__init__()

    def initialize(self):
        self.addInput(str, "attr")
        self.addOutput(float, "value")

    def __run(self, *args, **kwargs):
        values = []

        for attr in args[0]:
            values.append(cmds.getAttr(attr))

        return values

    def run(self):
        attrs = []
        inp = self.input("attr")

        while (True):
            attr_p = inp.receive()
            if attr_p.isEOP():
                break

            attr = attr_p.value()
            attr_p.drop()

            attrs.append(attr)

        values = MayaUtil.Execute(self.__run, *(attrs, ))

        val = self.output("value")

        for v in values:
            if not val.send(v):
                val.send(0)


class MayaPyGetAttrString(block.Block):
    def __init__(self):
        super(MayaPyGetAttrString, self).__init__()

    def initialize(self):
        self.addInput(str, "attr")
        self.addOutput(str, "value")

    def __run(self, *args, **kwargs):
        values = []

        for attr in args[0]:
            values.append(cmds.getAttr(attr))

        return values

    def run(self):
        attrs = []
        inp = self.input("attr")

        while (True):
            attr_p = inp.receive()
            if attr_p.isEOP():
                break

            attr = attr_p.value()
            attr_p.drop()

            attrs.append(attr)

        values = MayaUtil.Execute(self.__run, *(attrs, ))

        val = self.output("value")

        for v in values:
            if not val.send(v):
                val.send("")


class MayaPySetAttrNumeric(block.Block):
    def __init__(self):
        super(MayaPySetAttrNumeric, self).__init__()

    def initialize(self):
        self.addInput(str, "attr")
        self.addInput(float, "value")
        self.addOutput(bool, "result")

    def __run(self, *args, **kwargs):
        results = []

        for attr, value in args[0]:
            res = True
            try:
                cmds.setAttr(attr, value)
            except:
                res = False

            results.append(res)

        return results

    def run(self):
        attr_vals = []

        in_att = self.input("attr")
        in_val = self.input("value")

        while (True):
            attr_p = in_att.receive()
            if attr_p.isEOP():
                break

            attr = attr_p.value()
            attr_p.drop()

            value_p = in_val.receive()
            if value_p.isEOP():
                break

            value = value_p.value()
            value_p.drop()

            attr_vals.append((attr, value))

        results = MayaUtil.Execute(self.__run, *(attr_vals, ))

        oup = self.output("result")
        for r in results:
            oup.send(r)


class MayaPySetAttrString(block.Block):
    def __init__(self):
        super(MayaPySetAttrString, self).__init__()

    def initialize(self):
        self.addInput(str, "attr")
        self.addInput(str, "value")
        self.addOutput(bool, "result")

    def __run(self, *args, **kwargs):
        results = []

        for attr, value in args[0]:
            res = True
            try:
                cmds.setAttr(attr, value, type="string")
            except:
                res = False

            results.append(res)

        return results

    def run(self):
        attr_vals = []

        in_att = self.input("attr")
        in_val = self.input("value")

        while (True):
            attr_p = in_att.receive()
            if attr_p.isEOP():
                break

            attr = attr_p.value()
            attr_p.drop()

            value_p = in_val.receive()
            if value_p.isEOP():
                break

            value = value_p.value()
            value_p.drop()

            attr_vals.append((attr, value))

        results = MayaUtil.Execute(self.__run, *(attr_vals, ))

        oup = self.output("result")
        for r in results:
            oup.send(r)
