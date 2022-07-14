const peg = require('pegjs');
const assert = require('assert');
const grammar = require('../lib/grammar');
const lexer = require('../lib/lexer');


function genGrammar(rule) {
  return grammar.initializer + rule + lexer.Token;
}

describe('Test parser', () => {
  it('Test rule directive', () => {
    const parser = peg.generate(genGrammar(grammar.directive));
    const result = parser.parse(`name p1 p2;`);
    assert.deepEqual(result, new grammar.Directive("name", ["p1", "p2"]))
  });

  it('Test start rule', () => {
    const parser = peg.generate(genGrammar(grammar.start + grammar.directive + grammar.block_directive));
    const result = parser.parse(`name p1 p2;`);
    assert.deepEqual(result, new grammar.Directive("name", ["p1", "p2"]))
  });

});
