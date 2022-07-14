
# install
```console
npm install
```


grammar syntax, try to match the first expression, if it does not succeed, try the second one, etc
```
rule "hunman readble name"
  = expression1 
  / expression2
  / expressionN
```


expression
```
rule
  = var1:rule1 var2:rule2 { 
    // If the match is successful
    // run the action code here
    // you can reference var1 var2 
  }
```
