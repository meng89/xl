# The MIT License

# https://github.com/meng89/xl

""" XML without mire! / 无坑 XML ！"""


__version__ = "0.4.0"

from abc import abstractmethod as _abstractmethod

_xml_escape_table = (
    ('&', '&amp;'),  # I guess this must be the first one?
    ('<', '&lt;'),
    # 大于好可能无需转义
    # https://stackoverflow.com/questions/76342593/xmlmapper-not-escaping-the-greater-than-character-but-does-escape-the-rest
    ('>', '&gt;')
)

_xml_attr_escape_table = _xml_escape_table + (
    ('"', '&quot;'),
    ("'", "&apos;")
)

_xml_comment_escape_table = (
    ("-", "&#45;")
)


def _unescape(text, table):
    _text = text
    nt = ""
    i = 0
    while i < len(text):
        unescaped = False
        for x, y in table:
            if text[i: i + len(y)] == y:
                nt += x
                i += len(y)
                unescaped = True
                break
        if not unescaped:
            nt += text[i]
            i += 1
    return nt


def _escape(text, table):
    nt = ""
    for c in text:
        escaped = False
        for x, y in table:
            if c == x:
                nt += y
                escaped = True
                break
        if not escaped:
            nt += c
    return nt


def _is_straight_line(element):
    if len(element.kids) == 0:
        return True

    if len(element.kids) == 1:
        if isinstance(element.kids[0], Element):
            return _is_straight_line(element.kids[0])
        else:
            return True

    elif len(element.kids) > 1:
        return False


def _is_have_string_kid(kids):
    for _kid in kids:
        if isinstance(_kid, str):
            return True
    return False


class ToStrError(Exception):
    pass


class _Node(object):
    @_abstractmethod
    def to_str(self):
        pass


class DocType(_Node):
    def __init__(self, text=None):
        self.text = text or "html"

    def to_str(self, *args, **kwargs):
        return "<!DOCTYPE {}>".format(self.text)


class InitError(Exception):
    pass


class Element(_Node):
    def __init__(self, tag=None, attrs=None, kids=None):
        _Node.__init__(self)
        self.tag = tag
        self._attrs = dict(attrs) if attrs else {}
        self._kids = list(kids) if kids else []

        # 通过 Element() 建立的节点，默认设置为自闭合标签
        self.self_closing = True

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, value):
        if not isinstance(value, str):
            raise ValueError
        self._tag = value

    @property
    def attrs(self):
        return self._attrs

    @attrs.setter
    def attrs(self, value):
        if not isinstance(dict, value):
            raise ValueError
        self._attrs = value

    @property
    def kids(self):
        return self._kids

    @kids.setter
    def kids(self, value):
        if not isinstance(value, list):
            raise ValueError
        self._kids = value

    @property
    def self_closing(self):
        return self._self_closing

    @self_closing.setter
    def self_closing(self, value):
        if not isinstance(value, bool):
            raise Exception
        self._self_closing = value

    def ekid(self, *args, **kwargs):
        e = Element(*args, **kwargs)
        self.kids.append(e)
        return e

    def skid(self, string: str):
        self.kids.append(string)
        return string

    def ckid(self, string: str):
        c = Comment(string)
        self.kids.append(c)
        return c

    def to_str(self,
               do_pretty=False,
               begin_indent=0,
               step=4,
               char=" ",
               dont_do_tags=None,
               self_closing=True
               ):

        dont_do_tags = dont_do_tags or []

        s = '<'
        assert self.tag
        s += self.tag

        _attrs_string_list = []
        for attr_name, attr_value in self.attrs.items():
            _attrs_string_list.append('{}="{}"'.format(attr_name, _escape(attr_value, _xml_attr_escape_table)))

        if _attrs_string_list:
            s += ' '
            s += ' '.join(_attrs_string_list)

        if self._kids:
            s += '>'

            _indent_text = '\n' + char * (begin_indent + step)
            do_pretty_ultimately = do_pretty and self.tag not in dont_do_tags and self not in dont_do_tags
            for _kid in self._kids:
                if do_pretty_ultimately:
                    s += _indent_text

                if isinstance(_kid, str):
                    s += _escape_element_string(_kid)

                elif isinstance(_kid, Element):
                    s += _kid.to_str(do_pretty_ultimately,
                                     begin_indent + step,
                                     step,
                                     char,
                                     dont_do_tags,
                                     self_closing
                                     )
                elif isinstance(_kid, Comment):
                    s += _kid.to_str()
                else:
                    raise TypeError("Kid type:{} not supported by to_str().".format(type(_kid)))
            if do_pretty_ultimately:
                s += '\n' + char * begin_indent

            s += '</{}>'.format(self.tag)

        else:
            if self_closing is True:
                self_closing_ultimately = True
            elif self_closing is False:
                self_closing_ultimately = False
            elif self_closing is None:
                self_closing_ultimately = self.self_closing
            else:
                raise Exception("HOW?")

            if self_closing_ultimately is True:
                s += '/>'
            elif self_closing_ultimately is False:
                s = s + ">" + '</{}>'.format(self.tag)
            else:
                raise Exception("HOW?")

        return s

    def find_attr(self, attr):
        for _attr, value in self.attrs.items():
            if _attr == attr:
                return value

    def find_all(self, tag):
        es = []
        if self.tag == tag:
            es.append(self)
        for _kid in self.kids:
            if isinstance(_kid, Element):
                es.extend(_kid.find_all(tag))
        return es

    def find_kids(self, tag):
        kids = []
        for _kid in self.kids:
            if isinstance(_kid, Element) and _kid.tag == tag:
                kids.append(_kid)
        return kids


