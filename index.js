const peg = require('pegjs');
const grammar = require('lib/grammar');
const lexer = require('lib/lexer');


const grammars = grammar.start
  + grammar.initializer
  + lexer.Token;

const parser = peg.generate(grammars)

module.exports = {
  grammars,
  parser
}


