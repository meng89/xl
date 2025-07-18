#!/usr/bin/env python3

l = ["", ""]

if l and all([isinstance(x, str) for x in l]) and "".join(l) != "":
    print("非空")
else:
    print("空")