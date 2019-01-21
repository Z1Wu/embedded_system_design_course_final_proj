import os
import sys
import re
"""
    由于烧写软件的限制，烧写进去的是一些 lua 脚本，没有编译的过程，由于本次实验需要使用UART，如果在wifi module 中
    使用print，print的内容同样输出在 uart 影响了实验，所以通过这个文件在把不该出现在最后代码中的语句去掉，包括在
    一下几个部分:
        1. 调试时使用的 print
        2. 注释
        3.
"""

USAGE = "python <this_script> <path_of_your_source_file>"

re_print_dect = re.compile(r'[ ]*print[ ]*\(')
re_comment_dect = re.compile(r'^[ ]*--')
origin_src = None

try:
    origin_src = sys.argv[1]
    print("src file name: " + origin_src)
except:
    print(USAGE)

# 提前检测是否有命名冲突
new_src = "new_" + origin_src

with open(origin_src, "r", encoding = "utf-8") as rf:
    with open(new_src, "w", encoding = "utf-8") as wf:
        old_content = rf.readlines()
        wf.write("".join([line for line in old_content if re_comment_dect.match(line) == None and re_print_dect.match(line) == None]))