#!/usr/bin/env python3
import xl as xl


xmlfile = "/mnt/data/projects/xml-p5a/T/T01/T01n0001.xml"

s = """
"""
s = """
<?xml version="1.0" ?>
<body>
    <p>窗前明月光，</p>hehe
    <p>疑似地上霜。</p><a>  </a><a2/>
    <p>举头望明月，</p>
    <p>低头思故乡。</p>
</body>
"""
xml = xl.parse(s, ignore_blank=True, unignore_blank_parent_tags=[])

print(xml.kids)