# question mark element
class QMElement(Element):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_str(self, *args, **kwargs):
        kwargs["self_closing"] = True
        s = super().to_str(*args, **kwargs)
        assert s[-2:] == "/>"
        new_s = "<?" + s[1:-2] + "?>"
        return new_s

    @property
    def kids(self):
        return []


class Prolog(QMElement):
    def __init__(self, version=None, encoding=None, standalone=None):
        super().__init__(tag="xml")
        self.version = version or '1.0'
        self.encoding = encoding or 'UTF-8'
        self.standalone = standalone

    @property
    def version(self):
        return self.attrs["version"]

    @version.setter
    def version(self, value):
        if value:
            self.attrs["version"] = value

    @property
    def encoding(self):
        return self.attrs["encoding"]

    @encoding.setter
    def encoding(self, value):
        if value:
            self.attrs["encoding"] = value

    @property
    def standalone(self):
        return self.attrs["standalone"]

    @standalone.setter
    def standalone(self, value):
        if value:
            self.attrs["standalone"] = value


class Comment(object):
    def __init__(self, text):
        self.text = text

    def to_str(self):
        return "<!--{}-->".format(_escape_comment(self.text))


def _escape_comment(text):
    # todo more research
    return text


def skid(element, tag, attrs=None, kids=None):
    sub_element = Element(tag, attrs, kids)
    element.kids.append(sub_element)
    return sub_element


def sub(*args, **kwargs):
    return skid(*args, **kwargs)


def _parse_prolog(text, i):
    if text[i] != "<":
        return False, None
    i += 1
    i = _ignore_blank(text, i)
    if text[i] != "?":
        return False, None
    i += 1
    i = _ignore_blank(text, i)

    ###
    tag, i = _read_till(text, i, " ")
    ###

    if tag == "xml":
        element = Prolog()
    else:
        element = QMElement(tag)

    i = _ignore_blank(text, i)

    while i < len(text) and text[i] not in "?>":
        key, value, i = _read_attr(text, i)
        element.attrs[key.lower()] = value
        i = _ignore_blank(text, i)

    i = _ignore_blank(text, i)
    if text[i] != "?":
        return False, None
    i += 1
    i = _ignore_blank(text, i)
    if text[i] != ">":
        return False, None
    i += 1
    return True, (element, i)


