#!/usr/bin/env python3
import xl


xmlfile = "/mnt/data/projects/xml-p5a/T/T01/T01n0001.xml"

s = open(xmlfile).read()

s = """ <a><!--CBETA todo type: a--><!--CBETA todo type: newmod--> </a>"""
s = """<a>&gt;</a>\n"""
s = """
<?xml version="1.0" ?>
<?xyz s="1"?>
<body>
    <p>窗前明月光，</p>hehe
    <p>疑似地上霜。</p><a>  </a><a2/>
    <p>举头望明月，</p>
    <p>低头思故乡。</p>
</body>
"""
xml = xl.parse(s, ignore_blank=True, unignore_blank_parent_tags=[],)


print("end")
print(xml.kids)


