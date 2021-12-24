

from Cup import AST
from Cup.Errors import CupSyntaxError


class ParserError(CupSyntaxError):

	def __init__(self, message, token):
		super(ParserError, self).__init__(message, token.line, token.column)


def enter_scope(parser, name):
	class State(object):
		def __enter__(self): parser.scope.append(name)
		def __exit__(self, exc_type, exc_val, exc_tb): parser.scope.pop()
	return State()


class Subparser(object):

	PRECEDENCE = {
		'call': 14, 'subscript': 14,
		'^': 13, 
		'unary': 12,
		'*': 11, '/': 11, '\\': 11, '%': 11, 
		'+': 10, '-': 10, 
		'<<': 9, '>>': 9, 
		'&&': 8,
		'^^': 7,
		'||': 6,
		'==': 5, '!=': 5, '><': 5, '<=>': 5,
		'>': 4, '>=': 4, '<': 4, '<=': 4, 
		'&': 3, 'and':3,
		'|': 2, 'or': 3,

	}

	def get_subparser(self, token, subparsers, default=None):
		cls = subparsers.get(token.name, default)
		if cls is not None: return cls()


class PrefixSubparser(Subparser):
	def parse(self, parser, tokens): raise NotImplementedError()


class InfixSubparser(Subparser):
	def parse(self, parser, tokens, left): raise NotImplementedError()
	def get_precedence(self, token): raise NotImplementedError()


# number expression: NUMBER
class NumberExpression(PrefixSubparser):
	
	def parse(self, parser, tokens):
		token = tokens.consume_expected('NUMBER')
		return AST.Number(token.value)


# string expression: STRING
class StringExpression(PrefixSubparser):

	def parse(self, parser, tokens):
		token = tokens.consume_expected('STRING')
		return AST.String(token.value)


# name expression: NAME
class NameExpression(PrefixSubparser):

	def parse(self, parser, tokens):
		token = tokens.consume_expected('NAME')
		return AST.Identifier(token.value)

# logic expression: LOGIC
class LogicExpression(PrefixSubparser):

	def parse(self, parser, tokens):
		token = tokens.consume_expected('LOGIC')
		return AST.Logic(token.value)

# prefix expression: OPERATOR expr

class UnaryOperatorExpression(PrefixSubparser):

	SUPPORTED_OPERATORS = ['!', 'not', '+', '-', '?', '~']
	def parse(self, parser, tokens):
		token = tokens.consume_expected('OPERATOR')
		if token.value not in self.SUPPORTED_OPERATORS:
			raise ParserError(f'Unary operator {token.value} is not supported', token)
		right = Expression().parse(parser, tokens, self.get_precedence(token))
		# left = Expression().parse(parser, tokens, self.get_precedence(token))
		if right is None: raise ParserError(f'Expected expression {token.value}', tokens.consume())
		# elif left: return AST.UnaryOperatorPostfix(token.value, left) 
		return AST.UnaryOperatorPrefix(token.value, right)
		

	def get_precedence(self, token): return self.PRECEDENCE['unary']


# group expression: LPAREN expr RPAREN
class GroupExpression(PrefixSubparser):

	def parse(self, parser, tokens):
		tokens.consume_expected('LPAREN')
		right = Expression().parse(parser, tokens)
		tokens.consume_expected('RPAREN')
		return right


# list expression: LBRACK list_of expression? RBRACK
class ListExpression(PrefixSubparser):

	def parse(self, parser, tokens):
		tokens.consume_expected('LBRACK')
		items = ListOfExpressions().parse(parser, tokens)
		tokens.consume_expected('RBRACK')
		return AST.List(items)


# list expression: LBRACK list_of expression? RBRACK
class SetExpression(PrefixSubparser):

	def parse(self, parser, tokens):
		tokens.consume_expected('LCBRACK')
		items = ListOfExpressions().parse(parser, tokens)
		tokens.consume_expected('RCBRACK')
		return AST.Set(items)