def _parse_doctype(text, i):
    if text[i:i + 10] != "<!DOCTYPE ":
        return False, None
    i += 10
    _text = ""

    lessthan = 0
    greaterthan = 0
    while i < len(text):
        if text[i] == ">":
            greaterthan += 1
        elif text[i] == "<":
            lessthan += 1

        if greaterthan - lessthan == 1:
            break
        else:
            _text += text[i]
            i += 1

    i += 1
    return True, (DocType(_text), i)


_blank = (" ", "\t", "\n", "\r")


def _ignore_blank(text, i):
    while i < len(text):
        if text[i] not in _blank:
            return i
        else:
            i += 1
    return i


def _read_tag(text, i):
    tag = ""
    while i < len(text) and text[i] not in " />":
        tag += text[i]
        i += 1
    return tag, i


def _read_endtag(text, i):
    tag = ""
    while i < len(text) and text[i] not in " >":
        tag += text[i]
        i += 1
    return tag, i


def _parse_string(text, i) -> tuple:
    s, i = _read_text(text, i)
    if s:
        # return True, (_unescape(s, _xml_escape_table), i)
        return True, (_unescape_element_string(s), i)
    else:
        return False, None


_element_string_table = (
    ('&', '&amp;'),  # I guess this must be the first one?
    ('<', '&lt;'),
    ('>', '&gt;')
)


def _unescape_element_string(text):
    table = (
        ('&', '&amp;'),  # I guess this must be the first one?
        ('<', '&lt;'),
        ('>', '&gt;')
    )
    return _unescape(text, table)


def _escape_element_string(text):
    table = (
        ('&', '&amp;'),  # I guess this must be the first one?
        ('<', '&lt;'),
        ('>', '&gt;')
    )
    return _escape(text, table)


def _read_text(text, i):
    t = ""
    while i < len(text) and text[i] not in "<":
        t += text[i]
        i += 1
    return t, i


#  ↑↓←→↖↗↙↘
def _parse_element(text, i, do_strip=False, dont_do_tags=None, ignore_comment=True):
    dont_do_tags = dont_do_tags or []

    # <a id="1">xx<b/>yy</a>
    # ↑           ↑
    if text[i] != "<":
        return False, None

    i = _ignore_blank(text, i + 1)

    if text[i] == "!":
        return False, None

    # <a level="1"></a>
    # <a level="1" />

    tag, i = _read_tag(text, i)
    if not tag:
        return False, None

    e = Element(tag=tag)
    i = _ignore_blank(text, i)

    # 读取属性
    while i < len(text) and text[i] not in "/>":
        # <a id="1">xx<b/>yy</a>
        #          ↖
        key, value, i = _read_attr(text, i)
        e.attrs[key] = value
        i = _ignore_blank(text, i)

    # />
    # 自封闭标签，到此结束
    if text[i] == "/":
        # <a id="1">xx<b/>yy</a>
        #               ↑
        i += 1
        i = _ignore_blank(text, i)
        if text[i] != ">":
            return False, None
        i += 1
        i = _ignore_blank(text, i)
        e.self_closing = True
        return True, (e, i)
    # >
    # 非自封闭标签，继续读取子元素
    elif text[i] == ">":
        # <a id="1">xx<b/>yy</a>
        #          ↑
        i += 1

    else:
        raise Exception
    #######

    _kids, i = _read_subs(text, i, do_strip=do_strip, dont_do_tags=dont_do_tags, ignore_comment=ignore_comment)
    for x in _kids:
        x2 = x
        if isinstance(x, str) and tag not in dont_do_tags:
            x2 = x.strip()
        if x2:
            e.kids.append(x2)

    # </a>
    # kids 读完了，该读取结尾了，结尾必然是这种格式：</a>
    if text[i] != "<":
        return False, None
    i += 1

    i = _ignore_blank(text, i)
    if text[i] != "/":
        return False, None
    i += 1

    i = _ignore_blank(text, i)
    if text[i:i+len(tag)] != tag:
        return False, None
    i += len(tag)

    i = _ignore_blank(text, i)
    if text[i] != ">":
        return False, None
    i += 1
    e.self_closing = False
    return True, (e, i)

    #######


