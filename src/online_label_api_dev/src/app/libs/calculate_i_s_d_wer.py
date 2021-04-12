# -*- coding: utf-8 -*-
import numpy as np


def edit_distance(r, h):
    """
    This function is to calculate the edit distance of reference sentence and the hypothesis sentence.
    Main algorithm used is dynamic programming.
    Attributes:
        r -> the list of words produced by splitting reference sentence.
        h -> the list of words produced by splitting hypothesis sentence.
    """

    d = np.zeros((len(r) + 1) * (len(h) + 1), dtype=np.uint8).reshape((len(r) + 1, len(h) + 1))
    for i in range(len(r) + 1):
        for j in range(len(h) + 1):
            if i == 0:
                d[0][j] = j
            elif j == 0:
                d[i][0] = i
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            if r[i - 1] == h[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                substitute = d[i - 1][j - 1] + 1
                insert = d[i][j - 1] + 1
                delete = d[i - 1][j] + 1
                d[i][j] = min(substitute, insert, delete)
    return d


def get_step_list(r, h, d):
    """
    This function is to get the list of steps in the process of dynamic programming.
    Attributes:
        r -> the list of words produced by splitting reference sentence.
        h -> the list of words produced by splitting hypothesis sentence.
        d -> the matrix built when calculating the editing distance of h and r.
    """
    x = len(r)
    y = len(h)
    line = []
    while True:
        if x == 0 and y == 0:
            break
        elif x >= 1 and y >= 1 and d[x][y] == d[x - 1][y - 1] and r[x - 1] == h[y - 1]:
            line.append("e")
            x = x - 1
            y = y - 1
        elif y >= 1 and d[x][y] == d[x][y - 1] + 1:
            line.append("i")
            x = x
            y = y - 1
        elif x >= 1 and y >= 1 and d[x][y] == d[x - 1][y - 1] + 1:
            line.append("s")
            x = x - 1
            y = y - 1
        else:
            line.append("d")
            x = x - 1
            y = y
    return line[::-1]


def aligned_print(line, r, h):
    """
    This function is to print the WER of comparing reference and hypothesis sentences in an aligned way.

    Attributes:
        list   -> the list of steps.
        r      -> the list of words produced by splitting reference sentence.
        h      -> the list of words produced by splitting hypothesis sentence.
    """
    for i in range(len(line)):
        if line[i] == "i":
            count = 0
            for j in range(i):
                if line[j] == "d":
                    count += 1
        elif line[i] == "s":
            count1 = 0
            for j in range(i):
                if line[j] == "i":
                    count1 += 1
            count2 = 0
            for j in range(i):
                if line[j] == "d":
                    count2 += 1
        else:
            count = 0
            for j in range(i):
                if line[j] == "i":
                    count += 1
    for i in range(len(line)):
        if line[i] == "d":
            count = 0
            for j in range(i):
                if line[j] == "i":
                    count += 1
        elif line[i] == "s":
            count1 = 0
            for j in range(i):
                if line[j] == "i":
                    count1 += 1
            count2 = 0
            for j in range(i):
                if line[j] == "d":
                    count2 += 1
        else:
            count = 0
            for j in range(i):
                if line[j] == "d":
                    count += 1

    i_num, d_num, s_num = 0, 0, 0
    for i in range(len(line)):
        if line[i] == "d":
            count = 0
            for j in range(i):
                if line[j] == "i":
                    count += 1
            d_num += 1
        elif line[i] == "i":
            count = 0
            for j in range(i):
                if line[j] == "d":
                    count += 1
            i_num += 1
        elif line[i] == "s":
            count1 = 0
            for j in range(i):
                if line[j] == "i":
                    count1 += 1
            index1 = i - count1
            count2 = 0
            for j in range(i):
                if line[j] == "d":
                    count2 += 1
            index2 = i - count2
            if len(r[index1]) > len(h[index2]):
                s_num += 1
            else:
                s_num += 1
        else:
            count = 0
            for j in range(i):
                if line[j] == "i":
                    count += 1
    return i_num, d_num, s_num


def i_s_d_wer(r, h):
    """
    This is a function that calculate the word error rate in ASR.
    You can use it like this: wer("what is it".split(), "what is".split())
    """
    # 计算wer
    d = edit_distance(r, h)
    line = get_step_list(r, h, d)
    # print r
    # print h
    # print ' '.join(line)
    # print '\n'.join(ch_sent_by_stepline(r, h,line))
    wer = float(d[len(r)][len(h)]) / len(r) * 100

    i_num, d_num, s_num = aligned_print(line, r, h)
    return i_num, s_num, d_num, wer


def ch_sent_by_stepline(r, h, stepline):
    new_r = ''
    r_cur = 0
    new_h = ''
    h_cur = 0
    for i in range(0, len(stepline)):
        if stepline[i] == 'e':
            new_r += r[r_cur]
            new_h += h[h_cur]
            r_cur += 1
            h_cur += 1
        elif stepline[i] == 'i':
            new_h += '<font color="blue">%s</font>' % h[h_cur]
            h_cur += 1
        elif stepline[i] == 'd':
            new_r += '<font color="red">%s</font>' % r[r_cur]
            r_cur += 1
        elif stepline[i] == 's':
            new_r += '<font color="green">%s</font>' % r[r_cur]
            new_h += '<font color="green">%s</font>' % h[h_cur]
            r_cur += 1
            h_cur += 1
    return new_r, new_h


def ch_sent_by_stepline2():
    pass

# print i_s_d_wer('那两个是和解那一一按他那原来证据救一致一致吗就保证书先说吧。',
#                 u'那你两个是和解那一一按他那原来证据就一致吗，就保证~先说吧。')


# print i_s_d_wer(u'这里有1000',
#                 u'这里是有1000')