# dict expression: LCBRACK (expr COLON expr COLON)* RCBRACK
class DictionaryExpression(PrefixSubparser):

	def _parse_keyvals(self, parser, tokens):
		items = []
		while not tokens.is_end():
			key = Expression().parse(parser, tokens)
			if key is not None:
				tokens.consume_expected('COLON')
				value = Expression().parse(parser, tokens)
				if value is None: raise ParserError('Dictionary value expected', tokens.consume())
				items.append((key, value))
			else: break
			if tokens.current().name == 'COMMA': tokens.consume_expected('COMMA	')
			else: break
		return items

	def parse(self, parser, tokens):
		tokens.consume_expected('LCBRACK')
		items = self._parse_keyvals(parser, tokens)
		tokens.consume_expected('RCBRACK')
		return AST.Dictionary(items)


# infix expression: expr OPERATOR expr
class BinaryOperatorExpression(InfixSubparser):

	def parse(self, parser, tokens, left):
		token = tokens.consume_expected('OPERATOR')
		right = Expression().parse(parser, tokens, self.get_precedence(token))
		if right is None: raise ParserError('Expected expression'.format(token.value), tokens.consume())
		return AST.BinaryOperator(token.value, left, right)

	def get_precedence(self, token): return self.PRECEDENCE[token.value]


# call expression: NAME LPAREN list_of expression? RPAREN
class CallFunctionExpression(InfixSubparser):

	def parse(self, parser, tokens, left):
		tokens.consume_expected('LPAREN')
		arguments = ListOfExpressions().parse(parser, tokens)
		tokens.consume_expected('RPAREN')
		return AST.CallFunction(left, arguments)

	def get_precedence(self, token): return self.PRECEDENCE['call']


# subscript expression: NAME LBRACK expr RBRACK
class SubscriptOperatorExpression(InfixSubparser):

	def parse(self, parser, tokens, left):
		tokens.consume_expected('LBRACK')
		key = Expression().parse(parser, tokens)
		if key is None: raise ParserError('Subscript operator key is required', tokens.current())
		tokens.consume_expected('RBRACK')
		return AST.SubscriptOperator(left, key)

	def get_precedence(self, token): return self.PRECEDENCE['subscript']


class Expression(Subparser):

	def get_prefix_subparser(self, token):
		return self.get_subparser(token, {
			'NUMBER': NumberExpression,
			'STRING': StringExpression,
			'LOGIC': LogicExpression,
			'NAME': NameExpression,
			'LPAREN': GroupExpression,
 			'LBRACK': ListExpression,
 			'LCBRACK': SetExpression,
			'LCBRACK': DictionaryExpression,
			'OPERATOR': UnaryOperatorExpression,
		})

	def get_infix_subparser(self, token):
		return self.get_subparser(token, {
			'OPERATOR': BinaryOperatorExpression,
			'LPAREN': CallFunctionExpression,
			'LBRACK': SubscriptOperatorExpression,
		})

	def get_next_precedence(self, tokens):
		if not tokens.is_end():
			token = tokens.current()
			parser = self.get_infix_subparser(token)
			if parser is not None: return parser.get_precedence(token)
		return 0

	def parse(self, parser, tokens, precedence=0):
		subparser = self.get_prefix_subparser(tokens.current())
		if subparser is not None:
			left = subparser.parse(parser, tokens)
			if left is not None:
				while precedence < self.get_next_precedence(tokens):
					op = self.get_infix_subparser(tokens.current()).parse(parser, tokens, left)
					if op is not None: left = op
				return left


# list_of expression: (expr COLON)*
class ListOfExpressions(Subparser):

	def parse(self, parser, tokens):
		items = []
		while not tokens.is_end():
			exp = Expression().parse(parser, tokens)
			if exp is not None: items.append(exp)
			else: break
			if tokens.current().name == 'COMMA': tokens.consume_expected('COMMA')
			else: break
		return items



# block: NEWLINE INDENT stmnts DEDENT
class Block(Subparser):

	def parse(self, parser, tokens):
		tokens.consume_expected('NEWLINE', 'INDENT')
		statements = Statements().parse(parser, tokens)
		tokens.consume_expected('DEDENT')
		return statements


