# The MIT License
# Chen Meng observerchan@gmail.com
# https://github.com/meng89/xl

""" XML without mire! / 无坑 XML ！"""

import abc
from abc import ABC
from typing import Self, List


__version__ = "1.2.0"


class _BaseElement:
    @abc.abstractmethod
    def to_str(self, *args, **kwargs):
        pass


class Escape:
    @abc.abstractmethod
    def to_str(self, *args, **kwargs):
        pass


class HtmlZWNJ(Escape):
    """The zero-width non-joiner"""
    def to_str(self, *args, **kwargs) -> str:
        return "&zwnj;"

# Element 子元素的转义需求：
# <> 这种字符元素因为和 xml 标签用冲突，所以需要转义。> 符号似乎不需要转义，但是，这是xml设计
# & 因为是转义字符，所以它也需要转义

# Element 的属性转义需求：
# 如果属性值是单引号包含的，需要用

_escape_table_string_kid = (
    ('&', '&amp;'),  # I guess this must be the first one?
    ('<', '&lt;'),
    # 大于号可能无需转义
    # https://stackoverflow.com/questions/76342593/xmlmapper-not-escaping-the-greater-than-character-but-does-escape-the-rest
    ('>', '&gt;'),
    HtmlZWNJ
)

_escape_table_single_quote = (("'", "&apos;"),)
_escape_table_double_quote = (('"', '&quot;'),)

_escape_table_quote = _escape_table_double_quote + _escape_table_double_quote

_xml_attr_escape_table = _escape_table_string_kid + _escape_table_quote


_escape_table_all = _escape_table_string_kid + _xml_attr_escape_table


def _merge(l: list[str|_BaseElement]):
    new_l = []
    for x in l:
        if isinstance(x, _BaseElement):
            new_l.append(x)
        elif isinstance(x, str):
            if len(new_l) > 0 and isinstance(new_l[-1], str):
                new_l[-1] = new_l[-1] + x
            else:
                new_l.append(x)
    return new_l


def _strip(l: list[str|_BaseElement]):
    if len(l) > 0 and isinstance(l[0], str):
        l[0] = l[0].rstrip()
    if len(l) > 0 and isinstance(l[-1], str):
        l[-1] = l[-1].rstrip()

    if len(l) == 1 and l[0] == "":
        return []
    else:
        return l


# text to XML
def _unescape(text, table) -> list[str|_BaseElement]:
    l = []
    i = 0
    while i < len(text):
        unescaped = False
        for z in table:
            if isinstance(z, tuple):
                x, y = z
                if text[i: i + len(y)] == y:
                    l.append(x)
                    i += len(y)
                    unescaped = True
                    break
            elif isinstance(z, type) and isinstance(z(), Escape):
                l.append(z())
                i += len(z().to_str())
                unescaped = True
                break

        if not unescaped:
            l.append(text[i])
            i += 1

    return _merge(l)


# XML to text
def _escape(text, table) -> list[str|_BaseElement]:
    s = ""
    for c in text:
        escaped = False
        for z in table:
            if isinstance(z, tuple):
                x, y = z
                if c == x:
                    s += y
                    escaped = True
                    break
        if not escaped:
            s += c
    return s


def _escape_quoted_string(s):
    return _escape(s, _escape_table_quote)


def _escape_unquoted_string(s):
    return _escape(s, _escape_table_all)


def _unescape_element_string(text):
    table = (
        ('&', '&amp;'),  # I guess this must be the first one?
        ('<', '&lt;'),
        ('>', '&gt;'),
        HtmlZWNJ,
    )
    return _unescape(text, table)


def _escape_element_string(text):
    table = (
        ('&', '&amp;'),  # I guess this must be the first one?
        ('<', '&lt;'),
        ('>', '&gt;')
    )
    return _escape(text, table)


def _read_till_strings(text, i, strings):
    old_s = None
    old_i = None
    end_s = None
    for string in strings:
        new_s, new_i = _read_till(text, i, string)
        if old_s is None:
            old_s = new_s
            old_i = new_i
            end_s = string
        else:
            if len(new_s) < len(old_s):
                old_s = new_s
                old_i = new_i
                end_s = string

    return old_s, old_i, end_s


def _parse_doctype(text, i):
    if text[i:i + 10].lower() != "<!DOCTYPE ".lower():
        return False, None

    e = DocType(default_html5=False)

    i += 10
    i = _ignore_blank(text, i)

    while i < len(text):
        if text[i] == ">":
            i += 1
            return True, (e, i)

        elif text[i] in ('"', "'"):
            s, i, end = _read_quoted_string(text, i)
            e.quoted_strings.append(_escape_quoted_string(s))

        else:
            s, i, end = _read_unquoted_string(text, i)
            e.unquoted_strings.append(_escape_unquoted_string(s))

        i = _ignore_blank(text, i)

    raise ParseError


