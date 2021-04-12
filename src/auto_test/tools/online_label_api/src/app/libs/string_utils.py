# -*- coding: utf-8 -*-
def try_decode(string, charset_list=('ascii', 'utf8', 'gbk')):

    for charset in charset_list:
        try:
            string = string.decode(charset)
            break
        except Exception as e:
            # print e
            pass
    return string
