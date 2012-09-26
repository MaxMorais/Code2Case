#!/usr/bin/python

import dis

from macroit import FuncInterpreter
from gluon.dal import Expression

class MacroCmd(str):
    def __repr__(self):
        return str(self)

class Case(Expression,FuncInterpreter):
    """
    Class transforming python function to SQL case statement

    * Function requirement
      - every if <sql_condition> statement must end with return
      Following is correct code:
      foo = db.foo()
      def casefunc():
          if today() < tommorrow():  # - this is not <sql_condition>
              do_something
          if foo.x > foo.y:  # this is SQL condition
              if foo.x > 5:
                  return foo.x
              return foo.y
          return None
      - And this is incorrect
      def casefunc():
          if foo.x > foo.y:
              if foo.x > 5:
                  return foo.x
              #### -> The (foo.x > foo.y) condition exits here without return
          if foo.z > 5:
              return 1
          return None
    """
    def __init__(self,func):
        FuncInterpreter.__init__(self,func)

        self.condstack = []
        self.case = []
        self.lastiflevel = 0
        self.lastretlevel = 0
        self.next_instr = 0

        self.run()

    def run(self):
        while not self.dispatch():
            if self.condstack and self.next_instr >= self.condstack[-1]:
                # We got out of condition without returning value
                # - that means, we are not in proper if/else
                #   code
                raise RuntimeError("Unsupported code.")

    def __repr__(self):
        return repr(self.case)

    def __str__(self):
        return self.sql()

    def sql(self,aliases):
        text = ''
        params = []
        for val in self.case:
            if isinstance(val,MacroCmd):
                text += val + ' '
            elif isinstance(val,Expr):
                t,p = val.sql()
                text += t + ' '
                params += p
            else:
                text += '%s '
                params.append(val)
        return text % params

    def RETURN_VALUE(self):
        returnvalue = self.stack.pop()
        returnvalue = self._fix_col(returnvalue)
        if self.condstack:
            if self.lastretlevel > len(self.condstack):
                self.case.append(MacroCmd('else'))
            self.case.append(returnvalue)
            if self.lastretlevel > len(self.condstack):
                self.case.append(MacroCmd('end'))

            self.lastretlevel = len(self.condstack)
            lastcond = self.condstack.pop()
            self.stack.append(None) #'If' jumps expect 1 item on stack
            self.next_instr = lastcond
            return
        else:
            if self.lastretlevel:
                self.case.append(MacroCmd('else'))
                self.case.append(returnvalue)
                self.case.append(MacroCmd('end'))
            else:
                self.case.append(returnvalue)

        return 1 #Finish processing

    def jump_it(self,stepby,cond):
        # Append beginning of if & end of the if
        #self.condstack.append(self.next_instr + stepby)

        self.condstack.append(stepby)

        if self.lastiflevel < len(self.condstack):
            self.case.append(MacroCmd('case'))
        self.lastiflevel = len(self.condstack)

        self.case.append(MacroCmd('when'))
        self.case.append(cond)
        self.case.append(MacroCmd('then'))
        return

    def JUMP_IF_FALSE(self, stepby):
        cond = self.stack[-1]

        if (isinstance(cond,Expr)):
            return self.jump_it(stepby, cond)
        if not cond:
            self.next_instr += stepby

    def JUMP_IF_TRUE(self, stepby):
        cond = self.stack[-1]
        if (isinstance(cond,Expr)):
            return self.jump_it(stepby, ~cond)
        if cond:
            self.next_instr += stepby

    def POP_JUMP_IF_TRUE(self, stepby):
        cond = self.stack[-1]
        if (isinstance(cond, sqlabstr.Condition)):
            return self.jump_it(stepby, cond)
        if cond:
            self.next_instr = stepby
            self.POP_TOP()

    def POP_JUMP_IF_FALSE(self, stepby):
        cond = self.stack[-1]
        if (isinstance(Cond, sqlabstr.Condition)):
            return self.jump_it(stepby, ~cond)
        if not cond:
            self.next_instr = stepby
            self.POP_TOP()