# func_stmnt: FUNCTION NAME LPAREN func_params? RPAREN COLON block
class FunctionStatement(Subparser):

	# func_params: (NAME COLON)*
	def _parse_params(self, tokens):
		params = []
		if tokens.current().name == 'NAME':
			while not tokens.is_end():
				id_token = tokens.consume_expected('NAME')
				params.append(id_token.value)
				if tokens.current().name == 'COMMA': tokens.consume_expected('COMMA')
				else:break
		return params

	def parse(self, parser, tokens):
		tokens.consume_expected('FUNCTION')
		id_token = tokens.consume_expected('NAME')
		tokens.consume_expected('LPAREN')
		arguments = self._parse_params(tokens)
		tokens.consume_expected('RPAREN')
		tokens.consume_expected('COLON')
		with enter_scope(parser, 'function'): block = Block().parse(parser, tokens)
		if block is None: raise ParserError('Expected function body', tokens.current())
		return AST.Function(id_token.value, arguments, block)

class ClassStatement(Subparser):

	# class_params: (NAME COLON)*
	# def _parse_params(self, tokens):
	# 	params = []
	# 	if tokens.current().name == 'NAME':
	# 		while not tokens.is_end():
	# 			id_token = tokens.consume_expected('NAME')
	# 			params.append(id_token.value)
	# 			if tokens.current().name == 'COMMA': tokens.consume_expected('COMMA')
	# 			else:break
	# 	return params

	def parse(self, parser, tokens):
		tokens.consume_expected('CLASS')
		id_token = tokens.consume_expected('NAME')
		# arguments = self._parse_params(tokens)
		tokens.consume_expected('COLON')
		with enter_scope(parser, 'class'): block = Block().parse(parser, tokens)
		if block is None: raise ParserError('Expected class body', tokens.current())
		return AST.Class(id_token.value, arguments, block)


# cond_stmnt: IF expr COLON block (ELIF COLON block)* (ELSE COLON block)?
class ConditionalStatement(Subparser):

	def _parse_elif_conditions(self, parser, tokens):
		conditions = []
		while not tokens.is_end() and tokens.current().name == 'ELIF':
			tokens.consume_expected('ELIF')
			test = Expression().parse(parser, tokens)
			if test is None: raise ParserError('Expected "elif" condition', tokens.current())
			tokens.consume_expected('COLON')
			with enter_scope(parser, 'condition'): block = Block().parse(parser, tokens)
			if block is None: raise ParserError('Expected "elif" body', tokens.current())
			conditions.append(AST.ConditionElif(test, block))
		return conditions

	def _parse_else(self, parser, tokens):
		else_block = None
		if not tokens.is_end() and tokens.current().name == 'ELSE':
			tokens.consume_expected('ELSE', 'COLON')
			with enter_scope(parser, 'condition'): else_block = Block().parse(parser, tokens)
			if else_block is None: raise ParserError('Expected "else" body', tokens.current())
		return else_block

	def parse(self, parser, tokens):
		tokens.consume_expected('IF')
		test = Expression().parse(parser, tokens)
		if test is None: raise ParserError('Expected "if" condition', tokens.current())
		tokens.consume_expected('COLON')
		with enter_scope(parser, 'condition'): if_block = Block().parse(parser, tokens)
		if if_block is None: raise ParserError('Expected if body', tokens.current())
		elif_conditions = self._parse_elif_conditions(parser, tokens)
		else_block = self._parse_else(parser, tokens)
		return AST.Condition(test, if_block, elif_conditions, else_block)

