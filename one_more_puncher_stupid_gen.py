# 生成 one_more_puncher_stupid 的句库 + 谐音表，写进 HTML 里 /*@@DATA*/ ... /*@@END*/ 之间
import json, re, sys
from collections import Counter
from pypinyin import pinyin, Style

DICT = sys.argv[1]
HTML = sys.argv[2]

# 句库：(句子, 权重)。这些是"答案"，不会显示在页面上
BANKS = {
  'luxun': [  # 树人模式：鲁迅《狂人日记》(1918)
    ('吃人', 3), ('满本都写着两个字是吃人', 2), ('从来如此，便对么', 2.5), ('救救孩子', 2.5),
    ('仁义道德', 1.5), ('我翻开历史一查', 1.5), ('横竖睡不着', 2), ('他们想要吃我了', 2),
    ('我也是人，他们想要吃我了', 2), ('今天晚上，很好的月光', 1.5), ('我怕得有理', 1.5),
    ('没有吃过人的孩子，或者还有', 1.5), ('你们可以改了，从真心改起', 1.2), ('吃人的人', 2),
    ('赵家的狗，何以看我两眼呢', 1.5), ('早上小心出门', 1.2), ('凡事须得研究，才会明白', 1.2),
    ('这就是吃人的家伙', 1.5), ('四千年来时时吃人的地方', 1.2), ('有了四千年吃人履历的我', 1.2),
    ('不能想了', 1.2), ('难见真的人', 1.5), ('他们会吃我', 1.5), ('自己想吃人，又怕被别人吃了', 1.5),
  ],
  'bro': [  # 暂时只有一个很小的词典
    ('神鬼军师', 2), ('倒吊', 2),
  ],
  'sanguo': [  # 新三国台词梗（萌娘百科 / 新三国 Wiki）
    ('龙，可是帝王之征啊', 3), ('我就扎聋我自己的耳朵', 3), ('战至最后一刻，自刎归天', 3),
    ('三军听令，自刎归天', 2.5), ('自尽便是懦夫', 2), ('这江东到底你是主还是我是主', 2),
    ('主公喜欢已婚少妇', 2), ('这雷把我吓死了', 2), ('生死不明？那就是死了', 2),
    ('不可能，我二弟天下无敌', 2), ('太阳从西边升起', 2), ('了不起，一开口便是大实话', 2),
    ('万万没有此事', 2), ('是啊，吃什么', 2), ('世人昨日看错了我，今日又看错了', 1.5),
    ('但我依然是我', 1.5), ('你们是来打仗的还是来调情的', 2), ('国贼董卓嘛', 1.5),
    ('今天不是老夫的生日，而是老夫的忌日', 2), ('不要惊动了巡夜的鹰犬', 1.5), ('天意啊，全是天意啊', 2),
    ('恭喜爹可以称帝了', 2), ('回去吧，你太老了', 2), ('关某的大刀不斩老幼', 1.5), ('当浮一大白', 1.5),
    ('抱歉，我的脑袋太贵', 2), ('是这个乱世害了你呀', 2), ('我那些个蛐蛐个个有情有义', 1.5),
    ('捅他一万个透明窟窿', 1.5), ('我的大斧早就饥渴难耐了', 1.5), ('听你讲话如饮美酒', 1.5),
    ('这就不奇怪了', 1.5), ('还是个长不大的孩子啊', 1.5), ('妖妇，你休得放肆', 2),
    ('徐州城不愧为中原第一雄关', 1.2), ('放肆，胆敢搜我的身我砍你的头', 1.5), ('兵法教出来的都是呆子', 1.5),
    ('先生真乃奇人也', 1.5), ('历史发生了剧变', 1.2), ('我不能走啊！云长！', 1.5),
    ('医死的人越多，医术越高明', 1.5), ('不要愤怒，愤怒会降低你的智慧', 1.2), ('可别逼我使出无情剑', 1.5),
    ('接着奏乐接着舞', 1.5), ('来，换大盏', 1.2), ('那好啊，他过江我也过江', 1.5),
    ('死是凉爽的夏夜，可供人无忧的安眠', 1.2), ('莫非朕不知兵吗', 1.5), ('信中言语近乎恳求', 1.2),
    ('好火啊，比夷陵之火还好啊', 1.5), ('一对笑面虎，两头乌角鲨', 1.2), ('车轮底下的野草，石头缝里的黄连', 1.2),
    ('老夫回答你之前，也有一事想请问足下', 1.2), ('咱家说了咱家不怕酸', 1.5),
    ('只当是陈宫从来就没有这些', 1.2), ('你是何人', 1.5), ('五百校刀手', 1.2),
  ],
}

# 常用字：按词频累计，取前 3500
freq = Counter()
for line in open(DICT, encoding='utf-8'):
    w, f = line.split()[:2]
    for c in w:
        if '一' <= c <= '鿿':
            freq[c] += int(f)
common = [c for c, _ in freq.most_common(3500)]
rank = {c: i for i, c in enumerate(common)}

def tone3(c):
    return pinyin(c, style=Style.TONE3)[0][0]
by_tone, by_syl = {}, {}
for c in common:
    t = tone3(c)
    s = re.sub(r'\d', '', t)
    by_tone.setdefault(t, []).append(c)
    by_syl.setdefault(s, []).append(c)

# 句库里每个字在上下文中的读音 → 同音字（同调在前）
homo = {}
for mode, bank in BANKS.items():
    for sent, _ in bank:
        rd = pinyin(sent, style=Style.TONE3)
        for c, r in zip(sent, rd):
            if not ('一' <= c <= '鿿'):
                continue
            t = r[0]; s = re.sub(r'\d', '', t)
            same = [x for x in by_tone.get(t, []) if x != c][:18]
            other = [x for x in by_syl.get(s, []) if x != c and x not in same][:10]
            a, b = homo.get(c, ('', ''))
            a += ''.join(x for x in same if x not in a)
            b += ''.join(x for x in other if x not in b and x not in a)
            homo[c] = (a, b)
# 用词频词典做正向最大匹配分词，句库存成 "词/词/词"，片段只能在词边界上起止
words = set()
for line in open(DICT, encoding='utf-8'):
    w, f = line.split()[:2]
    if 2 <= len(w) <= 4 and int(f) >= 20: words.add(w)
def seg(sent):
    out, i = [], 0
    while i < len(sent):
        for L in (4, 3, 2, 1):
            if L == 1 or sent[i:i+L] in words:
                out.append(sent[i:i+L]); i += L; break
    return '/'.join(out)
BANKS = {m: [[seg(t), w] for t, w in b] for m, b in BANKS.items()}

homo_str = ';'.join(f'{c}{a}|{b}' for c, (a, b) in sorted(homo.items()))

data = ('const BANKS = ' + json.dumps(BANKS, ensure_ascii=False) + ';\n'
        + 'const HOMO_RAW = ' + json.dumps(homo_str, ensure_ascii=False) + ';\n')
html = open(HTML, encoding='utf-8').read()
html = re.sub(r'/\*@@DATA\*/.*?/\*@@END\*/', lambda m: '/*@@DATA*/\n' + data + '/*@@END*/', html, flags=re.S)
open(HTML, 'w', encoding='utf-8').write(html)
print('homo chars', len(homo), 'data bytes', len(data.encode()))
