const Token = `
Word
 = l:[a-zA-Z]+ { return l.join(''); }

NumericWord
  = l:[a-zA-Z0-9]+ { return l.join(''); }

Parameter "parameter"
  = l:[a-zA-Z0-9/:$]+ { return l.join(''); }


wss "whitespaces"
  = l:ws+ { return l.join(''); }
      
ws "whitespace"
  = [ \\t]
`


module.exports = {
  Token,
}
