from petitBloc import block
from petitBloc.exts import mayaExts
from maya import cmds
from numbers import Number


class MayaUtil:
    Numeric = ["bool", "doubleLinear", "doubleAngle", "double", "long", "short", "byte", "enum", "float"]
    String = ["string"]

    @staticmethod
    def IsNumeric(typeName):
        return typeName in MayaUtil.Numeric

    @staticmethod
    def IsString(typeName):
        return typeName in MayaUtil.String


class MayaPyFileOpen(block.Block):
    def __init__(self):
        super(MayaPyFileOpen, self).__init__()

    def initialize(self):
        self.addParam(str, "file")
        self.addOutput(str, "node")

    def __run(self, *args, **kwargs):
        return cmds.file(args[0], **kwargs)

    def run(self):
        new_nodes = mayaExts.ExecuteFunction(self.__run, *(self.param("file").get(), ), open=True, force=True, returnNewNodes=True)

        oup = self.output("node")

        for n in new_nodes:
            oup.send(n)


class MayaPyFileImport(block.Block):
    def __init__(self):
        super(MayaPyFileImport, self).__init__()

    def initialize(self):
        self.addInput(str, "file")
        self.addInput(str, "namespace")
        self.addOutput(str, "node")
        self.addParam(bool, "reference")

    def __run(self, *args, **kwargs):
        new_nodes = []

        for (file_path, ns) in args[0]:
            option = kwargs.copy()
            if ns:
                option["namespace"] = ns

            results = cmds.file(file_path, **option) or []
            new_nodes += results

        return new_nodes

    def run(self):
        file_ns_list = []
        options = {}
        namespace_eop = False
        namespace_dump = None

        in_ns = self.input("namespace")
        in_file = self.input("file")

        while (True):
            if not namespace_eop:
                ns_p = in_ns.receive()
                if ns_p.isEOP():
                    namespace_eop = True
                else:
                    namespace_dump = ns_p.value()
                    ns_p.drop()

            if namespace_dump is None:
                break

            file_p = in_file.receive()
            if file_p.isEOP():
                break

            file_ns_list.append((file_p.value(), namespace_dump))
            file_p.drop()

        if self.param("reference").get():
            options["reference"] = True
        else:
            options["import"] = True

        options["returnNewNodes"] = True

        new_nodes = mayaExts.ExecuteFunction(self.__run, *(file_ns_list, ), **options)

        oup = self.output("node")

        for n in new_nodes:
            oup.send(n)


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

        nodes = mayaExts.ExecuteFunction(self.__run, *args, **kwargs)

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

        results = mayaExts.ExecuteFunction(self.__run, *(names,))

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
        for r in mayaExts.ExecuteFunction(self.__run, *(objs, ), **kwargs):
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

        types = mayaExts.ExecuteFunction(self.__run, *(attrs,))

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

        numerics, others = mayaExts.ExecuteFunction(self.__run, *(attrs, ))

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

        strings, others = mayaExts.ExecuteFunction(self.__run, *(attrs, ))

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
            v = cmds.getAttr(attr)
            if not isinstance(v, Number):
                self.warn("Invalid type '{}'".format(type(v)))
                continue

            values.append(v)

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

        values = mayaExts.ExecuteFunction(self.__run, *(attrs, ))

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
            v = cmds.getAttr(attr)
            if v is None:
                v = ""

            if not isinstance(v, basestring):
                self.warn("Invalid type '{}'".format(type(v)))
                continue

            values.append(v)

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

        values = mayaExts.ExecuteFunction(self.__run, *(attrs, ))

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
            except Exception as e:
                self.warn(str(e))
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

        results = mayaExts.ExecuteFunction(self.__run, *(attr_vals, ))

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
            except Exception as e:
                self.warn(str(e))
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

        results = mayaExts.ExecuteFunction(self.__run, *(attr_vals, ))

        oup = self.output("result")
        for r in results:
            oup.send(r)


