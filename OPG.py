alphabet = "QWERTYUIOPASDFGHJKLZXCVBNM"


class Rule:
    rules = []
    matrix = []
    cnt = 0

    @classmethod
    def clear(cls):
        cls.rules = []
        cls.matrix = []
        cls.cnt = 0
        Ut.symbols = {}
        Ut.cnt = 0
        Vt.symbols = {}
        Vt.cnt = 0

    @classmethod
    def find(cls, rule):
        try:
            id = cls.rules.idex(rule)
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
        for i in range(Vt.cnt):
            cls.matrix[i][Vt.cnt] = '>'
            cls.matrix[Vt.cnt][i] = '<'
        cls.matrix[Vt.cnt][Vt.cnt] = '='
        Vt.add('#')

    @classmethod
    def get_matrix(cls):
        cls.matrix = [[' ' for i in range(Vt.cnt+1)] for j in range(Vt.cnt+1)]
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

if __name__ == '__main__':
    Rule.add(('E', 'E+T | T'))
    Rule.add(('T', 'T*F | F'))
    Rule.add(('F', '(E) | i'))
    #Rule.add(('F', '(I) | I'))
    #Rule.add(('I', '1|2|3|4|5|6|7|8|9|0'))
    Rule.parse()
    print(list(Vt.symbols.keys()))
    for role in Rule.matrix:
        print(role)