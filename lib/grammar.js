class Directive {
  constructor(directive, parameters) {
    this.directive = directive;
    this.parameters = parameters;
  }
}

// A directive consists of the name and parameters separated
// by spaces and ends with a semicolon (;)
// return Directive object
const directive = `
directive
  = key:Word params:(wss Parameter)+ ws* ";" {
    // params: [['ws', 'para1'], ['ws', 'para12'], ...]
    params = params.map(arr => arr.join('').trim());
    return new Directive(key, params)
  }
`

// A block directive has the same structure as a simple directive,
// but instead of the semicolon it ends with a set of additional
// instructions surrounded by braces ({ and }).
const block_directive = `
block_directive  
  = "todo"
`

const initializer = `
{
${Directive.toString()}
}
`


const start = `
start "start rule"
  = directive
  / block_directive
`

module.exports = {
  start,
  initializer,
  // rules
  directive,
  block_directive,
  // classes
  Directive,
}
