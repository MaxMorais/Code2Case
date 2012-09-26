#!/usr/bin/python
"""
Interpreter of Python function

* Does not support exceptions
"""
import dis
import new
def get_cell_value(cell):
    def make_closure_that_returns_value(use_this_value):
        def closure_that_returns_value():
            return use_this_value
        return closure_that_returns_value
    dummy_function = make_closure_that_returns_value(0)
    dummy_function_code = dummy_function.func_code
    our_function = new.function(dummy_function_code, {}, None, None, (cell,))
    value_from_cell = our_function()
    return value_from_cell

def unaryoperation(func):
    def ufunction(self):
        w_1 = self.stack.pop()
        result = func(w_1)
        self.stack.append(result)
    return ufunction

def binaryoperation(func):
    def bfunction(self):
        w_2 = self.stack.pop()
        w_1 = self.stack.pop()
        result = func(w_1,w_2)
        self.stack.append(result)
    return bfunction

def binline(func,attr):
    def bfunction(self):
        w_2 = self.stack.pop()
        w_1 = self.stack.pop()
        if hasattr(w_1,attr):
            self.stack.append(getattr(w_1,attr)(w_2))
        else:
            w_1 = func(w_1,w_2)
            self.stack.append(w_1)
    return bfunction

class FuncInterpreter(object):
    def __init__(self,func):
        assert isinstance(func,new.function)
        self.func = func
        self.pycode = func.func_code
        self.stack = []
        self.locals = {}
        self.globals = func.func_globals
        self.blockstack = []

        self.clovars = []
        if func.func_closure:
            for cell in func.func_closure:
                self.clovars.append(get_cell_value(cell))

    def run(self):
        self.next_instr = 0
        while not self.dispatch():
            pass

    def dispatch(self):
        opcode = self.nextop()

        try:
            fn = getattr(self,dis.opname[opcode])
        except AttributeError:
            raise NotImplementedError('Unsupported opcode: %s' % dis.opname[opcode])

        if opcode >= dis.HAVE_ARGUMENT:
            oparg = self.nextarg()
            return fn(oparg)
        else:
            return fn()

    def nextop(self):
        c = self.pycode.co_code[self.next_instr]
        self.next_instr += 1
        return ord(c)

    def nextarg(self):
        lo = self.nextop()
        hi = self.nextop()
        return (hi<<8) + lo

    ### accessor functions ###

    def getlocalvarname(self, index):
        return self.pycode.co_varnames[index]

    def getconstant(self, index):
        return self.pycode.co_consts[index]

    def getname(self, index):
        return self.pycode.co_names[index]


    def NOP(f):
        pass

    def LOAD_DEREF(self,varindex):
        self.stack.append(self.clovars[varindex])

    def LOAD_FAST(self, varindex):
        varname = self.getlocalvarname(varindex)
        self.stack.append(self.locals[varname])

    def LOAD_CONST(self, constindex):
        w_const = self.getconstant(constindex)
        self.stack.append(w_const)

    def STORE_FAST(self, varindex):
        varname = self.getlocalvarname(varindex)
        w_newvalue = self.stack.pop()
        self.locals[varname] = w_newvalue

    def POP_TOP(self):
        if self.condstack:
            self.condstack.pop()
        self.stack.pop()

    def ROT_TWO(self):
        w_1 = self.stack.pop()
        w_2 = self.stack.pop()
        self.stack.append(w_1)
        self.stack.append(w_2)

    def ROT_THREE(self):
        w_1 = self.stack.pop()
        w_2 = self.stack.pop()
        w_3 = self.stack.pop()
        self.stack.append(w_1)
        self.stack.append(w_3)
        self.stack.append(w_2)

    def ROT_FOUR(self):
        w_1 = self.stack.pop()
        w_2 = self.stack.pop()
        w_3 = self.stack.pop()
        w_4 = self.stack.pop()
        self.stack.append(w_1)
        self.stack.append(w_4)
        self.stack.append(w_3)
        self.stack.append(w_2)

    def DUP_TOP(self):
        w_1 = self.stack[-1]
        self.stack.append(w_1)

    def DUP_TOPX(f, itemcount):
        assert 1 <= itemcount <= 5, "limitation of the current interpreter"
        self.stack.extend(self.stack[-itemcount:])

    UNARY_POSITIVE = unaryoperation(lambda x:+x)
    UNARY_NEGATIVE = unaryoperation(lambda x:-x)
    UNARY_NOT      = unaryoperation(lambda x:not x)
    UNARY_CONVERT  = unaryoperation(lambda x:repr(x))
    UNARY_INVERT   = unaryoperation(lambda x:~x)

    BINARY_POWER = binaryoperation(lambda x,y:x**y)
    BINARY_MULTIPLY = binaryoperation(lambda x,y:x*y)
    BINARY_TRUE_DIVIDE  = binaryoperation(lambda x,y:x/y)
    BINARY_FLOOR_DIVIDE = binaryoperation(lambda x,y:x//y)
    BINARY_DIVIDE       = binaryoperation(lambda x,y:x/y)
    BINARY_MODULO       = binaryoperation(lambda x,y:x%y)
    BINARY_ADD      = binaryoperation(lambda x,y:x+y)
    BINARY_SUBTRACT = binaryoperation(lambda x,y:x-y)
    BINARY_SUBSCR   = binaryoperation(lambda x,y:x[y])
    BINARY_LSHIFT   = binaryoperation(lambda x,y:x<<y)
    BINARY_RSHIFT   = binaryoperation(lambda x,y:x>>y)
    BINARY_AND = binaryoperation(lambda x,y:x&y)
    BINARY_XOR = binaryoperation(lambda x,y:x^y)
    BINARY_OR  = binaryoperation(lambda x,y:x|y)


    INPLACE_POWER = binline(lambda x,y:x**y,'__pow__')
    INPLACE_MULTIPLY = binline(lambda x,y:x*y,'__mul__')
    INPLACE_TRUE_DIVIDE  = binline(lambda x,y:x/y,'__truediv__')
    INPLACE_FLOOR_DIVIDE = binline(lambda x,y:x//y,'__floordiv__')
    INPLACE_DIVIDE       = binline(lambda x,y:x/y,'__div__')
    INPLACE_MODULO       = binline(lambda x,y:x%y,'__mod__')
    INPLACE_ADD      = binline(lambda x,y:x+y,'__add__')
    INPLACE_SUBTRACT = binline(lambda x,y:x-y,'__sub__')
    INPLACE_LSHIFT   = binline(lambda x,y:x<<y,'__lshift__')
    INPLACE_RSHIFT   = binline(lambda x,y:x>>y,'__rshift__')
    INPLACE_AND = binline(lambda x,y:x&y,'__and__')
    INPLACE_XOR = binline(lambda x,y:x^y,'__xor__')
    INPLACE_OR  = binline(lambda x,y:x|y,'__or__')

    def slice(f, w_start, w_end):
        w_obj = self.stack.pop()
        self.stack.append(w_obj[w_start:w_end])

    def SLICE_0(self):
        w_obj = self.stack.pop()
        self.stack.append(w_obj[:])

    def SLICE_1(self):
        w_start = self.stack.pop()
        self.stack.append(w_obj[w_start:])

    def SLICE_2(self):
        w_end = self.stack.pop()
        self.stack.append(w_obj[:w_end])

    def SLICE_3(self):
        w_end = self.stack.pop()
        w_start = self.stack.pop()
        self.stack.append(w_obj[w_start:w_end])

    def storeslice(self, w_start, w_end):
        w_obj = self.stack.pop()
        w_newvalue = self.stack.pop()
        w_obj[w_start:w_end] = w_newvalue

    def STORE_SLICE_0(self):
        self.storeslice(None,None)

    def STORE_SLICE_1(self):
        w_start = self.stack.pop()
        self.storeslice(w_start,None)

    def STORE_SLICE_2(self):
        w_end = self.stack.pop()
        self.storeslice(None,w_end)

    def STORE_SLICE_3(self):
        w_end = self.stack.pop()
        w_start = self.stack.pop()
        self.storeslice(w_start, w_end)

    def deleteslice(f, w_start, w_end):
        w_obj = self.stack.pop()
        del w_obj[w_start:w_end]

    def DELETE_SLICE_0(self):
        self.deleteslice(f.space.w_None, f.space.w_None)

    def DELETE_SLICE_1(self):
        w_start = self.stack.pop()
        self.deleteslice(w_start, None)

    def DELETE_SLICE_2(self):
        w_end = self.stack.pop()
        self.deleteslice(None, w_end)

    def DELETE_SLICE_3(self):
        w_end = self.stack.pop()
        w_start = self.stack.pop()
        self.deleteslice(w_start, w_end)

    def STORE_SUBSCR(self):
        "obj[subscr] = newvalue"
        w_subscr = self.stack.pop()
        w_obj = self.stack.pop()
        w_newvalue = self.stack.pop()
        f.space.setitem(w_obj, w_subscr, w_newvalue)

    def DELETE_SUBSCR(self):
        "del obj[subscr]"
        w_subscr = self.stack.pop()
        w_obj = self.stack.pop()
        del w_obj[w_subscr]

    def PRINT_EXPR(self):
        w_expr = self.stack.pop()
        print w_expr

    def PRINT_ITEM_TO(self):
        w_stream = self.stack.pop()
        w_item = self.stack.pop()
        if w_stream == None:
            print w_item,
        print w_item >> w_stream

    def PRINT_ITEM(self):
        w_item = self.stack.pop()
        print w_item,

    def PRINT_NEWLINE_TO(self):
        w_stream = self.stack.pop()
        if w_stream == None:
            print
        print >> w_stream

    def PRINT_NEWLINE(self):
        print

    def RETURN_VALUE(self):
        w_returnvalue = self.stack.pop()
        return 1,w_returnvalue

    def STORE_NAME(self, varindex):
        w_varname = self.getname(varindex)
        w_newvalue = self.stack.pop()
        self.locals[w_varname] = w_newvalue

    def DELETE_NAME(self, varindex):
        w_varname = self.getname(varindex)
        del self.locals[w_varname]

    def UNPACK_SEQUENCE(self, itemcount):
        w_iterable = self.stack.pop()
        items = list(w_iterable)
        items.reverse()
        for item in items:
            self.stack.append(item)

    def STORE_ATTR(self, nameindex):
        "obj.attributename = newvalue"
        w_attributename = self.getname(nameindex)
        w_obj = self.stack.pop()
        w_newvalue = self.stack.pop()
        setattr(w_obj,w_attributename,w_newvalue)

    def DELETE_ATTR(self, nameindex):
        "del obj.attributename"
        w_attributename = self.getname(nameindex)
        w_obj = self.stack.pop()
        delattr(w_obj, w_attributename)

    def STORE_GLOBAL(self, nameindex):
        w_varname = self.getname(nameindex)
        w_newvalue = self.stack.pop()
        f.space.setitem(f.w_globals, w_varname, w_newvalue)

    def DELETE_GLOBAL(self, nameindex):
        w_varname = self.getname(nameindex)
        f.space.delitem(f.w_globals, w_varname)

    def LOAD_NAME(self, nameindex):
        w_varname = self.getname(nameindex)
        try:
            w_value = self.locals[w_varname]
        except KeyError:
            pass
        f.LOAD_GLOBAL(nameindex)    # fall-back

    def LOAD_GLOBAL(self, nameindex):
        w_varname = self.getname(nameindex)
        if self.globals.has_key(w_varname):
            self.stack.append(self.globals[w_varname])
        else:
            self.stack.append(__builtins__[w_varname])

    def DELETE_FAST(self, varindex):
        varname = f.getlocalvarname(varindex)
        del self.locals[varname]

    def BUILD_TUPLE(self, itemcount):
        items = [self.stack.pop() for i in range(itemcount)]
        items.reverse()
        w_tuple = tuple(items)
        self.stack.append(w_tuple)

    def BUILD_LIST(self, itemcount):
        items = [self.stack.pop() for i in range(itemcount)]
        items.reverse()
        self.stack.append(items)

    def BUILD_MAP(self, zero):
        if zero != 0:
            raise pyframe.BytecodeCorruption
        self.stack.append(dict())

    def LOAD_ATTR(self, nameindex):
        "obj.attributename"
        w_attributename = self.getname(nameindex)
        w_obj = self.stack.pop()
        w_value = getattr(w_obj, w_attributename)
        self.stack.append(w_value)

    def cmp_lt(w_1, w_2):  return w_1 < w_2
    def cmp_le(w_1, w_2):  return w_1 <= w_2
    def cmp_eq(w_1, w_2):  return w_1 == w_2
    def cmp_ne(w_1, w_2):  return w_1 != w_2
    def cmp_gt(w_1, w_2):  return w_1 > w_2
    def cmp_ge(w_1, w_2):  return w_1 >= w_2

    def cmp_in(w_1, w_2):
        return w_1 in w_2
    def cmp_not_in(w_1, w_2):
        return w_1 not in w_2
    def cmp_is(w_1, w_2):
        return w_1 is w_2
    def cmp_is_not(w_1, w_2):
        return w_1 is not w_2

    compare_dispatch_table = {
        0: cmp_lt,   # "<"
        1: cmp_le,   # "<="
        2: cmp_eq,   # "=="
        3: cmp_ne,   # "!="
        4: cmp_gt,   # ">"
        5: cmp_ge,   # ">="
        6: cmp_in,
        7: cmp_not_in,
        8: cmp_is,
        9: cmp_is_not,
        }
    def COMPARE_OP(self, testnum):
        w_2 = self.stack.pop()
        w_1 = self.stack.pop()
        try:
            testfn = self.compare_dispatch_table[testnum]
        except KeyError:
            raise pyframe.BytecodeCorruption, "bad COMPARE_OP oparg"
        w_result = testfn(w_1, w_2)
        self.stack.append(w_result)

    def JUMP_FORWARD(self, stepby):
        self.next_instr += stepby

    def JUMP_IF_FALSE(self, stepby):
        w_cond = self.stack[-1]
        if not w_cond:
            self.next_instr += stepby

    def JUMP_IF_TRUE(self, stepby):
        w_cond = self.stack[-1]
        if w_cond:
            self.next_instr += stepby

    def JUMP_ABSOLUTE(self, jumpto):
        self.next_instr = jumpto

    def call_function(self, oparg, w_star=None, w_starstar=None):
        n_arguments = oparg & 0xff
        n_keywords = (oparg>>8) & 0xff
        keywords = {}
        if n_keywords:
            for i in range(n_keywords):
                w_value = self.stack.pop()
                w_key   = self.stack.pop()
                key = str(w_key)
                keywords[key] = w_value
        arguments = [self.stack.pop() for i in range(n_arguments)]
        arguments.reverse()

        w_function  = self.stack.pop()
        w_result = w_function(*arguments,**keywords)
        self.stack.append(w_result)

    def CALL_FUNCTION(self, oparg):
        self.call_function(oparg)

    def CALL_FUNCTION_VAR(self, oparg):
        w_varargs = self.stack.pop()
        self.call_function(oparg, w_varargs)

    def CALL_FUNCTION_KW(self, oparg):
        w_varkw = self.stack.pop()
        self.call_function(oparg, None, w_varkw)

    def CALL_FUNCTION_VAR_KW(self, oparg):
        w_varkw = self.stack.pop()
        w_varargs = self.stack.pop()
        self.call_function(oparg, w_varargs, w_varkw)

    def BUILD_SLICE(self, numargs):
        if numargs == 3:
            w_step = self.stack.pop()
        elif numargs == 2:
            w_step = None
        else:
            raise pyframe.BytecodeCorruption
        w_end   = self.stack.pop()
        w_start = self.stack.pop()

        w_slice = slice(w_start, w_end, w_step)
        self.stack.append(w_slice)

    def LIST_APPEND(self):
        w = self.stack.pop()
        v = self.stack.pop()
        v.append(w)

    def SET_LINENO(self, lineno):
        pass

    def POP_BLOCK(self):
        self.blockstack.pop()

    def SETUP_LOOP(self, offsettoend):
        self.blockstack.append(self.next_instr + offsettoend)

    def FOR_ITER(self, jumpby):
        w_iterator = self.stack[-1]
        try:
            w_nextitem = w_iterator.next()
        except StopIteration:
            self.next_instr += jumpby
        else:
            self.stack.append(w_nextitem)

    def GET_ITER(self):
        w_iterable = self.stack.pop()
        w_iterator = iter(w_iterable)
        self.stack.append(w_iterator)

    def BREAK_LOOP(f):
        self.next_instr = self.blockstack.pop()

