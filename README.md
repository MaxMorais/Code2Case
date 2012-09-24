Code2Case
=========

Web2py Plugin for easy conversion of slow virtual columns for agile columns case
This plugin uses the standard module dis, allowing disassembly of python code and building columns in sql case


[pt-Br] Web2Py Plugin para fácil conversão de colunas virtuais lentas para colunas sql case ágeis
Este plugin usa o módulo padrão dis, que permite a desmontagem (disassembly) do código python e a construção de colunas case em sql

Ex:

```python
def main():
  from case import Case
  def myfunc():
    if db.mytable.myfield == 0:
      return 'A'
    elif db.mytable.myfield == 1:
      return 'B'
    else:
      return 'C'
  
  def myfunc1():
    if db.mytable.myfield == 0:
      if db.mytable.myfield1 == 'a':
        return 1
      return 0
    return False

  db().select(db.mytable.ALL, Case(myfunc), Case(myfunc))
```

The function code is evaluated and transformed in case below.

[pt-Br] O código da função será avaliado e transformado no case abaixo

```sql
CASE WHEN (mytable.myfield = 0) THEN 'A' ELSE CASE WHEN (mytable.myfield == 1) THEN 'B' ELSE 'C' END END,
CASE WHEN (mytable.myfield = 0) THEN CASE WHEN (mytable.myfield1 == 1) THEN 1 ELSE 0 END ELSE 'False' END
```
