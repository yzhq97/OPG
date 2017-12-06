alphabet = "QWERTYUIOPASDFGHJKLZXCVBNM"


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
            procedure.append((symstk, cmp, src[piv], src[piv + 1:]))
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
                                    procedure.append((symstk, cmp, vt2['symbol'], src[piv+1:]))
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
                                    procedure.append((symstk, cmp, vt2['symbol'], src[piv+1:]))
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
                procedure.append((symstk, 'error', vt2['symbol'], src[piv+1:]))
                return procedure;

            if src[piv]=='#' and symstk[-1]==cls.starter:
                procedure.append((symstk + src[piv], '', '', ''))
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
    Rule.init('E')
    Rule.add(('E', 'E+T | E-T | T'))
    Rule.add(('T', 'T*F | T/F | F'))
    Rule.add(('F', '(E) | i'))
    Rule.parse()

    print('   ', end='')
    for i in range(Vt.cnt):
        print(' {0}  '.format(Vt.ids[i]), end=' ')
    print()
    for i in range(Vt.cnt):
        print(Vt.ids[i], end=' ')
        print(Rule.matrix[i])

    print()

    s = '(i*i)'
    print(s)
    procedure = Rule.analyze(s)

    for role in procedure:
        print(role)