def _read_unquoted_string(text, i):
    x = _read_till_strings(text, i, (" ", ">"))
    return x


def _read_quoted_string(text, i):
    mark = text[i]
    i += 1
    s, i, end = _read_till_strings(text, i, (mark, ))
    i += 1
    return s, i, end


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


def _parse_string(text, i) -> tuple:
    s, i = _read_text(text, i)
    if s:
        # return True, (_unescape(s, _xml_escape_table), i)
        return True, (_unescape_element_string(s), i)
    else:
        return False, None


def _read_text(text, i):
    s = ""
    while i < len(text) and text[i] not in "<":
        s += text[i]
        i += 1
    return s, i


def _parse_prolog_or_qme(text, i):
    if text[i] != "<":
        return False, None
    i += 1
    i = _ignore_blank(text, i)
    if text[i] != "?":
        return False, None
    i += 1
    i = _ignore_blank(text, i)

    ###
    tag, i, end = _read_till_strings(text, i, (" ", "?"))
    ###
    i += 1
    i = _ignore_blank(text, i)

    if tag == "xml":
        e = Prolog()
    else:
        e = QMElement(tag)

    if end == "?":
        i = _ignore_blank(text, i)
        if text[i] == ">":
            i += 1
            return True, (text, i)
        else:
            return False, None

    while i < len(text):
        if text[i] == "?":
            i += 1
            break

        key, value, i = _read_attr(text, i)
        e.attrs[key.lower()] = value
        i = _ignore_blank(text, i)

    i = _ignore_blank(text, i)
    # print(e.attrs)
    # if text[i] != "?":
    #    return False, None
    # i += 1
    i = _ignore_blank(text, i)
    if text[i] != ">":
        return False, None
    i += 1
    return True, (e, i)


def _parse_cdata(text, i):
    if text[i:i + 9].lower() != "<![CDATA[".lower():
        return False, None

    i += 9

    s, i = _read_till(text, i, "]]>")
    i += 3
    cdata = Cdata(s)
    return True, (cdata, i)


#  ↑↓←→↖↗↙↘
# def _parse_element(text, i, do_strip=False, dont_do_tags=None, ignore_comment=False):
def _parse_element(text, i,
                   ignore_blank: bool = False,
                   unignore_blank_parent_tags: list = None,
                   strip: bool = False,
                   unstrip_parent_tags: list = None,
                   ignore_comment: bool = False,
                   ):
    unignore_blank_parent_tags = unignore_blank_parent_tags or []
    unstrip_parent_tags = unstrip_parent_tags or []

    # <a id="1">xx<b/>yy</a>
    # ↑           ↑
    if text[i] != "<":
        return False, None

    i = _ignore_blank(text, i + 1)

    if text[i] in ("?", "!"):
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

    _kids, i = _read_subs(text, i,
                          ignore_blank, unignore_blank_parent_tags,
                          strip, unstrip_parent_tags,
                          ignore_comment,
                          tag)
    e.kids = _kids

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


def _parse_comment(text, i):
    if text[i:i + 4] != "<!--":
        return False, None
    i += 4
    comment_text, i = _read_till(text, i, "-->")
    i += 3
    comment_text2 = Comment(_unescape_comment(comment_text))
    return True, (comment_text2, i)


def _unescape_comment(text):
    # todo more research
    return text


def _read_attr(text, i):
    key, i = _read_till(text, i, "=")
    i += 1
    key = key.strip()
    i = _ignore_blank(text, i)
    qmark = text[i]
    i += 1
    string_value, i = _read_till(text, i, qmark)
    i += 1
    return key, _unescape(string_value, _xml_attr_escape_table), i


def _read_till(text: str, i: int, stop_s: str):
    index = text.find(stop_s, i)
    if index > -1:
        return text[i:index], index
    else:
        return text[i:], len(text)


def _read_subs(text, i,
               ignore_blank, unignore_blank_parent_tags,
               strip, unstrip_parent_tags,
               ignore_comment,
               tag) -> tuple:
    kids = []
    # while True:
    while i < len(text):
        for fun in (_parse_cdata, _parse_prolog_or_qme, _parse_doctype, _parse_comment, _parse_element, _parse_string):
            if fun is _parse_element:
                is_success, result = fun(text, i,
                                         ignore_blank, unignore_blank_parent_tags,
                                         strip, unstrip_parent_tags,
                                         ignore_comment,
                                         )
            else:
                is_success, result = fun(text, i)

            if is_success:
                term, i = result

                if isinstance(term, list):
                    if ignore_blank is True and tag not in unignore_blank_parent_tags:
                        term = _strip(term)
                    if strip is True and tag not in unstrip_parent_tags:
                        term = _strip(term)
                    if term:
                        kids.extend(term)
                elif isinstance(term, Comment) and ignore_comment:
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


