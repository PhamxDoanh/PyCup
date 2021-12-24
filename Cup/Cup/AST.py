

from collections import namedtuple

Number = namedtuple('Number', ['value'])
String = namedtuple('String', ['value'])
Logic = namedtuple('Logic', ['value']) # not yet
Identifier = namedtuple('Identifier', ['value'])
Assignment = namedtuple('Assignment', ['left', 'right'])
BinaryOperator = namedtuple('BinaryOperator', ['operator', 'left', 'right'])
UnaryOperatorPrefix = namedtuple('UnaryOperatorPrefix', ['operator', 'right'])
UnaryOperatorPostfix = namedtuple('UnaryOperatorPostfix', ['operator', 'left']) # not yet
Class = namedtuple('Class', ['name', 'body'])
Function = namedtuple('Function', ['name', 'params', 'body'])
CallFunction = namedtuple('CallFunction', ['left', 'arguments'])
CallClass = namedtuple('CallClass', ['left', 'arguments'])
Condition = namedtuple('Condition', ['test', 'if_body', 'elifs', 'else_body'])
ConditionElif = namedtuple('ConditionElif', ['test', 'body'])
Use = namedtuple('Use', ['obj', 'library'])
Do = namedtuple('Do', ['do_body', 'unlesses', 'last_body'])
Unless = namedtuple('Unless', ['unlesses', 'body'])
When = namedtuple('When', ['test', 'patterns', 'else_body'])
WhenPattern = namedtuple('WhenPattern', ['pattern', 'body'])
WhileLoop = namedtuple('WhileLoop', ['test', 'body', 'else_body'])
ForLoop = namedtuple('ForLoop', ['var_name', 'collection', 'body'])
Quit = namedtuple('Quit', [])
Continue = namedtuple('Continue', [])
Skip = namedtuple('Skip', [])
Return = namedtuple('Return', ['value'])
Throw = namedtuple('Throw', ['value'])
List = namedtuple('List', ['items'])
Packs = namedtuple('Packs', ['items']) # not yet
Set = namedtuple('Set', ['items']) # not yet
Shell = namedtuple('Shell', ['items'])
Dictionary = namedtuple('Dictionary', ['items'])
SubscriptOperator = namedtuple('SubscriptOperator', ['left', 'key'])
BuiltinFunction = namedtuple('BuiltinFunction', ['params', 'body'])
Program = namedtuple('Program', ['body'])
