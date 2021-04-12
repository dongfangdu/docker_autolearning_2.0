# -*- coding: utf-8 -*-
"""
([零一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟亿]+亿)?零?([一二三四五六七八九十百千壹贰叁肆伍陆柒捌玖拾佰仟]+万)?零?([一二三四五六七八九十百壹贰叁肆伍陆柒捌玖拾佰][千仟])?零?([一二三四五六七八九十壹贰叁肆伍陆柒捌玖拾][百佰])?零?([一二三四五六七八九壹贰叁肆伍陆柒捌玖]?[十拾])?零?([一二三四五六七八九壹贰叁肆伍陆柒捌玖])?
两[十拾百佰千仟万萬亿億]
"""
import re


def get_number(str_han):
    str_han = str_han.encode('utf8')
    res = 0
    if str_han in '一壹幺':
        res = 1
    elif str_han in '二贰两':
        res = 2
    elif str_han in '三叁':
        res = 3
    elif str_han in '四肆':
        res = 4
    elif str_han in '五伍':
        res = 5
    elif str_han in '六陆':
        res = 6
    elif str_han in '七柒':
        res = 7
    elif str_han in '八捌':
        res = 8
    elif str_han in '九玖':
        res = 9
    elif str_han in '十拾':
        res = 10
    return res


def get_base_number(str_han):
    str_han = str_han.encode('utf8')
    res = 1
    if str_han in '十拾':
        res = 10
    elif str_han in '百佰':
        res = 100
    elif str_han in '千仟':
        res = 1000
    elif str_han in '万萬':
        res = 10000
    elif str_han in '亿億':
        res = 100000000

    return res


def format_text_to_number(text_han_unicode, level=0):
    res = 0
    if len(text_han_unicode) == 1:
        res = get_number(text_han_unicode)
    else:
        str_number = text_han_unicode[:-1]
        str_maybe_base = text_han_unicode[-1]
        if len(text_han_unicode) == 2:
            res = get_number(str_number) * get_base_number(str_maybe_base)
        else:
            re_rule = ur'([零一幺二两三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟亿]+亿)?零?([一幺二两三四五六七八九百千壹贰叁肆伍陆柒捌玖十拾佰仟]+万)?零?([一幺二两三四五六七八九十百壹贰叁肆伍陆柒捌玖拾佰][千仟])?零?([一幺二两三四五六七八九十壹贰叁肆伍陆柒捌玖拾][百佰])?零?([一幺二两三四五六七八九壹贰叁肆伍陆柒捌玖]?[十拾])?零?([一幺二两三四五六七八九壹贰叁肆伍陆柒捌玖])?'
            result = re.finditer(re_rule, str_number)

            counter = 0
            start_idx = 0
            for p in result:
                for g in p.groups():
                    if g:
                        tmp = format_text_to_number(g, level + 1)
                        idx = text_han_unicode.index(g, start_idx)
                        if tmp < 10:
                            if idx > 0:
                                if text_han_unicode[idx - 1] != u'零':
                                    base = (get_base_number(text_han_unicode[idx - 1]) / 10)
                                    if base == 0:
                                        res *= 10
                                    tmp *= base or 1
                        res += tmp
                        start_idx = idx + len(g)
                    counter += 1
            res *= get_base_number(str_maybe_base)
    # print level, res
    return res


def format_sentence(sentence):
    re_rule = ur'([零一幺二两三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟亿]+亿)?零?([一幺二两三四五六七八九百千壹贰叁肆伍陆柒捌玖十拾佰仟]+万)?零?([一幺二两三四五六七八九十百壹贰叁肆伍陆柒捌玖拾佰][千仟])?零?([一幺二两三四五六七八九十壹贰叁肆伍陆柒捌玖拾][百佰])?零?([一幺二两三四五六七八九壹贰叁肆伍陆柒捌玖]?[十拾])?零?([一幺二两三四五六七八九壹贰叁肆伍陆柒捌玖])?'
    result = re.finditer(re_rule, sentence)
    new_sentence = sentence

    for p in result:
        sub_str = p.group()
        # print sub_str
        if sub_str:
            place_str = u''
            for c in sub_str:
                if c != u'零':
                    break
                place_str += u'0'
            # print sub_str
            # print [(k, len(list(g))) for k, g in itertools.groupby(sub_str)][0][0]
            if len(place_str) == len(sub_str):
                new_sentence = new_sentence.replace(sub_str, place_str, 1)
            else:
                new_sentence = new_sentence.replace(
                    sub_str, u'{}{}'.format(place_str, format_text_to_number(u'{} '.format(sub_str))), 1
                )
    # new_sentence = new_sentence.replace(u'幺', u'1')
    return new_sentence


