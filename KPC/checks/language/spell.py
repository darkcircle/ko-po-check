# -*- coding: utf-8 -*-

import re
from KPC.classes import Error, BaseCheck

# 의존명사를 위한 -할 형태의 동사 모음
verbs_re = '(?:'+'|'.join([
    '가져올',
    '갈',
    '걸',
    '고칠'
    '나타날',
    '내릴',
    '놓일',
    '되돌릴',
    '만들',
    '바꿀',
    '보낼',
    '볼',
    '생길',
    '시킬',
    '쓸',
    '알',
    '얻어낼',
    '얻을',
    '없앨',
    '열',
    '올',
    '일',
    '읽어들일',
    '읽을',
    '있을',
    '잠글',
    '지울',
    '찾을',
    '할',
    ])+')'

# '~할 지'라고 잘못 띄어 쓸 때를 위해. 위 경우보다 더 넓은 범위에서 ㄹ 종성 모두를 잡는다.
eul_verbs_re = r'\w*(?:'+'|'.join(chr(c + ord('갈') - ord('가')) for c in range(ord('가'), ord('힣')+1, ord('개')-ord('가'))) + ')'

variations_re = '(있다|없다|있습니다|없습니다|있는|없는|있게|없게)'

# 조사 모음
josa_re = '(?:'+'|'.join([
    '가', '이', r'이\(가\)', r'가\(이\)', r'\(이\)가', r'\(가\)이',
    '를', '을', r'을\(를\)', r'를\(을\)', r'\(을\)를', r'\(를\)을',
    '는', '은', r'은\(는\)', r'는\(은\)', r'\(은\)는', r'\(는\)은',
    '와', '과', r'와\(과\)', r'과\(와\)',
    '로', '으로', r'\(으\)로',
    '로서', '으로서', r'\(으\)로서',
    '로써', '으로써', r'\(으\)로써',
    '로부터', '으로부터', r'\(으\)로부터',
    '라는', '이라는', r'\(이\)라는',
    '의', '도', '에', '에서', '만', '부터',
    ])+')'


def test_noun_suffix(str):
    if (str[-1] != '슴'):
        return 1
    elif ((ord(str[-2]) - 0xac00) % 28 == 20):
        return 0
    elif (str[-2] == '없'):
        return 0
    else:
        return 1

c_format = r'%(?:[1-9][0-9]*\$)?[-+ #\'0]*(?:[1-9][0-9]*)?(?:\.[0-9]+)?' \
           r'(?:(?:hh|h|j|l|L|ll|q|t|z|Z)?' \
           r'[dioufeEgGaAcCspnmhjlLqtxXzZ1-9]|hh|ll)'

unit_re = '(?:'+'|'.join([
    '분', '시간', '초'
    ])+')'


misspell_data = [
    {
        're':    re.compile(r'(않\s*(한|함|합니다|된|됨|됩니다))'),
        'error': '\"%s\": 짧은 부정문에서는 \'않\'이 아니라 \'안\'을 씁니다'
    },
    {
        're':    re.compile(r'((?<!모)읍니다)'),
        'error': '\"%s\": \'읍니다\'가 아니라 \'습니다\'입니다'
    },
    {
        're':    re.compile(r'([^\s]+슴)([\s\.\,\?]|$)'),
        'func':  test_noun_suffix,
        'error': '\"%s\": \'슴\'이 아니라 \'음\'입니다'
    },
    {
        're':    re.compile(r'('+verbs_re+r'수(가|도|는)?\s'+')'),
        'error': '\"%s\": 의존 명사는 띄어 써야 합니다'
    },
    {
        're':    re.compile(r'('+verbs_re+r'\s*수(있|없)'+')'),
        'error': '\"%s\": 의존 명사는 띄어 써야 합니다'
    },
    {
        're':    re.compile(r'('+verbs_re+r'때(가|도|는)?\s'+')'),
        'error': '\"%s\": \'~할 때\'라고 띄어 써야 합니다'
    },
    {
        're':    re.compile(r'(' + eul_verbs_re + ' 지' + r'(?:$|\.| 여부))'),
        'error': '\"%s\": 의문을 나타내는 \'~ㄹ지\'는 어미이므로 붙여 써야 합니다'
    },
    {
        're':    re.compile(r'([0-9A-Za-z-+\`\'\"\u2019\u201D()%_]+ ' +
                            josa_re + r')(?:$|\s)'),
        'error': '\"%s\": 조사는 체언에 붙여 써야 합니다'
    },
    {
        're':    re.compile(r'((?:' + c_format + '|[0-9]+) ' + unit_re + ')' +
                            '(?:' + josa_re + r')?\b'),
        'error': '\"%s\": 단위 명사는 숫자와 붙여 씁니다'
    },
]


class SpellCheck(BaseCheck):
    def check(self, entry, context):
        msgstr = entry.msgstr
        errors = []
        for data in misspell_data:
            misspell_re = data['re']
            misspell_error = data['error']
            s = msgstr
            while 1:
                mo = misspell_re.search(s)
                if mo:
                    if ('func' in data and data['func'](mo.group(1))):
                        s = s[mo.end():]
                        continue
                    errors.append(Error(misspell_error % mo.group(1)))
                    s = s[mo.end():]
                else:
                    break
        return errors

name = 'language/spell'
description = '흔히 하는 맞춤법 오류를 찾아냅니다'
checker = SpellCheck()