class ParseError(Exception):
    pass


class NotExistsError(Exception):
    pass


class _Tag:
    def __init__(self, tag=None):
        self.tag = tag

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, value):
        if not isinstance(value, str):
            raise ValueError
        self._tag = value

    def _tag2str(self):
        if self.tag:
            return self.tag
        else:
            raise Exception


class _Attr:
    def __init__(self, attrs: dict = None):
        self._attrs = dict(attrs) if attrs else {}

    @property
    def attrs(self):
        return self._attrs

    @attrs.setter
    def attrs(self, value):
        if not isinstance(dict, value):
            raise ValueError
        self._attrs = value

    def _attrs2str(self):
        if self.attrs == {}:
            return ""
        s = ""
        _attrs_string_list = []
        for attr_name, attr_value in self.attrs.items():
            _attrs_string_list.append('{}="{}"'.format(attr_name, _escape(attr_value, _xml_attr_escape_table)))

        if _attrs_string_list:
            s += " "
            s += " ".join(_attrs_string_list)
        return s


class _Kids:
    def __init__(self, kids=None):
        self.kids = kids or []

    @property
    def kids(self):
        return self._kids

    @kids.setter
    def kids(self, value):
        try:
            iter(value)
        except TypeError:
            raise ValueError("kids needs to be iterable")
        self._kids = value





class QMElement(_BaseElement, _Tag, _Attr):
    def __init__(self, tag: str = None, attrs: dict = None):
        _Tag.__init__(self, tag)
        _Attr.__init__(self, attrs)

    def to_str(self, *args, **kwargs):
        s = "<?" + self.tag
        attrs_str = self._attrs2str()
        if attrs_str:
            # s += " "
            s += self._attrs2str()
        s += "?>"

        return s


class Prolog(QMElement):
    def __init__(self, version=None, encoding=None, standalone=None):
        super().__init__("xml")
        self.version = version or "1.0"
        self.encoding = encoding or "UTF-8"
        if standalone:
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
        if value.lower() in ("yes", "no"):
            self.attrs["standalone"] = value
        elif value is None:
            pass
        else:
            raise Exception


class Comment(_BaseElement):
    def __init__(self, text: str):
        self.text = text

    def to_str(self, *args, **kwargs):
        text = self.text.replace("-->", "--&gt;")
        return "<!--{}-->".format(text)


# html thing, not xml thing
class DocType(_BaseElement):
    def __init__(self, unquoted_strings: list = None, quoted_strings: list = None, default_html5=True):
        self.unquoted_strings = unquoted_strings or []
        self.quoted_strings = quoted_strings or []

        if not self.unquoted_strings and not self.quoted_strings and default_html5 is True:
            self.unquoted_strings.append("html")

    @property
    def unquoted_strings(self):
        return self._unquoted_strings

    @unquoted_strings.setter
    def unquoted_strings(self, value):
        if hasattr(value, "__iter__"):
            self._unquoted_strings = value

    @property
    def quoted_strings(self):
        return self._quoted_strings

    @quoted_strings.setter
    def quoted_strings(self, value):
        if hasattr(value, "__iter__"):
            self._quoted_strings = value

    def to_str(self, *args, **kwargs):
        s = "<!DOCTYPE"
        for unquoted_string in self.unquoted_strings:
            s += " {}".format(unquoted_string)

        for quoted_string in self.quoted_strings:
            s += " \"{}\"".format(quoted_string)

        s += ">"
        return s


class Cdata(_BaseElement):
    def __init__(self, text: str = None):
        self.text = text or ""

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value: str):
        if "]]>" not in value:
            self._text = value
        else:
            raise ValueError

    def to_str(self, *args, **kwargs):
        return "<![CDATA[{}]]>".format(self.text)