if __name__ == '__main__':
    text_string = [u'~他打入实习人员名单~还有几个案子都把他打入实习人员名单',
                   u'你美国但是以以联合国的名义进进来打的哦这场战',
                   u'五一三零二五一九六五零三一四三四九零系景园之父',
                   u'我就我在那屋檐下坐着我不知道他死没死',
                   u'知道这样一个活动的话~当时知道~关注',
                   u'~我想问一下那我们这个立案的话大概',
                   u'~中大灾难性事故的后续~工作~',
                   u'不能做了公司就承认借你的钱嘛这有什么哦我说借我的钱你就还来',
                   u'七七八七七八蒋介石的蒋不是是贾',
                   u'中央法院中央法院你找中央法院呀',
                   u'就想把中年轻的共和国扼杀在摇篮',
                   u'也就是二零一七年十二月十九日',
                   u'是一万三千二百六十七块四毛三',
                   u'~那么一年的时间我们兴化法院',
                   u'长兴县二零一六嗯年零五二二',
                   u'~转账了他每次也从来也没拿过一分现金嘛也就是转账',
                   u'是他是上诉人还是被上诉人',
                   u'奥呢奥运会的奥奥运会的奥',
                   u'那你又说你又不敢说谁打谁',
                   u'二五九七七五七三对吗五七三二五九七五七三是七位数',
                   u'~也是从这个解放思想~',
                   u'交呢不交呢到时候还撤诉',
                   u'三千叁佰三十三点三三元',
                   u'一百三十八万给涪城法院',
                   u'嗯当事人你的名字叫什么',
                   u'如何坚决党指~各地方',
                   u'唉小女人我跟你说这样子',
                   u'呃幺三五八八零三幺三五',
                   u'零五七幺一二三六八好嘞',
                   u'然后呢~法庭这一块呢',
                   u'就是你把钱借给他过后',
                   u'十四万六千两百五十九~视察调研亲力执行',
                   u'好的呃呃多少啊二五二二七二二二五二二七二二',
                   u'我跟任德全我只认你',
                   u'找钱后面自己才去找钱最后拖到下午',
                   u'那个就不叫砍头戏了',
                   u'浙零五明中幺九一号',
                   u'asy二五港香港证',
                   u'恒耀永恒的永恒的恒',
                   u'就是急诊医生看的',
                   u'提交到长兴法院13号恩恩恩恩嗯13号',
                   u'~当事人名字报一下',
                   u'然后他帮忙操作一下',
                   u'然后赵龙只是有担保作用赵龙牵的线',
                   u'书记员的嗯那个联系方式你要记一下吗',
                   u'我就是说他这辈子把我是折磨够了的他',
                   u'等那个~这边信号',
                   u'他~吻合不起来',
                   u'啊一千五百个县',
                   u'嗯二五二二七七零',
                   u'刘安文也可以作证',
                   u'~的时候曾经说过',
                   u'谁叫你转的嘛~是什么人吗上诉人',
                   u'总共供货是好多',
                   u'三角九分钱本钱',
                   u'半脱位是不是哦',
                   u'我电脑但是从~',
                   u'~2597521',
                   u'~看一下你看一下',
                   u'第十四份也就是',
                   u'嗯被告被告被告是',
                   u'第一个项目经营部',
                   u'氯胺酮俗称K粉五百二十八点三八克',
                   u'一千七百六十九万五千三百一十元',
                   u'显现了队伍素质',
                   u'当事人叫什么名字',
                   u'他只得得到一点点',
                   u'嗯你记一下刑庭那边二五二二七八五',
                   u'呃二五二二六七幺',
                   u'~你看这个数目',
                   u'就就这个是葬身在',
                   u'嗯二五二二七幺五',
                   u'二十九点二七二克',
                   u'这系统有点问题了',
                   u'四亿四亿四亿四亿六千万人嘛当时',
                   u'实际上我们把这些案例填上去以后',
                   u'~跟我法院我甚至是执行到位',
                   u'湖州中院嘛嗯对',
                   u'方式芳草的方吗',
                   u'拾万贰仟贰佰元',
                   u'六万一嘛六万二',
                   u'哪个~判下来的',
                   u'杭州市中级人民法院是哪个啊你前面加零五七幺',
                   u'刚开始因为几个领导已经说到~',
                   u'七万六千二百元',
                   u'还内个钱作为我',
                   u'二百二十天一八年十月二十四日',
                   u'我们已经在~',
                   u'我方~驳回原告的离婚请求~',
                   u'那书记员叫啥王',
                   u'他只得得到点点',
                   u'后面创意经济与',
                   u'那么你你你辩辩',
                   u'院长你说院长他你跟院长聊两句',
                   u'邱维康我信得过',
                   u'那么第二小点',
                   u'靠近你们很近的',
                   u'现在是十四亿人',
                   u'分歧意见比较大',
                   u'这个是运用了~',
                   u'就有个~公式吗',
                   u'执行案件当中',
                   u'出现了非法所得',
                   u'这也可以预见~你想要的快乐~无极限欢迎收听fm996',
                   u'三万三千四加上这个三百一十四万二千再加一百三十八万',
                   u'他本身莫得他就是那一种做一天拿一天钱那种农村主要就是以种地为主为生',
                   u'所协的条件啦就管委会来承担',
                   u'哎你说唉唉我是浙江沪苏的~',
                   u'垃圾~处理费就是一哈嘛总共',
                   u'社会风尚倡导这个契约精神',
                   u'所协的条件啦由管委会来承担',
                   u'没有那种说法不要这样说',
                   u'交警大队拍过照的他们~我们现在都可以看~他们填第二道那个~要换',
                   u'还有一点是指什么我在这边提一提~',
                   u'就是那个吊死那个寰字你先就记这个吧',
                   u'~保全了诶诶就是对就是财产保全把他养老金冻掉了啊嗯',
                   u'嗯任世初任是',
                   u'改判了以后啊',
                   u'面积三千六百二十七点七六',
                   u'你按照你自己',
                   u'我们在~工程款就行了嘛',
                   u'~的上诉案',
                   u'小女孩这样子',
                   u'再吃肯德基呢',
                   u'你好湖州中院',
                   u'嗯何玉红是二五二二六八幺',
                   u'那个就不叫~',
                   u'成效我这个是不太很懂~',
                   u'大写一百是吧',
                   u'实际年龄他的',
                   u'~把国外订单',
                   u'就是电话是二五九七五菱三',
                   u'你好湖州中院',
                   u'~少数意见',
                   u'以及第二一份',
                   u'九月二十二号',
                   u'电源有限的对电源有限公司',
                   u'管委会~如果是到期了',
                   u'宋永泰的证言',
                   u'你好湖州中院',
                   u'一百三十八万',
                   u'不可能是一样',
                   u'二五二五九七六五九六五九哎姓蔡蔡法官',
                   u'六月二十四号',
                   u'那么四月十二号那个是三九二七六零元',
                   u'你可以你~',
                   u'~本案是三个',
                   u'呃零零五七二',
                   u'湖州中院您好',
                   u'九月二十三号',
                   u'我感觉~法院',
                   u'呢个和国贸方',
                   u'江湖的江曲江',
                   u'所协的条件就管委会来承担',
                   u'他重整重整了',
                   u'六零年开富了六一年那时共产党尽管',
                   u'哦就摆起了嘛那个时候那个时候摆起啦',
                   u'那么根据创意经济在一审时那么结果是',
                   u'身份证号五一一五二二一九八二零七零四零二XX',
                   u'但是即使是拍了照手机',
                   u'张水金是吧稍微等一下啊',
                   u'~自由畅快的听觉享受',
                   u'~房租合同~就~规定呢',
                   u'二五二二七零九是吧哎对',
                   u'当事人叫什么名字月月良',
                   u'三万九千九百一十一元',
                   u'四万一千一百五十七元',
                   u'~额这个报告里边书写到',
                   u'他都依法告知我东阳法院给的我这个案号二零一七浙零一三八',
                   u'~尤其是对江苏法院更是如此',
                   u'嗯二零一七浙零五零六幺五七八号',
                   u'~给温州市温州市温州市~',
                   u'当事人叫李金发木子李金银铜铁的金',
                   u'二五九七多少多少全号五七三五七三',
                   u'赵龙给你讲没有他在和任德全合伙做工程呢', ]
    # print get_base_number(u'亿')
    # print get_number(u'一')
    # print format_text_to_number(u'三千叁佰三十三asdjflaskfjk')

    for t_s in text_string:
        print t_s, '==', format_sentence(t_s)
    #
    # print format_sentence(u'二六六四万二')
    # # print format_sentence(u'四万')
    # print format_sentence(u'是一万三千二百六十七块四毛三')
    # print format_sentence(u'三万零二百四')
    # print format_sentence(u'三万零二百零四')
    # print format_sentence(u'四十')
    # print format_sentence(u'现在是十四亿人')
    # print format_text_to_number(u'{} '.format(u'十一'))

    # chinese_num = '一二三四五六七八九十'
    # for c_n in chinese_num:
    #     print repr(c_n)
    #
    # print ''.join([repr(c_n).replace('u', '').replace('\'', '').replace('\\', '\\u') for c_n in chinese_num])
    # re_rule = ur'([零一二三四五六七八九十百千万壹贰叁肆伍陆柒捌玖拾佰仟亿]+亿)?零?([一二三四五六七八九十百千壹贰叁肆伍陆柒捌玖拾佰仟]+万)?零?([一二三四五六七八九十百壹贰叁肆伍陆柒捌玖拾佰][千仟])?零?([一二三四五六七八九十壹贰叁肆伍陆柒捌玖拾][百佰])?零?([一二三四五六七八九壹贰叁肆伍陆柒捌玖]?[十拾])?零?([一二三四五六七八九壹贰叁肆伍陆柒捌玖])?'
    # result = re.finditer(re_rule, u'二百二')
    # counter = 0
    # for p in result:
    #     print counter, p.group()
    #     counter += 1
