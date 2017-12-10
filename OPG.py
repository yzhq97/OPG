alphabet = "ZQWERTYUIOPASDFGHJKLXCVBNM"


class Rule:
    rules = []
    matrix = []
    starter = ''
    cnt = 0

    @classmethod
    def init(cls, starter):
        cls.rules = []
        cls.matrix = []
        cls.cnt = 0
        cls.starter = starter
        Ut.symbols = {}
        Ut.cnt = 0
        Vt.symbols = {}
        Vt.cnt = 0
        cls.add(('Z', '#'+starter+'#'))

    @classmethod
    def find(cls, rule):
        try:
            id = cls.rules.index(rule)
            return id
        except:
            return -1

    @classmethod
    def add(cls, rule):
        left, right = rule
        left = left.replace(' ', '')
        right = right.replace(' ', '')
        if len(left) > 1 or not (left in alphabet):
            print('invalid rule')
            return
        rights = right.split('|')
        for right in rights:
            rule = (left, right)
            id = cls.find(rule)
            if id == -1:
                cls.rules.append(rule)
                cls.cnt += 1

    @classmethod
    def parse(cls):
        # register Uts and Vts
        for rule in cls.rules:
            left, right = rule
            Ut.add(left)
            for i in range(len(right)):
                if right[i] in alphabet:
                    Ut.add(right[i])
                else:
                    Vt.add(right[i])

        # compute matrix
        Ut.get_first_vt()
        Ut.get_last_vt()
        cls.get_matrix()
        Vt.get_neighbor_ut()

    @classmethod
    def get_matrix(cls):
        cls.matrix = [[' ' for i in range(Vt.cnt)] for j in range(Vt.cnt)]
        for rule in cls.rules:
            left, x = rule
            for i in range(len(x)-1):
                if x[i] in Vt.symbols and x[i+1] in Vt.symbols:
                    v1 = Vt.get(x[i])['id']
                    v2 = Vt.get(x[i+1])['id']
                    cls.matrix[v1][v2] = '='
                    cls.matrix[v2][v1] = '='
                if i < len(x)-2:
                    if x[i] in Vt.symbols and x[i+1] in Ut.symbols and x[i+2] in Vt.symbols:
                        v1 = Vt.get(x[i])['id']
                        v2 = Vt.get(x[i+2])['id']
                        cls.matrix[v1][v2] = '='
                        cls.matrix[v2][v1] = '='
                if x[i] in Vt.symbols and x[i+1] in Ut.symbols:
                    U = Ut.get(x[i+1])
                    v1 = Vt.get(x[i])
                    for vsym in U['firstvt']:
                        v2 = Vt.get(vsym)
                        cls.matrix[v1['id']][v2['id']] = '<'
                if x[i] in Ut.symbols and x[i+1] in Vt.symbols:
                    U = Ut.get(x[i])
                    v1 = Vt.get(x[i+1])
                    for vsym in U['lastvt']:
                        v2 = Vt.get(vsym)
                        cls.matrix[v2['id']][v1['id']] = '>'

    @classmethod
    def compare(cls, vt1, vt2):
        vt1 = Vt.get(vt1)
        vt2 = Vt.get(vt2)
        return cls.matrix[vt1['id']][vt2['id']]

    @classmethod
    def analyze(cls, src):
        procedure = []
        src = src + '#'
        piv = 0
        symstk = '#'
        genstk = []

        while True:
            cmp = cls.compare(symstk[-1], src[piv])
            procedure.append((symstk, cmp, src[piv], src[piv + 1:], 'move in'))
            if cmp == '<':
                genstk.append(len(symstk))
                symstk += src[piv]
                piv += 1

            elif cmp == '>':
                generalized = False
                while len(genstk) > 0:
                    genstart = genstk[-1]
                    gen = symstk[genstart:]
                    vt1 = Vt.get(symstk[genstart-1])
                    vt2 = Vt.get(src[piv])
                    found = False
                    if cls.compare(vt1['symbol'], vt2['symbol']) == '<':
                        if 'prevut' in vt2:
                            for rule in Rule.rules:
                                left, right = rule
                                if right == gen:
                                    found = True
                                    symstk = symstk[:genstart] + left
                                    procedure.append((symstk, cmp, vt2['symbol'], src[piv+1:], 'generalize'))
                                    if left == vt2['prevut']:
                                        generalized = True
                                    break
                    elif cls.compare(vt1['symbol'], vt2['symbol']) in '>=':
                        if 'nextut' in vt1:
                            for rule in Rule.rules:
                                left, right = rule
                                if right == gen:
                                    found = True
                                    symstk = symstk[:genstart] + left
                                    procedure.append((symstk, cmp, vt2['symbol'], src[piv+1:], 'generalize'))
                                    if left == vt1['nextut']:
                                        genstk.pop()
                                    break

                    if generalized or not found:
                        if piv+1 < len(src):
                            symstk += src[piv]
                            piv += 1
                        break
            else:
                print('error')
                procedure.append((symstk, 'err', vt2['symbol'], src[piv+1:], 'error'))
                return procedure;

            if src[piv]=='#' and symstk[-1]==cls.starter:
                procedure.append((symstk + src[piv], '', '', '', 'finish'))
                break

        return procedure


