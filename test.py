#!/usr/bin/env python3
import xl as xl

s = """
<root>
<milestone n="1" unit="juan"/>
<a>1</a>
</root>
"""
print(xl.parse(s).to_str())


def x(text: str):
    while True:
        new_text = text.replace("-->", "--&gt;")