# exception_stmnt: DO COLON block (ELIF COLON block)* (LAST COLON block)?
class ExceptionStatement(Subparser):

	def _parse_error_exceptions(self, parser, tokens):
		exceptions = []
		while not tokens.is_end() and tokens.current().name == 'UNLESS':
			tokens.consume_expected('UNLESS')
			error = Expression().parse(parser, tokens)
			if error is None: raise ParserError('Expected "unless" exception', tokens.current())
			tokens.consume_expected('COLON')
			with enter_scope(parser, 'exception'): block = Block().parse(parser, tokens)
			if block is None: raise ParserError('Expected "unless" body', tokens.current())
			exceptions.append(AST.Unless(error, block))
		return exceptions

	def _parse_last(self, parser, tokens):
		last_block = None
		if not tokens.is_end() and tokens.current().name == 'LAST':
			tokens.consume_expected('LAST', 'COLON')
			with enter_scope(parser, 'exception'): last_block = Block().parse(parser, tokens)
			if last_block is None: raise ParserError('Expected "last" body', tokens.current())
		return last_block

	def parse(self, parser, tokens):
		tokens.consume_expected('DO', 'COLON')
		with enter_scope(parser, 'exception'): do_block = Block().parse(parser, tokens)
		if do_block is None: raise ParserError('Expected "do" body', tokens.current())
		unlesses = self._parse_error_exceptions(parser, tokens)
		last_block = self._parse_last(parser, tokens)
		return AST.Do(do_block, unlesses, last_block)

# when_stmnt: WHEN expr COLON NEWLINE INDENT when_is+ (ELSE COLON block)? DEDENT
class WhenStatement(Subparser):

	# match_when: IS expr COLON block
	def _parse_when(self, parser, tokens):
		tokens.consume_expected('IS')
		pattern = Expression().parse(parser, tokens)
		if pattern is None: raise ParserError('Pattern expression expected', tokens.current())
		tokens.consume_expected('COLON')
		with enter_scope(parser, 'cond'): block = Block().parse(parser, tokens)
		return AST.WhenPattern(pattern, block)

	def parse(self, parser, tokens):
		tokens.consume_expected('WHEN')
		test = Expression().parse(parser, tokens)
		tokens.consume_expected('COLON', 'NEWLINE', 'INDENT')
		patterns = []
		while not tokens.is_end() and tokens.current().name == 'IS':
			patterns.append(self._parse_when(parser, tokens))
		if not patterns:
			raise ParserError('One or more "when" pattern excepted', tokens.current())
		else_block = None
		if not tokens.is_end() and tokens.current().name == 'ELSE':
			tokens.consume_expected('ELSE', 'COLON')
			with enter_scope(parser, 'cond'): else_block = Block().parse(parser, tokens)
			if else_block is None:
				raise ParserError('Expected "else" body', tokens.current())
		tokens.consume_expected('DEDENT')
		return AST.When(test, patterns, else_block)


# loop_while_stmnt: WHILE expr COLON block
class WhileLoopStatement(Subparser):

	def parse(self, parser, tokens):
		tokens.consume_expected('WHILE')
		test = Expression().parse(parser, tokens)
		if test is None: raise ParserError('While condition expected', tokens.current())
		tokens.consume_expected('COLON')
		with enter_scope(parser, 'loop'): block = Block().parse(parser, tokens)
		if block is None: raise ParserError('Expected loop body', tokens.current())
		else_block = self._parse_else(parser, tokens)
		return AST.WhileLoop(test, block, else_block)

	def _parse_else(self, parser, tokens):
		else_block = None
		if not tokens.is_end() and tokens.current().name == 'ELSE':
			tokens.consume_expected('ELSE', 'COLON')
			else_block = Block().parse(parser, tokens)
			if else_block is None: raise ParserError('Expected "else" body', tokens.current())
		return else_block

# loop_for_stmnt: FOR NAME expr COLON block
class ForLoopStatement(Subparser):

	def parse(self, parser, tokens):
		tokens.consume_expected('FOR')
		id_token = tokens.consume_expected('NAME')
		tokens.consume_expected('IN')
		collection = Expression().parse(parser, tokens)
		tokens.consume_expected('COLON')
		with enter_scope(parser, 'loop'):
			block = Block().parse(parser, tokens)
		if block is None:
			raise ParserError('Expected loop body', tokens.current())
		return AST.ForLoop(id_token.value, collection, block)

