from tokens import *
from Lexer import Token

tokens = []             # the list of tk
iTk = None              # current token, index in tk list
consumedTk = None       # last consumed tk
owner = None            # current symbol owner, funct/struct


#prints error messg with current line numn n exits progr
def tkerr(fmt, *args):  
    import sys
    print(f"Error at line {tokens[iTk].line}: {fmt % args}", file = sys.stderr)
    sys.exit(1)


#checks if current tk matched the expected code: y-advances n returns True / n-returns false
def consume(code):      
    global iTk, consumedTk
    if iTk < len(tokens) and tokens[iTk].code == code:
        consumedTk = tokens[iTk]
        iTk += 1
        return True
    return False


#entering point 4 parsing
def parse(token_list):
    global tokens, iTk
    tokens = token_list
    iTk = 0
    if not unit():
        tkerr("Syntax error")
    print("Syntax ok")


#top lvl grammar rule
def unit():
    global iTk
    while True:
        if structDef():
            pass
        elif fnDef():
            pass
        elif varDef():
            pass
        else:
            break
    if consume(END):
        return True
    return False


#parse a struct def
def StructDef():
    global iTk, owner
    tk = iTk
    if consume(STRUCT):
        if consume(ID):
            tkName = consumedTk
            if consume(LACC):
                s = findSymbolInDomain(symTable, tkName.text)
                if s:
                    tkerr("Symbol redefinition: %s", tkName.text)
                s = addSymbolToDomain(SymTable, newSymbol(tkName.text, SK_STRUCT))
                s.type.tb = TB_STRUCT
                s.type.s = s
                s.type.n = -1
                pushDomain()
                owner = s
                while True:
                    if varDef():
                        pass
                    else:
                        break
                if consume(RACC):
                    if consume(SEMICOLON):
                        owner = None
                        dropDomain()
                        return True
                    else:
                        tkerr("Missing semicolon after struct declaration")
                else:
                    tkerr("Missing \"}\" in struct declaration")
        else:
            tkerr("Missing/invalid struct identifier")
    iTk = tk
    return False


#parse variable def
def varDef():
    global iTk, owner
    tk = iTk
    t = Type()
    if typeBase(t):
        if consume(ID):
            tkName = consumedTk
            if arrayDecl(t):
                if t.n == 0:
                    tkerr("An array must have a specif dimension")
            
            if consume(SEMICOLON):
                var = findSymbolInDomain(SymTable, tkName.text)
                if var:
                    tkerr("Symbol redefinition: %s", tkName.text)
                var = newSymbol(tkName.text, SK_VAR)
                var.type = t
                var.owner = owner
                addSymbolToDomain(symTable, var)
                if owner:
                    if owner.kind == SK_FN:
                        var.varIdx = symbolsLen(owner.fn.locals)
                        addSymbolToList(owner.StructMembers, dupSymbol(var))
                    elif owner.kind == SK_STRUCT:
                        var.varIdx = typeSize(owner.type)
                        addSymbolToList(Owner.structMembers, dupSymbol(var))
                else:
                    var.varMem = safeAlloc(typeSize(t))
                return True
            else:
                tkerr("Missing semicolon after variable declaration")
        else:
            tkerr("Missing/invalid identifierafter base type")
    iTk = tk
    return False


#parse the base type of a var/struct membr
def typeBase(t):
    t.n = -1
    if consume(TYPE_INT):
        t.tb = TB_INT
        return True
    if consume(TYPE_DOUBLE):
        t.tb = TB_DOUBLE
        return True
    if consume(TYPE_CHAR):
        t.tb = TB_CHAR
        return True
    if consume(STRUCT):
        if consume(ID):
            tkName = consumedTk
            t.tb = TB_STRUCT
            t.s = findSymbol(tkName.text)
            if not t.s:
                tkerr("Undefined struct: %s", tkName.text)
            return True
        else:
            tkerr("Missing struct indentifier") 
    return False

#parse an array declaration
def arrayDecl(t):
    if consume(LBRACKET):
        if consume(INT):
            tkSize = consumedTk
            t.n = tkSize.i
        else:
            t.n = 0
        if consume(RBRACKET):
            return True
        else:
            tkerr("Missing \"]\" for array declaration") 
    return False

def fnDef():
    global iTk, owner
    tk = iTk
    t = Type()
    consumedVoidTk = False
    if typeBase(t) or (consumedVoidTk := consume(VOID)):
        if consumedVoidTk:
            t.tb = TB_VOID
        if consume(ID):
            tkName = consumedTk
            if consume(LPAR):
                fn = findSymbolInDomain(symTable, tkName.text)
                if fn:
                    tkerr("Symbol redefinition: %s", tkName.text)
                fn = newSymbol(tkName.text, SK_FN)
                fn.type = t
                addSymbolToDomain(symTable, fn)
                owner = fn
                pushDomain()
                if fnParam():
                    while consume(COMMA):
                        if not fnParam():
                            tkerr("Missing/invalid additional funct param after comma")

                if consume(RPAR):
                    if stmCompound(False):
                        dropDomain()
                        owner = None
                        return True
                    else:
                        tkerr("Missing funct body in function def")
                else:
                    tkerr("Missing \")\" in funct signature")
        else:
            tkerr("Missing/invalid identif after base type")
    iTk = tk
    return False


def fnParam():
    global iTk
    tk = iTk
    t = Type()
    if typeBase(t):
        if consume(ID):
            tkName = consumedTk
            if arrayDecl(t):
                t.n = 0
            
            param = findSymbolInDomain(symTable, tkName.text)
            if param:
                tkerr("Symbol redefinition: %s", tkName.text)
            param = newSymbol(tkName.text, SK_PARAM)
            param.type = t
            param.owner = owner
            param.paramIdx = symbolsLen(owner.fn.params)
            addSymbolToDomain(symTable, param)
            addSymbolToList(owner.fn.params, dupSymbol(param))
            return True
        else:
            tkerr("Missing/invalid identif after base type")
    iTk = tk
    return False