Code2Case
=========

Web2py Plugin for easy conversion of slow virtual columns for agile columns case
This plugin uses the standard module dis, allowing disassembly of python code and building columns in sql case


[pt-Br] Web2Py Plugin para fácil conversão de colunas virtuais lentas para colunas sql case ágeis
Este plugin usa o módulo padrão dis, que permite a desmontagem (disassembly) do código python e a construção de colunas case em sql

Eg. (Ex):

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

print(db()._select(db.mytable.ALL, Case(myfunc))
```

```sql
SELECT CASE WHEN (mytable.myfield = 0) THEN 'A' ELSE CASE WHEN (mytable.myfield == 1) THEN 'B' ELSE 'C' END END FROM mytable
````

```python
  def myfunc1():
    if db.mytable.myfield == 0:
      if db.mytable.myfield1 == 'a':
        return 1
      return 0
    return False

  print db()._select(db.mytable.ALL, Case(myfunc1))
```

```sql
SELECT CASE WHEN (mytable.myfield = 0) THEN CASE WHEN (mytable.myfield1 == 1) THEN 1 ELSE 0 END ELSE 'F' END FROM mytable
```

```python
def myfunc3():
  if db.mytable.myfield >= 5 or db.mytable.field < 2 :
    if db.mytable.myfiedl1 == 0 and db.mytable.myfield2 == 1:
      return 2
    return 3
  return 1

```

```sql
SELECT CASE WHEN ((mytable.myfield >= 5) OR (mytable.myfield < 2)) THEN CASE WHEN ((mytable.myfield1 == 0) AND (mytable.myfield2 == 1) THEN 2 ELSE 3 END ELSE 1 END FROM mytable