def _parse_comment(text, i):
    if text[i:i + 4] != "<!--":
        return False, None
    i += 4

    comment_text, i = _read_till(text, i, "-->")
    comment_text2 = Comment(_unescape_comment(comment_text))
    return True, (comment_text2, i)


def _unescape_comment(text):
    # todo more research
    return text


def _read_attr(text, i):
    key, i = _read_till(text, i, "=")
    key = key.strip()
    i = _ignore_blank(text, i)
    qmark = text[i]
    i += 1
    string_value, i = _read_till(text, i, qmark)
    return key, _unescape(string_value, _xml_attr_escape_table), i


class Xml(object):
    def __init__(self, root=None, prolog=None, doctype=None):
        self._kids = []

        if prolog:
            self._kids.append(prolog)
        if doctype:
            self._kids.append(doctype)
        if root:
            self._kids.append(root)

    @property
    def kids(self):
        return self._kids

    @property
    def root(self):
        for x in self.kids:
            if type(x) is type(Element("x")):
                return x

    @property
    def prolog(self):
        for x in self.kids:
            if type(x) is type(Prolog()):
                return x

    @property
    def doctype(self):
        for x in self.kids:
            if type(x) is type(DocType()):
                return x

    def to_str(self,
               do_pretty=False,
               begin_indent=0,
               step=4,
               char=" ",
               dont_do_tags=None,
               self_closing=None):
        s = ''

        for x in self.kids:
            s += x.to_str(do_pretty=do_pretty,
                          begin_indent=begin_indent,
                          step=step,
                          char=char,
                          dont_do_tags=dont_do_tags,
                          self_closing=self_closing)
            s += "\n"

        return s


def _read_subs(text: str, i: int, *args, ignore_comment, **kwargs) -> tuple:
    kids = []
    # while True:
    while i < len(text):
        for fun in (_parse_prolog, _parse_doctype, _parse_comment, _parse_element, _parse_string):
            if fun is _parse_element:
                is_success, result = fun(text, i, *args, ignore_comment=ignore_comment, **kwargs)
            else:
                is_success, result = fun(text, i)

            if is_success:
                term, i = result
                if ignore_comment and (type(term) is type(Comment(""))):
                    pass
                elif term == "":
                    pass
                else:
                    kids.append(term)
                break

        if is_success:
            continue
        else:
            break
    # print(kids)
    return kids, i


def parse(text, do_strip: bool = None, dont_do_tags: list[str] or tuple[str] = None, ignore_comment: bool = False)\
        -> Xml:
    kids, i = _read_subs(text, 0, do_strip=do_strip, dont_do_tags=dont_do_tags, ignore_comment=ignore_comment)

    xml = Xml()
    for kid in kids:
        if not isinstance(kid, str):
            xml.kids.append(kid)

    return xml


def parse_e(text, *args, **kwargs):
    i = _ignore_blank(text, 0)
    is_success, (root, i) = _parse_element(text, i, *args, **kwargs)
    i = _ignore_blank(text, i)
    if len(text) != i:
        raise ParseError("Some text could not parse: {}".format(repr(text[i:])))
    return root


def _read_till(text, bi, stoptext):
    _text = ""
    while bi < len(text):
        if text[bi:bi + len(stoptext)] == stoptext:
            return _text, bi + len(stoptext)
        else:
            _text += text[bi]
            bi += 1
    return _text, bi


class ParseError(Exception):
    pass
