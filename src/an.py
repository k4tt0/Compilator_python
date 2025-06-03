from typing import Optional

# Symbol table n Type system

class Type:
    def __init__(self, tb = None, s = None, n = -1):
        self.tb = tb    # type base (TB_INT, TB_DOUBLE, etc)
        self.s = s      # struct symbol (TB_STRUCTURE)
        self.n = n      # array size (-1 - scalar, 0 - pointer)

class Symbol:
    def __init__(self, name, kind):
        self.name = name
        self.kind = kind
        self.type = None
        self.owner = None
        self.varIdx = None
        self.varMem = None
        self.paramIdx = None
        self.fn = type('Fn', (), {'params': None, 'locals': None, 'extFnPtr': None})()
        self.structMembers = None
        self.next = None

class Domain:
    def __init__(self, parent = None):
        self.symbols = None
        self.parent = parent

symTable = Domain()

def typeBaseSize(t: Type):
    if t.tb == 'TB_INT':
        return 4
    if t.tb == 'TB_DOUBLE':
        return 8
    if t.tb == 'TB_CHAR':
        return 1
    if t.tb == 'TB_VOID':
        return 0
    
    # TB_STRUCT
    size = 0
    m = t.s.structMembers if t.s else None
    while m: 
        size += typeSize(m.type)
        m = m.next
    return size

def typeSize(t: Type):
    if t.n < 0:
        return typeBaseSize(t)
    if t.n == 0:
        return 8    # pointer size
    return t.n * typeBaseSize(t)

def newSymbol(name, kind):
    return Symbol(name, kind)

def dupSymbol(symbol):
    import copy
    s = copy.deepcopy(symbol)
    s.next = None
    return s

def addSymbolToList(lst, s):
    if lst is None:
        return s
    head = lst
    while lst.next:
        lst = lst.next
    lst.next = s
    return head

def symbolsLen(lst):
    n = 0
    while lst:
        n += 1
        lst = lst.next
    return n

def pushDomain():
    global symTable
    d = Domain(symTable)
    symTable = d
    return d

def dropDomain():
    global symTable
    d = symTable
    symTable = d.parent

def findSymbolInDomain(domain, name):
    s = domain.symbols
    while s:
        if s.name == name:
            return s
        s = s.next
    return None

def findSymbol(name):
    d = symTable
    while d:
        s = findSymbolInDomain(d, name)
        if s :
            return s
        d = d.parent
    return None

def addSymbolToDomain(domain, s):
    if domain.symbols is None:
        domain.symbols = s
    else:
        domain.symbols = addSymbolToList(domain.symbols, s)
    return s

def addExtFn(name, extFnPtr, retType):
    fn = newSymbol(name, 'SK_FN')
    fn.fn.extFnPtr = extFnPtr
    fn.type = retType
    addSymbolToDomain(symTable, fn)
    return fn

def addFnParam(fn, name, typ):
    param = newSymbol(name, 'SK_PARAM')
    param.type = typ
    param.paramIdx = symbolsLen(fn.fn.params)
    fn.fn.params = addSymbolToList(fn.fn.params, dupSymbol(param))
    return param

def findSymbolInList(lst, name):
    while lst:
        if lst.name == name:
            return lst
        lst = lst.next
    return None