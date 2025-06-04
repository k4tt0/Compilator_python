from typing import Optional
from tokens import *

class Type:
    def __init__(self, tb=None, s=None, n=-1):
        self.tb = tb    # type base (TB_INT, TB_DOUBLE, etc)
        self.s = s      # struct definition for TB_STRUCT
        self.n = n      # >0 array of given size, 0=array without size, <0 non array

    def copy(self):
        return Type(self.tb, self.s, self.n)

class Symbol:
    def __init__(self, name, kind):
        self.name = name
        self.kind = kind
        self.type = Type()
        self.mem = None  # MEM_GLOBAL, MEM_ARG, MEM_LOCAL
        self.depth = 0   # 0-global, 1-in function, 2... - nested blocks
        self.owner = None
        self.varIdx = None
        self.paramIdx = None
        self.fn = type('Fn', (), {'params': None, 'locals': None, 'extFnPtr': None})()
        self.structMembers = None
        self.next = None

class Domain:
    def __init__(self, parent=None):
        self.symbols = None  # linked list of symbols
        self.parent = parent

# Global symbol table
symTable = Domain()
crtDepth = 0  # Current block depth

def initSymbol(symbol, name, kind):
    """Initialize a symbol with basic properties"""
    symbol.name = name
    symbol.kind = kind
    symbol.depth = crtDepth
    return symbol

def newSymbol(name, kind):
    """Create a new symbol with given name and kind"""
    s = Symbol(name, kind)
    s.type = Type()
    return initSymbol(s, name, kind)

def dupSymbol(symbol):
    """Create a deep copy of a symbol"""
    if not symbol:
        return None
    s = Symbol(symbol.name, symbol.kind)
    s.type = symbol.type.copy() if symbol.type else Type()
    s.mem = symbol.mem
    s.depth = symbol.depth
    s.owner = symbol.owner
    s.varIdx = symbol.varIdx
    s.paramIdx = symbol.paramIdx
    return s

def addSymbolToList(lst, symbol):
    """Add a symbol to a linked list"""
    symbol.next = lst
    return symbol

def deleteSymbolsAfter(start_symbol):
    """Delete all symbols after the given symbol in current domain"""
    if not start_symbol:
        symTable.symbols = None
        return
    current = symTable.symbols
    while current and current != start_symbol:
        current = current.next
    if current:
        current.next = None

def symbolsLen(symbols):
    """Count symbols in a linked list"""
    count = 0
    while symbols:
        count += 1
        symbols = symbols.next
    return count

def findSymbolInList(lst, name):
    """Find symbol by name in a linked list"""
    while lst:
        if lst.name == name:
            return lst
        lst = lst.next
    return None

def typeBaseSize(t):
    """Get size of a base type"""
    if t is None or t.tb is None:
        return 0
    if t.tb == TB_INT:
        return 4
    if t.tb == TB_DOUBLE:
        return 8
    if t.tb == TB_CHAR:
        return 1
    if t.tb == TB_VOID:
        return 0
    # TB_STRUCT case
    size = 0
    m = t.s.structMembers if t.s else None
    while m:
        size += typeSize(m.type)
        m = m.next
    return size

def typeSize(t):
    """Get total size of a type (including arrays)"""
    if t is None:
        return 0
    if t.n < 0:  # non-array
        return typeBaseSize(t)
    if t.n == 0:  # pointer
        return 8
    return t.n * typeBaseSize(t)

def addSymbolToDomain(domain, symbol):
    """Add symbol to domain, maintaining proper linking"""
    if domain.symbols is None:
        domain.symbols = symbol
    else:
        symbol.next = domain.symbols
        domain.symbols = symbol
    return symbol

def findSymbolInDomain(domain, name):
    """Find symbol in specific domain (right-to-left search)"""
    s = domain.symbols
    while s:
        if s.name == name:
            return s
        s = s.next
    return None

def findSymbol(name):
    """Find symbol in current domain or parent domains"""
    d = symTable
    while d:
        s = findSymbolInDomain(d, name)
        if s:
            return s
        d = d.parent
    return None

def pushDomain():
    """Create new domain scope"""
    global symTable, crtDepth
    d = Domain(symTable)
    symTable = d
    crtDepth += 1
    return d

def dropDomain():
    """Remove current domain scope"""
    global symTable, crtDepth
    d = symTable
    symTable = d.parent
    crtDepth -= 1

def addFn(name, retType):
    """Add function to symbol table"""
    fn = newSymbol(name, SK_FN)
    fn.type = retType if retType else Type()
    addSymbolToDomain(symTable, fn)
    return fn

def addExtFn(name, extFnPtr, retType):
    """Add external function to symbol table"""
    fn = addFn(name, retType)
    fn.fn.extFnPtr = extFnPtr
    return fn

def addFnParam(fn, name, typ):
    """Add parameter to function"""
    param = newSymbol(name, SK_PARAM)
    param.type = typ if typ else Type()
    param.mem = MEM_ARG
    param.paramIdx = symbolsLen(fn.fn.params)
    fn.fn.params = addSymbolToList(fn.fn.params, dupSymbol(param))
    return param

def showSymbols():
    """Display all symbols in symbol table"""
    def showSymbol(s):
        kind = s.kind
        mem = s.mem if s.mem else "N/A"
        type_str = f"{s.type.tb}"
        if s.type.n >= 0:
            type_str += f"[{s.type.n}]"
        print(f"Name: {s.name:<15} Kind: {kind:<10} Mem: {mem:<10} Type: {type_str}")

    def showDomain(d, level=0):
        s = d.symbols
        while s:
            print("  " * level, end="")
            showSymbol(s)
            s = s.next
        if d.parent:
            showDomain(d.parent, level + 1)

    print("\nSymbol Table Contents:")
    print("-" * 60)
    showDomain(symTable)
    print("-" * 60)