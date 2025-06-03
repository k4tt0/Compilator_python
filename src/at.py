from an import Type

class Ret:
    def __init__(self, typ=None, lval=False, ct=False):
        if typ is None:
            self.type = Type()
        else:
            self.type = typ
        self.lval = lval
        self.ct = ct

def canBeScalar(r:Ret):
    t = r.type
    if t.n >= 0:
        return False
    if t.tb == 'TB_VOID':
        return False
    return True

def convTo(src: Type, dst: Type):
    if src.n >= 0:
        if dst.n >= 0:
            return True
        return False
    if dst.n >= 0:
        return False
    if src.tb in ('TB_INT', 'TB_DOUBLE', 'TB_CHAR'):
        if dst.tb in ('TB_INT', 'TB_DOUBLE', 'TB_CHAR'):
            return True
        return False
    if src.tb == 'TB_STRUCT':
        return dst.tb == 'TB_STRUCT' and src.s == dst.s
    return False

def arithTypeTo(t1: Type, t2:Type, dst:Type):
    if t1.n >= 0 or t2.n >= 0:
        return False
    dst.s = None
    dst.n = -1
    if t1.tb == 'TB_INT':
        if t2.tb in ('TB_INT', 'TB_CHAR'):
            dst.tb = 'TB_INT'
            return True
        if t2.tb == 'TB_DOUBLE':
            dst.tb = 'TB_DOUBLE'
            return True
        return False
    if t1.tb == 'TB_DOUBLE':
        if t2.tb in ('TB_INT', 'TB_DOUBLE', 'TB_CHAR'):
            dst.tb = 'TB_DOUBLE'
            return True
        return False
    if t1.tb == 'TB_CHAR':
        if t2.tb in ('TB_INT', 'TB_DOUBLE', 'TB_CHAR'):
            dst.tb = t2.tb
            return True
        return False
    return False

def findSymbolInList(lst, name):
    while lst:
        if lst.name == name:
            return lst
        lst = lst.next
    return None