class MayaPyConnectAttr(block.Block):
    def __init__(self):
        super(MayaPyConnectAttr, self).__init__()

    def initialize(self):
        self.addInput(str, "source")
        self.addInput(str, "destination")
        self.addOutput(bool, "result")

    def __run(self, *args, **kwargs):
        results = []

        for src, dst in args[0]:
            try:
                cmds.connectAttr(src, dst, force=True)
                results.append(True)
            except Exception as e:
                self.warn(str(e))
                results.append(False)

        return results

    def run(self):
        src_dst_list = []
        in_src = self.input("source")
        in_dst = self.input("destination")

        while (True):
            src = None
            dst = None

            src_p = in_src.receive()
            if src_p.isEOP():
                break

            src = src_p.value()
            src_p.drop()

            dst_p = in_dst.receive()
            if dst_p.isEOP():
                break

            dst = dst_p.value()
            dst_p.drop()

            src_dst_list.append((src, dst))

        results = mayaExts.ExecuteFunction(self.__run, *(src_dst_list,))

        oup = self.output("result")
        for r in results:
            oup.send(r)


class MayaPyDisconnectAttr(block.Block):
    def __init__(self):
        super(MayaPyDisconnectAttr, self).__init__()

    def initialize(self):
        self.addInput(str, "source")
        self.addInput(str, "destination")
        self.addOutput(bool, "result")

    def __run(self, *args, **kwargs):
        results = []

        for src, dst in args[0]:
            try:
                cmds.disconnectAttr(src, dst)
                results.append(True)
            except Exception as e:
                self.warn(str(e))
                results.append(False)

        return results

    def run(self):
        src_dst_list = []
        in_src = self.input("source")
        in_dst = self.input("destination")

        while (True):
            src = None
            dst = None

            src_p = in_src.receive()
            if src_p.isEOP():
                break

            src = src_p.value()
            src_p.drop()

            dst_p = in_dst.receive()
            if dst_p.isEOP():
                break

            dst = dst_p.value()
            dst_p.drop()

            src_dst_list.append((src, dst))

        results = mayaExts.ExecuteFunction(self.__run, *(src_dst_list,))

        oup = self.output("result")
        for r in results:
            oup.send(r)


class MayaPyIsConnected(block.Block):
    def __init__(self):
        super(MayaPyIsConnected, self).__init__()

    def initialize(self):
        self.addInput(str, "source")
        self.addInput(str, "destination")
        self.addOutput(bool, "result")

    def __run(self, *args, **kwargs):
        results = []

        for src, dst in args[0]:
            try:
                results.append(cmds.isConnected(src, dst))
            except Exception as e:
                self.warn(str(e))
                results.append(False)

        return results

    def run(self):
        src_dst_list = []
        in_src = self.input("source")
        in_dst = self.input("destination")

        while (True):
            src = None
            dst = None

            src_p = in_src.receive()
            if src_p.isEOP():
                break

            src = src_p.value()
            src_p.drop()

            dst_p = in_dst.receive()
            if dst_p.isEOP():
                break

            dst = dst_p.value()
            dst_p.drop()

            src_dst_list.append((src, dst))

        results = mayaExts.ExecuteFunction(self.__run, *(src_dst_list,))

        oup = self.output("result")
        for r in results:
            oup.send(r)


class MayaPyCreateNode(block.Block):
    def __init__(self):
        super(MayaPyCreateNode, self).__init__()

    def initialize(self):
        self.addInput(str, "name")
        self.addInput(str, "nodeType")
        self.addOutput(str, "node")

    def __run(self, *args, **kwargs):
        results = []

        for name, node_type in args[0]:
            results.append(cmds.createNode(node_type, n=name, s=True))

        return results

    def run(self):
        all_types = cmds.allNodeTypes()
        in_name = self.input("name")
        in_type = self.input("nodeType")

        name_type_list = []
        node_type_eop = False
        node_type_dump = None

        while (True):
            if (not node_type_eop):
                type_p = in_type.receive()
                if type_p.isEOP():
                    node_type_eop = True
                else:
                    node_type_dump = type_p.value()
                    type_p.drop()

            if node_type_dump is None:
                break

            if node_type_dump not in all_types:
                self.warn("Unknown nodeType '{}'".format(node_type_dump))
                return

            name_p = in_name.receive()
            if name_p.isEOP():
                break

            name_type_list.append((name_p.value(), node_type_dump))
            name_p.drop()

        results = mayaExts.ExecuteFunction(self.__run, *(name_type_list,))

        oup = self.output("node")
        for r in results:
            oup.send(r)