class Element(_BaseElement, _Tag, _Attr, _Kids):
    def __init__(self, tag: str = None, attrs: dict[str, str] = None, kids: list = None):
        _BaseElement.__init__(self)
        _Tag.__init__(self, tag)
        _Attr.__init__(self, attrs)
        self.kids = kids or []
        self.self_closing = True

    @property
    def self_closing(self):
        return self._self_closing

    @self_closing.setter
    def self_closing(self, value):
        if not isinstance(value, bool):
            raise Exception
        self._self_closing = value

    def ekid(self, *args, **kwargs) -> Self:
        e = Element(*args, **kwargs)
        self.kids.append(e)
        return e

    def skid(self, string: str) -> None:
        self.kids.append(string)

    def find_kids(self, tag) -> List[Self]:
        kids = []
        for _kid in self.kids:
            if isinstance(_kid, Element) and _kid.tag == tag:
                kids.append(_kid)
        return kids

    def find_descendants(self, tag):
        es = []
        if self.tag == tag:
            es.append(self)
        for _kid in self.kids:
            if isinstance(_kid, Element):
                es.extend(_kid.find_descendants(tag))
        return es

    def to_str(self,
               do_pretty: bool = False,
               begin_indent: int = 0,
               step: int = 4,
               char: str = " ",
               dont_do_tags: list[str] = None,
               try_self_closing: bool = None,
               ) -> str:
        dont_do_tags = dont_do_tags or []

        s = "<" + self.tag + self._attrs2str()

        def _is_empty_kids():
            for __kid in self._kids:
                if isinstance(__kid, str):
                    if __kid == "":
                        pass
                    else:
                        return False
                else:
                    return False
            return True

        if self._kids and not _is_empty_kids():
            s += '>'

            _indent_text = '\n' + char * (begin_indent + step)
            do_pretty_ultimately = do_pretty is True and self.tag not in dont_do_tags

            for _kid in self._kids:
                if do_pretty_ultimately:
                    s += _indent_text

                if isinstance(_kid, str):
                    s += _escape_element_string(_kid)

                elif isinstance(_kid, Escape):
                    s += _kid.to_str()

                elif isinstance(_kid, _BaseElement):
                    s += _kid.to_str(do_pretty_ultimately,
                                     begin_indent + step,
                                     step,
                                     char,
                                     dont_do_tags,
                                     try_self_closing
                                     )
                else:
                    raise TypeError("Kid type:{} not supported.".format(type(_kid)))

            if do_pretty_ultimately:
                s += '\n' + char * begin_indent
            s += '</{}>'.format(self.tag)

        else:
            if try_self_closing is True:
                self_closing_ultimately = True
            elif try_self_closing is False:
                self_closing_ultimately = False
            elif try_self_closing is None:
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


class Xml(_Kids):
    def __init__(self, root: Element = None,
                 prolog: Prolog = None, doctype: DocType = None, qmelements: list[QMElement] = None,
                 kids: list[Prolog | DocType | QMElement | Element] = None):
        _Kids.__init__(self)
        if prolog:
            self.kids.append(prolog)
        if qmelements:
            self.kids.extend(qmelements)
        if doctype:
            self.kids.append(doctype)
        if root:
            self.kids.append(root)
        if kids:
            self.kids = kids

    @property
    def root(self) -> Element:
        for x in self.kids:
            if isinstance(x, Element):
                return x
        raise NotExistsError

    @property
    def prolog(self) -> Prolog:
        for x in self.kids:
            if isinstance(x, Prolog):
                return x
        raise NotExistsError

    @property
    def doctype(self) -> DocType:
        for x in self.kids:
            if type(x) is type(DocType()):
                return x
        raise NotExistsError

    def to_str(self,
               new_line_after_kid: bool = None,
               do_pretty: bool = False,
               begin_indent: int = 0,
               step: int = 4,
               char: str = " ",
               dont_do_tags: list[str] = None,
               try_self_closing: bool = None,
               ) -> str:
        if do_pretty is True and new_line_after_kid is None:
            new_line_after_kid = True
        s = ""
        ss = []
        for kid in self.kids:
            if isinstance(kid, _BaseElement):
                x = kid.to_str(do_pretty,
                               begin_indent,
                               step,
                               char,
                               dont_do_tags,
                               try_self_closing,
                               )
                ss.append(x)
            elif isinstance(kid, str):
                ss.append(kid)
            else:
                raise Exception("How???")
        if new_line_after_kid is True:
            s += "\n".join(ss)
            s += "\n"
        else:
            s += "".join(ss)
        return s


def parse(text,
          ignore_blank: bool = False, unignore_blank_parent_tags: list = None,
          strip: bool = False, unstrip_parent_tags: list = None,
          ignore_comment: bool = False) -> Xml:
    unignore_blank_parent_tags = unignore_blank_parent_tags or []
    unstrip_parent_tags = unstrip_parent_tags or []
    xml = Xml()
    kids, i = _read_subs(text, 0,
                         ignore_blank, unignore_blank_parent_tags,
                         strip, unstrip_parent_tags,
                         ignore_comment,
                         None
                         )

    for kid in kids:
        # if not isinstance(kid, str):
        xml.kids.append(kid)

    return xml


def parse_e(text, *args, **kwargs):
    xml = parse(text, *args, **kwargs)
    return xml.root
