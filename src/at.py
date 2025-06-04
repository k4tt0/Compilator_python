from typing import Optional
from tokens import *
from ad import Type, Symbol

class CtVal:
    def __init__(self):
        self.i = 0      # for int, char
        self.d = 0.0    # for double
        self.str = ""   # for char[]

class Ret:
    def __init__(self, typ=None, lval=False, ct=False):
        self.type = typ if typ else Type()  # type of the result
        self.lval = lval    # if it is a left value
        self.ct = ct        # if it is a constant value
        self.ctVal = CtVal()  # constant value storage

def canBeScalar(r: Ret) -> bool:
    """Check if a value can be used as a scalar"""
    if r is None or r.type is None:
        return False
    t = r.type
    if t.n >= 0:  # array check
        return False
    if t.tb == TB_VOID:
        return False
    return True

def convTo(src: Type, dst: Type) -> bool:
    """Check if src type can be converted to dst type"""
    if src is None or dst is None:
        return False
        
    # Array conversion rules
    if src.n >= 0:  # src is array
        if dst.n >= 0:  # dst is array
            return src.tb == dst.tb  # arrays must be of same base type
        return False  # can't convert array to non-array
    if dst.n >= 0:  # dst is array but src isn't
        return False  # can't convert non-array to array

    # Struct conversion rules
    if src.tb == TB_STRUCT:
        if dst.tb == TB_STRUCT:
            return src.s == dst.s  # must be same struct type
        return False
    if dst.tb == TB_STRUCT:
        return False

    # Scalar type conversion rules - following AtomC implicit conversion rules
    if src.tb == dst.tb:
        return True  # same types can convert
    
    # Type hierarchy: DOUBLE > INT > CHAR
    if dst.tb == TB_DOUBLE:
        return src.tb in (TB_INT, TB_CHAR)  # can convert to double
    if dst.tb == TB_INT:
        return src.tb == TB_CHAR  # can convert to int
    if dst.tb == TB_CHAR:
        return False  # cannot implicitly convert to char
        
    return False

def cast(dst: Type, src: Type) -> None:
    """Convert src type to dst type, raising error if impossible"""
    if src.n > -1:  # src is array
        if dst.n > -1:  # dst is array
            if src.tb != dst.tb:
                raise Exception("an array cannot be converted to an array of another type")
        else:
            raise Exception("an array cannot be converted to a non-array")
    else:  # src is scalar
        if dst.n > -1:  # dst is array
            raise Exception("a non-array cannot be converted to an array")
    
    if src.tb == TB_STRUCT:
        if dst.tb == TB_STRUCT:
            if src.s != dst.s:
                raise Exception("a structure cannot be converted to another one")
            return
        raise Exception("incompatible types")
    
    if src.tb in (TB_CHAR, TB_INT, TB_DOUBLE):
        if dst.tb in (TB_CHAR, TB_INT, TB_DOUBLE):
            return
    
    raise Exception("incompatible types")

def getArithType(t1: Type, t2: Type) -> Type:
    """Get resulting type from arithmetic operation between t1 and t2"""
    if t1 is None or t2 is None:
        raise Exception("invalid operand types")
        
    # Check for arrays and structs
    if t1.n > -1 or t2.n > -1:
        raise Exception("cannot perform arithmetic on arrays")
    if t1.tb == TB_STRUCT or t2.tb == TB_STRUCT:
        raise Exception("cannot perform arithmetic on structs")
    if t1.tb == TB_VOID or t2.tb == TB_VOID:
        raise Exception("cannot perform arithmetic on void type")
        
    # Result is the "largest" type
    result = Type()
    if t1.tb == TB_DOUBLE or t2.tb == TB_DOUBLE:
        result.tb = TB_DOUBLE
    elif t1.tb == TB_INT or t2.tb == TB_INT:
        result.tb = TB_INT
    elif t1.tb == TB_CHAR and t2.tb == TB_CHAR:
        result.tb = TB_CHAR
    else:
        raise Exception("invalid types for arithmetic")
    
    result.n = -1  # Result is always scalar
    return result

def arithTypeTo(t1: Type, t2: Type, dst: Type) -> bool:
    """Check and set arithmetic result type"""
    if t1 is None or t2 is None or dst is None:
        return False

    # Only allow arithmetic on scalar types
    if t1.n >= 0 or t2.n >= 0:
        return False
    if t1.tb == TB_STRUCT or t2.tb == TB_STRUCT:
        return False
    if t1.tb == TB_VOID or t2.tb == TB_VOID:
        return False

    # Set result type as the "largest" type
    if t1.tb == TB_DOUBLE or t2.tb == TB_DOUBLE:
        dst.tb = TB_DOUBLE
    elif t1.tb == TB_INT or t2.tb == TB_INT:
        dst.tb = TB_INT
    elif t1.tb == TB_CHAR and t2.tb == TB_CHAR:
        dst.tb = TB_CHAR
    else:
        return False

    dst.n = -1
    dst.s = None
    return True

def findSymbolInList(lst: Symbol, name: str) -> Optional[Symbol]:
    """Find symbol by name in a linked list"""
    while lst:
        if lst.name == name:
            return lst
        lst = lst.next
    return None