class MayaPyDelete(block.Block):
    def __init__(self):
        super(MayaPyDelete, self).__init__()

    def initialize(self):
        self.addInput(str, "node")

    def __run(self, *args, **kwargs):
        cmds.delete(args[0])

    def run(self):
        nodes = []

        in_node = self.input("node")
        while (True):
            node_p = in_node.receive()
            if node_p.isEOP():
                break

            nodes.append(node_p.value())
            node_p.drop()

        mayaExts.ExecuteFunction(self.__run, *(nodes, ))


class MayaPyListConnections(block.Block):
    def __init__(self):
        super(MayaPyListConnections, self).__init__()

    def initialize(self):
        self.addInput(str, "name")
        self.addParam(bool, "srcConnection")
        self.addParam(bool, "dstConnection")
        self.addParam(str, "type")
        self.addOutput(str, "source")
        self.addOutput(str, "destination")

    def __run(self, *args, **kwargs):
        results = []

        for name in args[0]:
            if kwargs.get("source"):
                op = kwargs.copy()
                op["destination"] = False

                conns = cmds.listConnections(name, **op) or []

                for i in range(0, len(conns), 2):
                    src = conns[i + 1]
                    dst = conns[i]

                    results.append((src, dst))

            if kwargs.get("destination"):
                op = kwargs.copy()
                op["source"] = False

                conns = cmds.listConnections(name, **op) or []

                for i in range(0, len(conns), 2):
                    src = conns[i]
                    dst = conns[i + 1]

                    results.append((src, dst))

        return results

    def run(self):
        options = {"connections": True, "plugs": True}
        options["source"] = self.param("srcConnection").get()
        options["destination"] = self.param("dstConnection").get()
        type_name = self.param("type").get()
        if type_name:
            options["type"] = type_name

        names = []
        in_name = self.input("name")
        while (True):
            name_p = in_name.receive()
            if name_p.isEOP():
                break

            names.append(name_p.value())
            name_p.drop()

        results = mayaExts.ExecuteFunction(self.__run, *(names, ), **options)

        out_src = self.output('source')
        out_dst = self.output('destination')

        for (src, dst) in results:
            out_src.send(src)
            out_dst.send(dst)


class MayaPyListChildren(block.Block):
    def __init__(self):
        super(MayaPyListChildren, self).__init__()

    def initialize(self):
        self.addInput(str, "name")
        self.addOutput(list, "children")
        self.addParam(bool, "fullPath")

    def __run(self, *args, **kwargs):
        results = []
        for name in args[0]:
            results.append(cmds.listRelatives(name, **kwargs) or [])

        return results

    def run(self):
        options = {}
        options["fullPath"] = self.param("fullPath").get()
        options["children"] = True

        names = []
        in_name = self.input("name")
        while (True):
            name_p = in_name.receive()
            if name_p.isEOP():
                break

            names.append(name_p.value())
            name_p.drop()

        results = mayaExts.ExecuteFunction(self.__run, *(names, ), **options)

        out_chd = self.output('children')

        for children in results:
            out_chd.send(children)


class MayaPyListParents(block.Block):
    def __init__(self):
        super(MayaPyListParents, self).__init__()

    def initialize(self):
        self.addInput(str, "name")
        self.addOutput(list, "parents")
        self.addParam(bool, "fullPath")

    def __run(self, *args, **kwargs):
        results = []
        for name in args[0]:
            results.append(cmds.listRelatives(name, **kwargs) or [])

        return results

    def run(self):
        options = {"fullPath": self.param("fullPath").get()}
        options["parent"] = True

        names = []
        in_name = self.input("name")
        while (True):
            name_p = in_name.receive()
            if name_p.isEOP():
                break

            names.append(name_p.value())
            name_p.drop()

        results = mayaExts.ExecuteFunction(self.__run, *(names, ), **options)

        out_prn = self.output('parents')

        for parents in results:
            out_prn.send(parents)