class Ut:
    symbols = {}
    ids = []
    cnt = 0
    fv = None
    lv = None

    @classmethod
    def add(cls, symbol):
        if not symbol in cls.symbols:
            sym = {}
            sym['symbol'] = symbol
            sym['id'] = cls.cnt
            sym['firstvt'] = []
            sym['lastvt'] = []
            cls.cnt += 1
            cls.symbols[symbol] = sym
            cls.ids.append(symbol)

    @classmethod
    def get(cls, symbol):
        return cls.symbols[symbol]

    @classmethod
    def get_first_vt(cls):
        cls.fv = [[0 for i in range(Vt.cnt)] for j in range(Ut.cnt)]
        stack = []

        for rule in Rule.rules:
            left, right = rule
            U = Ut.get(left)
            if right[0] in Vt.symbols:
                b = Vt.get(right[0])
                if cls.fv[U['id']][b['id']] == 0:
                    cls.fv[U['id']][b['id']] = 1
                    stack.append((U, b));
            elif len(right) > 1 and right[1] in Vt.symbols:
                b = Vt.get(right[1])
                if cls.fv[U['id']][b['id']] == 0:
                    cls.fv[U['id']][b['id']] = 1
                    stack.append((U, b));
        while len(stack) > 0:
            V, b = stack.pop()
            for rule in Rule.rules:
                left, right = rule
                U = Ut.get(left)
                if right[0] == V['symbol']:
                    if cls.fv[U['id']][b['id']] == 0:
                        cls.fv[U['id']][b['id']] = 1
                        stack.append((U, b));

        for i in range(Ut.cnt):
            for j in range(Vt.cnt):
                if cls.fv[i][j] == 1:
                    U = Ut.ids[i]
                    V = Vt.ids[j]
                    Ut.symbols[U]['firstvt'].append(V)

    @classmethod
    def get_last_vt(cls):
        cls.lv = [[0 for i in range(Vt.cnt)] for j in range(Ut.cnt)]
        stack = []

        for rule in Rule.rules:
            left, right = rule
            U = Ut.get(left)
            if right[-1] in Vt.symbols:
                b = Vt.get(right[-1])
                if cls.lv[U['id']][b['id']] == 0:
                    cls.lv[U['id']][b['id']] = 1
                    stack.append((U, b));
            elif len(right) > 1 and right[-2] in Vt.symbols:
                b = Vt.get(right[-2])
                if cls.lv[U['id']][b['id']] == 0:
                    cls.lv[U['id']][b['id']] = 1
                    stack.append((U, b));
        while len(stack) > 0:
            V, b = stack.pop()
            for rule in Rule.rules:
                left, right = rule
                U = Ut.get(left)
                if right[-1] == V['symbol']:
                    if cls.lv[U['id']][b['id']] == 0:
                        cls.lv[U['id']][b['id']] = 1
                        stack.append((U, b));

        for i in range(Ut.cnt):
            for j in range(Vt.cnt):
                if cls.lv[i][j] == 1:
                    U = Ut.ids[i]
                    V = Vt.ids[j]
                    Ut.symbols[U]['lastvt'].append(V)


class Vt:
    symbols = {}
    cnt = 0
    ids = []

    @classmethod
    def add(cls, symbol):
        if not symbol in cls.symbols:
            sym = {}
            sym['symbol'] = symbol
            sym['id'] = cls.cnt
            cls.cnt += 1
            cls.symbols[symbol] = sym
            cls.ids.append(symbol)

    @classmethod
    def get(cls, symbol):
        return cls.symbols[symbol]

    @classmethod
    def get_neighbor_ut(cls):
        for rule in Rule.rules:
            left, right = rule
            l = len(right)
            for i in range(l):
                if right[i] in Vt.symbols:
                    if i > 0:
                        if right[i-1] in Ut.symbols:
                            Vt.symbols[right[i]]['prevut'] = right[i-1]
                    if i < l-1:
                        if right[i+1] in Ut.symbols:
                            Vt.symbols[right[i]]['nextut'] = right[i+1]

if __name__ == '__main__':
    print('请输入开始符号，开始符号是规约的最终目标，必须出现在后面的语法中')
    starter = input()
    Rule.init(starter)
    print()

    print('请输入产生式，一行输入一条产生式')
    print('大写字母为非终结符,Z不能使用,其他为终结符')
    print('产生式用->分隔，输入一个#表示结束')
    while True:
        rule_str = input()
        if rule_str == '#':
            break
        sep = rule_str.index('->')
        left = rule_str[:sep]
        right = rule_str[sep+2:]
        rule = (left, right)
        Rule.add(rule)
    print()

    Rule.parse()

    print('非终结符:')
    for key in Ut.symbols:
        if not key=='Z':
            U = Ut.symbols[key]
            print('{0}'.format(key))
            print('firstvt: {0}'.format(' '.join(U['firstvt'])))
            print('lastvt: {0}'.format(' '.join(U['lastvt'])))
            print()
    print()

    print('终结符优先矩阵:')
    print('  ', end='')
    for i in range(Vt.cnt):
        print(' {0}'.format(Vt.ids[i]), end=' ')
    print()
    for i in range(Vt.cnt):
        print(Vt.ids[i], end=' ')
        for j in range(Vt.cnt):
            print(' {0} '.format(Rule.matrix[i][j]), end='')
        print()
    print()

    while True:
        print('请输入要分析的符号串，输入一个#表示退出')
        str = input()
        if str == '#':
            break
        procedure = Rule.analyze(str)
        fmt = '| {0:15s} | {1:3s} | {2:2s} | {3:15s} | {4:10s} |'
        print(fmt.format('stack', 'cmp', 'nx', 'remaining', 'operation'))
        for role in procedure:
            print(fmt.format(role[0], role[1], role[2], role[3], role[4]), end='')
            print()
        print()


