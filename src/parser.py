from tokens import *
from Lexer import Token
from ad import (
    Type, symTable, findSymbolInDomain, addSymbolToDomain, newSymbol,
    pushDomain, dropDomain, symbolsLen, addSymbolToList, dupSymbol, typeSize, findSymbol)
from at import Ret, canBeScalar, convTo, arithTypeTo, findSymbolInList


class ParserError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.iTk = 0
        self.consumedTk = None
        self.owner = None


    #prints error messg with current line numn n exits progr
    def tkerr(self, fmt, *args):  
        line = self.tokens[self.iTk].line if self.iTk < len(self.tokens) else '?'
        raise ParserError(f"Error at line {line}: {fmt % args}")


    #checks if current tk matched the expected code: y-advances n returns True / n-returns false
    def consume(self, code):      
        if self.iTk < len(self.tokens) and self.tokens[self.iTk].code == code:
            self.consumedTk = self.tokens[self.iTk]
            self.iTk += 1
            return True
        return False


    #entering point 4 parsing
    def parse(self):
        if not self.unit():
            self.tkerr("Syntax error")
        print("Syntax ok")


    #top lvl grammar rule
    def unit(self):
        while True:
            if self.structDef():
                continue
            elif self.fnDef():
                continue
            elif self.varDef():
                continue
            else:
                break
        return self.consume(END)


    #parse a struct def
    def structDef(self):
        tk = self.iTk
        if self.consume(STRUCT):
            if self.consume(ID):
                tkName = self.consumedTk
                if self.consume(LACC):
                    s = findSymbolInDomain(symTable, tkName.text)
                    if s:
                        self.tkerr("Symbol redefinition: %s", tkName.text)
                    s = addSymbolToDomain(symTable, newSymbol(tkName.text, SK_STRUCT))
                    s.type.tb = TB_STRUCT
                    s.type.s = s
                    s.type.n = -1
                    pushDomain()
                    self.owner = s
                    while self.varDef():
                        pass
                        
                    if self.consume(RACC):
                        if self.consume(SEMICOLON):
                            self.owner = None
                            dropDomain()
                            return True
                        else:
                            self.tkerr("Missing semicolon after struct declaration")
                    else:
                        self.tkerr('Missing "}" in struct declaration')
            else:
                self.tkerr("Missing/invalid struct identifier")
        self.iTk = tk
        return False


    #parse variable def
    def varDef(self):
        tk = self.iTk
        t = Type()
        if self.typeBase(t):
            if self.consume(ID):
                tkName = self.consumedTk
                if self.arrayDecl(t):
                    if t.n == 0:
                        self.tkerr("An array must have a specif dimension")
                
                if self.consume(SEMICOLON):
                    var = findSymbolInDomain(symTable, tkName.text)
                    if var:
                        self.tkerr("Symbol redefinition: %s", tkName.text)
                    var = newSymbol(tkName.text, SK_VAR)
                    var.type = t
                    var.owner = self.owner
                    addSymbolToDomain(symTable, var)
                    if self.owner:
                        if self.owner.kind == SK_FN:
                            var.varIdx = symbolsLen(self.owner.fn.locals)
                            self.owner.fn.locals = addSymbolToList(self.owner.fn.locals, dupSymbol(var))
                        elif self.owner.kind == SK_STRUCT:
                            var.varIdx = typeSize(self.owner.type)
                            self.owner.structMembers = addSymbolToList(self.owner.structMembers, dupSymbol(var))
                    return True
                else:
                    self.tkerr("Missing semicolon after variable declaration")
            else:
                self.tkerr("Missing/invalid identifierafter base type")
        self.iTk = tk
        return False


    #parse the base type of a var/struct membr
    def typeBase(self, t):
        t.n = -1
        if self.consume(TYPE_INT):
            t.tb = TB_INT
            return True
        if self.consume(TYPE_DOUBLE):
            t.tb = TB_DOUBLE
            return True
        if self.consume(TYPE_CHAR):
            t.tb = TB_CHAR
            return True
        if self.consume(STRUCT):
            if self.consume(ID):
                tkName = self.consumedTk
                t.tb = TB_STRUCT
                t.s = findSymbol(tkName.text)
                if not t.s:
                    self.tkerr("Undefined struct: %s", tkName.text)
                return True
            else:
                self.tkerr("Missing struct indentifier") 
        return False

    #parse an array declaration
    def arrayDecl(self, t):
        if self.consume(LBRACKET):
            if self.consume(INT):
                tkSize = self.consumedTk
                t.n = tkSize.i
            else:
                t.n = 0
            if self.consume(RBRACKET):
                return True
            else:
                self.tkerr("Missing \"]\" for array declaration") 
        return False

    def fnDef(self):
        tk = self.iTk
        t = Type()
        consumedVoidTk = False
        if self.typeBase(t) or (consumedVoidTk := self.consume(VOID)):
            if consumedVoidTk:
                t.tb = TB_VOID
            if self.consume(ID):
                tkName = self.consumedTk
                if self.consume(LPAR):
                    fn = findSymbolInDomain(symTable, tkName.text)
                    if fn:
                        self.tkerr("Symbol redefinition: %s", tkName.text)
                    fn = newSymbol(tkName.text, SK_FN)
                    fn.type = t
                    addSymbolToDomain(symTable, fn)
                    self.owner = fn
                    pushDomain()
                    if self.fnParam():
                        while self.consume(COMMA):
                            if not self.fnParam():
                                self.tkerr("Missing/invalid additional funct param after comma")

                    if self.consume(RPAR):
                        if self.stmCompound(False):
                            dropDomain()
                            self.owner = None
                            return True
                        else:
                            self.tkerr("Missing funct body in function def")
                    else:
                        self.tkerr("Missing \")\" in funct signature")
            else:
                self.tkerr("Missing/invalid identif after base type")
        self.iTk = tk
        return False


    def fnParam(self):
        tk = self.iTk
        t = Type()
        if self.typeBase(t):
            if self.consume(ID):
                tkName = self.consumedTk
                if self.arrayDecl(t):
                    t.n = 0
                
                param = findSymbolInDomain(symTable, tkName.text)
                if param:
                    self.tkerr("Symbol redefinition: %s", tkName.text)
                param = newSymbol(tkName.text, SK_PARAM)
                param.type = t
                param.owner = self.owner
                param.paramIdx = symbolsLen(self.owner.fn.params)
                addSymbolToDomain(symTable, param)
                self.owner.fn.params = addSymbolToList(self.owner.fn.params, dupSymbol(param))
                return True
            else:
                self.tkerr("Missing/invalid identif after base type")
        self.iTk = tk
        return False
    
    def stm(self):
        if self.consume(IF):
            if self.consume(LPAR):
                rCond = Ret()
                if self.expr(rCond):
                    if self.consume(RPAR):
                        if self.stm():
                            if self.consume(ELSE):
                                if not self.stm():
                                    self.tkerr("Missing statement after 'else'")
                            return True
                        else:
                            self.tkerr("Missing statement after 'if' condition")
                    else:
                        self.tkerr("Missing ')' after 'if' condition")
                else:
                    self.tkerr("Missing expression in 'if' condition")
            else:
                self.tkerr("Missing '(' after 'if'")
        elif self.consume(WHILE):
            if self.consume(LPAR):
                rCond = Ret()
                if self.expr(rCond):
                    if self.consume(RPAR):
                        if self.stm():
                            return True
                        else:
                            self.tkerr("Missing statement after 'while' condition")
                    else:
                        self.tkerr("Missing ')' after 'while' condition")
                else:
                    self.tkerr("Missing expression in 'while' condition")
            else:
                self.tkerr("Missing '(' after 'while'")
        elif self.consume(RETURN):
            rRet = Ret()
            if self.expr(rRet):
                if self.consume(SEMICOLON):
                    return True
                else:
                    self.tkerr("Missing semicolon after return value")
            elif self.consume(SEMICOLON):
                return True  # return with no value
            else:
                self.tkerr("Missing semicolon after return")
        elif self.consume(LACC):
            self.iTk -= 1  # put back LACC for stmCompound
            return self.stmCompound(True)
        else:
            r = Ret()
            if self.expr(r):
                if self.consume(SEMICOLON):
                    return True
                else:
                    self.tkerr("Missing semicolon after expression statement")
            elif self.consume(SEMICOLON):
                return True  # empty statement
        return False


    def stmCompound(self, newDomain):
        if self.consume(LACC):
            if newDomain:
                pushDomain()
            while self.varDef() or self.stm():
                pass
            if self.consume(RACC):
                if newDomain:
                    dropDomain()
                return True
            else:
                self.tkerr('Missing "{"')
        return False

    def expr(self, r):
        return self.exprAssign(r)

    def exprAssign(self, r):
        tk = self.iTk
        rDst = Ret()
        if self.exprUnary(rDst):
            if self.consume(ASSIGN):
                if self.exprAssign(r):
                    if not rDst.lval:
                        self.tkerr("The assignment destination must be a left value")
                    if rDst.ct:
                        self.tkerr("The assignment destination cannot be a constant")
                    if not canBeScalar(rDst):
                        self.tkerr("The assignment source must be a scalar")
                    if not convTo(r.type, rDst.type):
                        self.tkerr("The assign source cannot be converted to the destination")
                    r.lval = False
                    r.ct = True
                    return True
                else:
                    self.tkerr('Invalid/missing expression after "=" (assignment) operator')
        self.iTk = tk
        return self.exprOr(r)

    def exprOr(self, r):
        tk = self.iTk
        if self.exprAnd(r):
            return self._exprOr(r)
        self.iTk = tk
        return False

    def _exprOr(self, r):
        tk = self.iTk
        rRight = Ret()
        if self.consume(OR):
            if self.exprAnd(rRight):
                tDst = Type()
                if not arithTypeTo(r.type, rRight.type, tDst):
                    self.tkerr('Invalid operand type for "||" (LOGICAL OR)')
                r.type = Type()
                r.type.tb = TB_INT
                r.lval = False
                r.ct = True
                self._exprOr(r)
                return True
            else:
                self.tkerr('Invalid/missing expression "||" (LOGICAL OR) operator')
        self.iTk = tk
        return True


    def exprAnd(self, r):
        tk = self.iTk
        if self.exprEq(r):
            return self._exprAnd(r)
        self.iTk = tk
        return False
    
    def _exprAnd(self, r):
        tk = self.iTk
        rRight = Ret()
        if self.consume(AND):
            if self.exprEq(rRight):
                tDst = Type()
                if not arithTypeTo(r.type, rRight.type, tDst):
                    self.tkerr('Invalid operand type for "&&" (LOGICAL AND)')
                r.type = Type()
                r.type.tb = TB_INT
                r.lval = False
                r.ct = True
                self._exprAnd(r)
                return True
            else:
                self.tkerr('Invalid/missing expression "&&" (LOGICAL AND) operator')
        self.iTk = tk
        return True

    def exprEq(self, r):
        tk = self.iTk
        if self.exprRel(r):
            return self._exprEq(r)
        self.iTk = tk
        return False
    
    def _exprEq(self, r):
        tk = self.iTk
        rRight = Ret()
        if self.consume(EQUAL) or self.consume(NOTEQ):
            op = self.tokens[self.iTk - 1].code
            if self.exprRel(rRight):
                tDst = Type()
                if not arithTypeTo(r.type, rRight.type, tDst):
                    self.tkerr('Invalid operand type for equality operator')
                r.type = Type()
                r.type.tb = TB_INT
                r.lval = False
                r.ct = True
                self._exprEq(r)
                return True
            else:
                self.tkerr('Invalid/missing expression after equality operator')
        self.iTk = tk
        return True
    
    def exprRel(self, r):
        tk = self.iTk
        if self.exprAdd(r):
            return self._exprRel(r)
        self.iTk = tk
        return False
    
    def _exprRel(self, r):
        tk = self.iTk
        rRight = Ret()
        if (self.consume(LESS) or self.consume(LESSEQ) or self.consume(GREATER) or self.consume(GREATEREQ)):
            op = self.tokens[self.iTk - 1].code
            if self.exprAdd(rRight):
                tDst = Type()
                if not arithTypeTo(r.type, rRight.type, tDst):
                    self.tkerr('Invalid operand type for relational operator')
                r.type = Type()
                r.type.tb = TB_INT
                r.lval = False
                r.ct = True
                self._exprRel(r)
                return True
            else:
                self.tkerr('Invalid/missing expression after relational operator')
        self.iTk = tk
        return True



    def exprAdd(self, r):
        tk = self.iTk
        if self.exprMul(r):
            self._exprAdd(r)
            return True
        self.iTk = tk
        return False
    
    def _exprAdd(self, r):
        tk = self.iTk
        rRight = Ret()
        if self.consume(ADD):
            if self.exprMul(rRight):
                tDst = Type()
                if not arithTypeTo(r.type, rRight.type, tDst):
                    self.tkerr('Invalid operand for "+" (ADDITION)')
                r.type = tDst
                r.lval = False
                r.ct = True
                self._exprAdd(r)
                return True
            else:
                self.tkerr('Invalid/missing expression after "+" (ADDITION) operator')
        
        if self.consume(SUB):
            if self.exprMul(rRight):
                tDst = Type()
                if not arithTypeTo(r.type, rRight.type, tDst):
                    self.tkerr('Invalid operand for "-" (SUBTRACTION)')
                r.type = tDst
                r.lval = False
                r.ct = True
                self._exprAdd(r)
                return True
            else:
                self.tkerr('Invalid/missing expression after "-" (SUBTRACTION) operator')

        self.iTk = tk
        return True
    
    def exprMul(self, r):
        tk = self.iTk
        if self.exprCast(r):
            self._exprMul(r)
            return True
        self.iTk = tk
        return False
    
    def _exprMul(self, r):
        tk = self.iTk
        rRight = Ret()
        if self.consume(MUL):
            if self.exprCast(rRight):
                tDst = Type()
                if not arithTypeTo(r.type, rRight.type, tDst):
                    self.tkerr('Invalid operand for "*" (MULTIPLICATION)')
                r.type = tDst
                r.lval = False
                r.ct = True
                self._exprAdd(r)
                return True
            else:
                self.tkerr('Invalid/missing expression after "*" (MULTIPLICATION) operator')
        
        if self.consume(DIV):
            if self.exprCast(rRight):
                tDst = Type()
                if not arithTypeTo(r.type, rRight.type, tDst):
                    self.tkerr('Invalid operand for "/" (DIVISION)')
                r.type = tDst
                r.lval = False
                r.ct = True
                self._exprAdd(r)
                return True
            else:
                self.tkerr('Invalid/missing expression after "/" (DIVISION) operator')

        self.iTk = tk
        return True

    def exprCast(self, r):
        tk = self.iTk
        t = Type()
        if self.consume(LPAR):
            if self.typeBase(t):
                if self.arrayDecl(t):
                    pass
                if self.consume(RPAR):
                    if self.exprCast(r):
                        if not canBeScalar(r):
                            self.tkerr("The cast operand must be a scalar")
                        if not convTo(r.type, t):
                            self.tkerr("Cannost cast to destination type")
                        r.type = t
                        r.lval = False
                        r.ct = True
                        return True
                    else:
                        self.tkerr("Invalid/missing expression cast type")
                else:
                    self.tkerr('Missing ")" after cast type')
        self.iTk = tk
        return self.exprUnary(r)
    
    def exprUnary(self, r):
        if self.consume(SUB):
            if self.exprUnary(r):
                if not canBeScalar(r):
                    self.tkerr("Unary '-' operand must be scalar")
                # r.type stays the same
                r.lval = False
                r.ct = True
                return True
            else:
                self.tkerr("Missing epression after unary '-'")
        
        if self.consume(NOT):
            if self.exprUnary(r):
                if not canBeScalar(r):
                    self.tkerr("Unary '!' operand must be scalar")
                r.type = Type()
                r.type.tb = TB_INT
                r.lval = False
                r.ct = True
                return True
            else:
                self.tkerr("Missing expression after unary '!'")
        return self.exprPostfix(r)
    
    def exprPostfix(self, r):
        if self.exprPrimary(r):
            return self._exprPostfix(r)
        return False
    
    def _exprPostfix(self, r):
        tk = self.iTk
        if self.consume(LBRACKET):
            rArr = Ret()
            if self.expr(rArr):
                if not self.consume(RBRACKET):
                    self.tkerr('Missing "]" in array access')
                #array access type checks here
                #ex: r.type == r.type.something
                r.lval = False
                r.ct = True
                return self._exprPostfix(r)
            else:
                self.tkerr("Missing expression inside array bracket")
        self.iTk = tk
        return True
    
    def exprPrimary(self, r):
        if self.consume(ID):
            tkName = self.consumedTk
            s = findSymbol(tkName.text)
            if not s:
                self.tkerr("Undefined symbol: %s", tkName.text)
            r.type = s.type
            r.lval = False
            r.ct = True
            return True
        if self.consume(INT):
            tkInt = self.consumedTk
            r.type = Type()
            r.type.tb = TB_INT
            r.lval = False
            r.ct = True
            return True
        if self.consume(DOUBLE):
            tkDouble = self.consumedTk
            r.type = Type()
            r.type.tb = TB_DOUBLE
            r.lval = False
            r.ct = True
            return True
        if self.consume(CHAR):
            tkChar = self.consumedTk
            r.type = Type()
            r.type.tb = TB_CHAR
            r.lval = False
            r.ct = True
            return True
        if self.consume(LPAR):
            if self.expr(r):
                if self.consume(RPAR):
                    return True
                else:
                    self.tkerr('Missing ")" after parenthesized expression')
            else:
                self.tkerr("Missing expression after '('")
        return False