# use_stmnt: USE NAME OF lib
class UseStatement(Subparser):

	def parse(self, parser, tokens):
		tokens.consume_expected('USE')
		obj = tokens.consume_expected('NAME')
		tokens.consume_expected('OF')
		library = tokens.consume_expected('NAME', 'NEWLINE')
		return AST.Use(obj.value, library)

# return_stmnt: RETURN expr?
class ReturnStatement(Subparser):

	def parse(self, parser, tokens):
		if not parser.scope or 'function' not in parser.scope:
			raise ParserError('Return outside of function', tokens.current())
		tokens.consume_expected('RETURN')
		value = Expression().parse(parser, tokens)
		tokens.consume_expected('NEWLINE')
		return AST.Return(value)

# throw_stmnt: THROW expr?
class ThrowStatement(Subparser):

	def parse(self, parser, tokens):
		if not parser.scope or 'function' not in parser.scope:
			raise ParserError('Throw outside of function', tokens.current())
		tokens.consume_expected('THROW')
		value = Expression().parse(parser, tokens)
		tokens.consume_expected('NEWLINE')
		return AST.Throw(value)


# quit_stmnt: QUIT
class QuitStatement(Subparser):

	def parse(self, parser, tokens):
		if not parser.scope or parser.scope[-1] != 'loop':
			raise ParserError('Quit outside of loop', tokens.current())
		tokens.consume_expected('QUIT', 'NEWLINE')
		return AST.Quit()


# cont_stmnt: CONTINUE
class ContinueStatement(Subparser):

	def parse(self, parser, tokens):
		if not parser.scope or parser.scope[-1] != 'loop':
			raise ParserError('Continue outside of loop', tokens.current())
		tokens.consume_expected('CONTINUE', 'NEWLINE')
		return AST.Continue()

# cont_stmnt: SKIP
class SkipStatement(Subparser):

	def parse(self, parser, tokens):
		if not parser.scope or parser.scope[-1] not in ['loop', 'condition', 'cond', 'exception'] and 'function' not in parser.scope:
			raise ParserError('Skip outside of loop or function', tokens.current())
		tokens.consume_expected('SKIP', 'NEWLINE')
		return AST.Skip()

# assing_stmnt: expr ASSIGN expr NEWLINE
class AssignmentStatement(Subparser):

	def parse(self, parser, tokens, left):
		tokens.consume_expected('ASSIGN')
		right = Expression().parse(parser, tokens)
		tokens.consume_expected('NEWLINE')
		return AST.Assignment(left, right)


# expr_stmnt: assing_stmnt
#           | expr NEWLINE
class ExpressionStatement(Subparser):

	def parse(self, parser, tokens):
		exp = Expression().parse(parser, tokens)
		if exp is not None:
			if tokens.current().name == 'ASSIGN':
				return AssignmentStatement().parse(parser, tokens, exp)
			else:
				tokens.consume_expected('NEWLINE')
				return exp


# stmnts: stmnt*
class Statements(Subparser):

	def get_statement_subparser(self, token):
		return self.get_subparser(token, {
			'FUNCTION': FunctionStatement,
			'CLASS': ClassStatement,
			'IF': ConditionalStatement,
			'USE': UseStatement,
			'DO': ExceptionStatement,
			'WHEN': WhenStatement,
			'WHILE': WhileLoopStatement,
			'FOR': ForLoopStatement,
			'RETURN': ReturnStatement,
			'THROW': ThrowStatement,
			'QUIT': QuitStatement,
			'CONTINUE': ContinueStatement,
			'SKIP': SkipStatement,			
		}, ExpressionStatement)

	def parse(self, parser, tokens):
		statements = []
		while not tokens.is_end():
			statement = self.get_statement_subparser(tokens.current()).parse(parser, tokens)
			if statement is not None:
				statements.append(statement)
			else:
				break
		return statements


# prog: stmnts
class Program(Subparser):

	def parse(self, parser, tokens):
		statements = Statements().parse(parser, tokens)
		tokens.expect_end()
		return AST.Program(statements)


class Parser(object):

	def __init__(self): self.scope = None
	def parse(self, tokens):
		self.scope = []
		return Program().parse(self, tokens)
