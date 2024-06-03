#!/usr/bin/env python3
import xl


xmlfile = "/mnt/data/projects/xml-p5a/T/T01/T01n0001.xml"

s = open(xmlfile).read()

s = """ <a><!--CBETA todo type: a--><!--CBETA todo type: newmod--> </a>"""
s = """<a>&gt;</a>\n"""
s = """<body>
    <p>窗前明月光，</p>hehe
    <p>疑似地上霜。</p><a>  </a><a2/>
    <p>举头望明月，</p>
    <p>低头思故乡。</p>
</body>
"""
xml = xl.parse(s, ignore_blank=True, unignore_blank_parent_tags=[],)


print("end")
print(xml.to_str(self_closing=None))


class _Base:
    pass


class _Attr:
    def __init__(self):
        self.attrs = {}

    def attrs_to_str(self):
        if self.attrs == {}:
            return ""

        s = " "
        _attrs_string_list = []
        for attr_name, attr_value in self.attrs.items():
            _attrs_string_list.append('{}="{}"'.format(attr_name, _escape(attr_value, _xml_attr_escape_table)))

        if _attrs_string_list:
            s += " "
            s += " ".join(_attrs_string_list)

        return s


class _Kids:
    def kids_to_str(self):
        pass


class Element(_Base, _Attr, _Kids):
    pass


class QMElement(_Base, _Attr):
    pass


class Prolog(QMElement):
    pass


class DocType:
    pass


class Comment:
    pass


class XML(_Base, _Kids):
    pass
