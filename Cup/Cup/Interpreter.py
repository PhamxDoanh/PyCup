

from __future__ import print_function
from collections import namedtuple
import operator, math

from Cup import AST
from Cup.Lexer import Lexer, TokenStream
from Cup.Parser import Parser, ListOfExpressions
from Cup.Errors import CupSyntaxError, report_error
from Cup.Utils import print_ast, print_tokens, print_env



class Quit(Exception): pass
class Continue(Exception): pass
class Skip(Exception): pass

class Return(Exception):
	def __init__(self, value):
		self.value = value

class Throw(Exception):
	def __init__(self, value):
		self.value = value

class Environment(object):

	def __init__(self, parent=None, args=None):
		self._parent = parent
		self._values = {}
		if args is not None:
			self._from_dict(args)

	def _from_dict(self, args):
		for key, value in args.items():
			self.set(key, value)

	def set(self, key, val):
		self._values[key] = val

	def get(self, key):
		val = self._values.get(key, None)
		if val is None and self._parent is not None:
			return self._parent.get(key)
		else:
			return val

	def asdict(self):
		return self._values

	def __repr__(self):
		return f'Environment({str(self._values)})'


def eval_bin_op(node, env):
	simple_operations = {
		'+': operator.add,
		'-': operator.sub,
		'*': operator.mul,
		'/': operator.truediv,
		'\\': operator.floordiv,
		'%': operator.mod,
		'^': operator.pow,
		'<<': operator.lshift,
		'>>': operator.rshift,
		'&&': operator.and_,
		'||':operator.or_,
		'^^': operator.xor,
		'>': operator.gt,
		'>=': operator.ge,
		'<': operator.lt,
		'<=': operator.le,
		'==': operator.eq,
		'!=': operator.ne,
		'><': lambda obj1, obj2: False if set(obj1) & set(obj2) else True,
		'<=>': lambda obj1, obj2: float(obj1) == float(obj2), 

	}
	lazy_operations = {
		'&': lambda obj1, obj2: obj1 and obj2,
		'and': lambda obj1, obj2: obj1 and obj2,
		'|': lambda obj1, obj2: obj1 or obj2,
		'or': lambda obj1, obj2: obj1 or obj2,
	}
	if node.operator in simple_operations: return simple_operations[node.operator](eval_expression(node.left, env), eval_expression(node.right, env))
	elif node.operator in lazy_operations: return lazy_operations[node.operator](bool(eval_expression(node.left, env)), bool(eval_expression(node.right, env)))
	else: raise Exception(f'Invalid operator {node.operator}')


def eval_unary_op(node, env):
	operations = {
		'+': operator.pos,
		'-': operator.neg,
		'!': operator.not_,
		'not': operator.not_,
		'?': lambda obj: type(obj),
		'~': lambda obj: round(obj),
	}
	return operations[node.operator](eval_expression(node.right, env))


def eval_assignment(node, env):

	if isinstance(node.left, AST.SubscriptOperator): return eval_setitem(node, env)
	else: return env.set(node.left.value, eval_expression(node.right, env))


def eval_condition(node, env):
	try:
		if eval_expression(node.test, env): return eval_statements(node.if_body, env)

		for cond in node.elifs:
			if eval_expression(cond.test, env):
				return eval_statements(cond.body, env)

		if node.else_body is not None: return eval_statements(node.else_body, env)
	except Skip: pass

def eval_exception(node, env):
	if node.do_body is not None:
		try:
			eval_statements(node.do_body, env)
		except Exception as e:
			for exc in node.errors:
				if eval_expression(exc.errors, env): return eval_statements(exc.body, env)
		finally:
			if node.last_body is not None: return eval_statements(node.last_body, env)

def eval_use(node, env):
	obj = node.obj
	library = node.library
	if str(obj) == 'pi' and str(library) == 'math': from math import pi
	else: import math

def eval_when(node, env):
	test = eval_expression(node.test, env)
	for pattern in node.patterns:
		if eval_expression(pattern.pattern, env) == test:
			return eval_statements(pattern.body, env)
	if node.else_body is not None:
		return eval_statements(node.else_body, env)


def eval_while_loop(node, env):
	while eval_expression(node.test, env):
		try: eval_statements(node.body, env)
		except Quit: break
		except Continue: pass
		except Skip: pass 
	else:
		try:
			if node.else_body is not None: return eval_statements(node.else_body, env)
		except Skip: pass


def eval_for_loop(node, env):
	var_name = node.var_name
	collection = eval_expression(node.collection, env)
	for val in collection:
		env.set(var_name, val)
		try: eval_statements(node.body, env)
		except Quit: break
		except Continue: pass
		except Skip: pass 


def eval_func_decla(node, env): return env.set(node.name, node)

def eval_call_func(node, env):
	function = eval_expression(node.left, env)
	n_expected_args = len(function.params)
	n_actual_args = len(node.arguments)
	if n_expected_args != n_actual_args:
		raise TypeError(f'Expected {n_expected_args} arguments, got {n_actual_args}')
	args = dict(zip(function.params, [eval_expression(node, env) for node in node.arguments]))
	if isinstance(function, AST.BuiltinFunction):
		return function.body(args, env)
	else:
		call_env = Environment(env, args)
		try: return eval_statements(function.body, call_env)
		except Return as ret: return ret.value
		except Throw as thw: return thw.value

def eval_class_decla(node, env): return env.set(node.name, node)

def eval_call_class(node, env):
	function = eval_expression(node.left, env)
	n_expected_args = len(function.params)
	n_actual_args = len(node.arguments)
	if n_expected_args != n_actual_args:
		raise TypeError(f'Expected {n_expected_args} arguments, got {n_actual_args}')
	args = dict(zip(function.params, [eval_expression(node, env) for node in node.arguments]))
	if isinstance(function, AST.BuiltinFunction):
		return function.body(args, env)
	else:
		call_env = Environment(env, args)
		return eval_statements(function.body, call_env)
 
def eval_identifier(node, env):
	name = node.value
	val = env.get(name)
	if val is None: raise NameError(f'Name "{name}" is not defined')
	return val


def eval_getitem(node, env):
	collection = eval_expression(node.left, env)
	key = eval_expression(node.key, env)
	return collection[key]


def eval_setitem(node, env):
	collection = eval_expression(node.left.left, env)
	key = eval_expression(node.left.key, env)
	collection[key] = eval_expression(node.right, env)


def eval_list(node, env): return [eval_expression(item, env) for item in node.items]
def eval_set(node, env): return set({eval_expression(item, env) for item in node.items})
# def eval_packs(node, env): return [eval_expression(item, env) for item in node.items]
def eval_shell(node, env): return tuple((eval_expression(item, env) for item in node.items))
def eval_dict(node, env): return {eval_expression(key, env): eval_expression(value, env) for key, value in node.items}

def eval_return(node, env): return eval_expression(node.value, env) if node.value is not None else None
def eval_throw(node, env):
	if node.value is not None:
		for val in eval_expression(node.value, env):
			yield val 
	else: return None


evaluators = {
	AST.Number: lambda node, env: node.value,
	AST.String: lambda node, env: node.value,
	AST.Logic: lambda node, env: node.value,
	AST.List: eval_list,
	# AST.Set: eval_set,
	# AST.Packs: eval_packs,
	AST.Shell: eval_shell,
	AST.Dictionary: eval_dict,
	AST.Identifier: eval_identifier,
	AST.BinaryOperator: eval_bin_op,
	AST.UnaryOperatorPrefix: eval_unary_op,
	AST.SubscriptOperator: eval_getitem,
	AST.Assignment: eval_assignment,
	AST.Condition: eval_condition,
	AST.Use: eval_use,
	AST.Do: eval_exception,
	AST.When: eval_when,
	AST.WhileLoop: eval_while_loop,
	AST.ForLoop: eval_for_loop,
	AST.Function: eval_func_decla,
	AST.Class: eval_class_decla,
	AST.CallFunction: eval_call_func,
	AST.CallClass: eval_call_class,
	AST.Return: eval_return,
	AST.Throw: eval_throw,
}


def eval_node(node, env):
	tp = type(node)
	if tp in evaluators:
		return evaluators[tp](node, env)
	else:
		raise Exception(f'Unknown node {tp.__name__} {node}')


def eval_expression(node, env): return eval_node(node, env)


def eval_statement(node, env): return eval_node(node, env)


def eval_statements(statements, env):
	ret = None
	for statement in statements:
		if isinstance(statement, AST.Quit): raise Quit(ret)
		elif isinstance(statement, AST.Continue): raise Continue(ret)
		elif isinstance(statement, AST.Skip): raise Skip(ret)
		ret = eval_statement(statement, env)
		if isinstance(statement, AST.Return): raise Return(ret)
		elif isinstance(statement, AST.Throw): raise Throw(ret)
	return ret

# for the future
def add_builtins(env):
	builtins = {

		# input/output system
		'read': (['inp'], lambda args, e: input(args['inp'])),
		'say': (['out'], lambda args, e: print(args['out'])),	

		# string, list, ... function
		'size': (['obj'], lambda args, e: len(args['obj'])),
		'cut': (['obj', 'start', 'stop', 'step'], lambda args, e: list(args['obj'][args['start']:args['stop']])),
		'swap': (['obj', 'obj1', 'obj2'], lambda args, e: args['obj'].replace([args['obj1'], args['obj2']])),
		'invert': (['obj'], lambda args, e: args['obj'][::-1]),
		'sort': (['obj'], lambda args, e: sorted(args['obj'])),
		'add':(['obj1', 'obj'], lambda args, e: args['obj'].append(args['obj1'])),
		'find': (['obj1', 'obj'], lambda args, e: args['obj'].find(args['obj1'])),
		'count': (['obj1', 'obj'], lambda args, e: args['obj'].count(args['obj1'])),
		'erase': (['obj1', 'obj'], lambda args, e: args['obj'].remove(args['obj1'])),			
		'clear': (['obj'], lambda args, e: args['obj'].clear()),			
		'upcase': (['str'], lambda args, e: args['str'].upper()),
		'lowcase': (['str'], lambda args, e: args['str'].lower()),
		'isupcase': (['str'], lambda args, e: args['str'].isupper()),
		'islowcase': (['str'], lambda args, e: args['str'].islower()),
		'title': (['str'], lambda args, e: args['str'].title()),
		'istitle': (['str'], lambda args, e: args['str'].istitle()),
		'isalpha': (['str'], lambda args, e: args['str'].isalpha()),
		'isdigit': (['str'], lambda args, e: args['str'].isdigit()),
		'isascii': (['str'], lambda args, e: args['str'].isascii()),
		'translate': (['str', 'lang'], lambda args, e: args['str'].translate(args['lang'])),
		'keys': (['obj'], lambda args, e: args['obj'].keys()),
		'values': (['obj'], lambda args, e: args['obj'].values()),
		'items': (['obj'], lambda args, e: args['obj'].items()),		
		'copy': (['obj'], lambda args, e: args['obj'].copy()),
		'join': (['txt', 'obj'], lambda args, e: args['obj'].join(args['txt'])),
		'split': (['txt', 'obj'], lambda args, e: args['txt'].split(args['obj'] if args['obj'] else " ")),

		# converter
		'ordinal': (['obj'], lambda args, e: ord(args['obj'])),'ord': (['obj'], lambda args, e: ord(args['obj'])),
		'string': (['obj'], lambda args, e: str(args['obj'])),'str': (['obj'], lambda args, e: str(args['obj'])),
		'char': (['obj'], lambda args, e: chr(args['obj'])),'chr': (['obj'], lambda args, e: chr(args['obj'])),
		'integer': (['obj'], lambda args, e: int(args['obj'])),'int': (['obj'], lambda args, e: int(args['obj'])),
		'decimal': (['obj'], lambda args, e: float(args['obj'])),'dec': (['obj'], lambda args, e: float(args['obj'])),
		'complex': (['obj'], lambda args, e: complex(args['obj'])),'cmplx': (['obj'], lambda args, e: complex(args['obj'])),
		'logic': (['obj'], lambda args, e: bool(args['obj'])),'bool': (['iter'], lambda args, e: list(args['iter'])),
		'list': (['iter'], lambda args, e: list(args['iter'])),
		'set': (['iter'], lambda args, e: set(args['iter'])),
		'shell': (['iter'], lambda args, e: tuple(args['iter'])),
		'dict': (['iter'], lambda args, e: dict(args['iter'])),
		'bin': (['obj'], lambda args, e: bin(args['obj'])),
		'hex': (['obj'], lambda args, e: hex(args['obj'])),
		'oct': (['obj'], lambda args, e: oct(args['obj'])),
		# math function
		'round': (['obj'], lambda args, e: round(args['obj'])),
		'abs': (['obj'],  lambda args, e: abs(args['obj'])),
		'sqrt': (['obj'], lambda args, e: math.sqrt(args['obj'])),
		'cbrt': (['obj'], lambda args, e: args['obj']**(1/3)),
		'pow': (['obj', 'obj1'], lambda args, e: pow(args['obj'], args['obj1'])),
		'max': (['obj'], lambda args, e: max(args['obj'])),
		'min': (['obj'], lambda args, e: min(args['obj'])),
		'solve': (['obj'], lambda args, e: eval(args['obj'])),
		'lcm': (['obj'], lambda args, e: math.lcm(args['obj'])),
		'gcd': (['obj'], lambda args, e: math.gcd(args['obj'])),
		'sum': (['obj'], lambda args, e: sum(args['obj'])),		
		'prod': (['obj'], lambda args, e: math.prod(args['obj'])),	
		'ceil': (['obj'], lambda args, e: math.ceil(args['obj'])),	
		'floor': (['obj'], lambda args, e: math.floor(args['obj'])),	
		'factorial': (['obj'], lambda args, e: math.factorial(args['obj'])),	
		'log': (['base', 'obj'], lambda args, e: math.log(args['obj'], args['base'])),	
		'sin': (['obj'], lambda args, e: math.sin(args['obj'])),	
		'cos': (['obj'], lambda args, e: math.cos(args['obj'])),	
		'tan': (['obj'], lambda args, e: math.tan(args['obj'])),
		'sinh': (['obj'], lambda args, e: math.sinh(args['obj'])),	
		'cosh': (['obj'], lambda args, e: math.cosh(args['obj'])),	
		'tanh': (['obj'], lambda args, e: math.tanh(args['obj'])),
		'asin': (['obj'], lambda args, e: math.asin(args['obj'])),	
		'acos': (['obj'], lambda args, e: math.acos(args['obj'])),	
		'atan': (['obj'], lambda args, e: math.atan(args['obj'])),
		'asinh': (['obj'], lambda args, e: math.asinh(args['obj'])),	
		'acosh': (['obj'], lambda args, e: math.acosh(args['obj'])),	
		'atanh': (['obj'], lambda args, e: math.atanh(args['obj'])),	
		'deg': (['obj'], lambda args, e: math.degrees(args['obj'])),	
		'rad': (['obj'], lambda args, e: math.radians(args['obj'])),		
		# other function
		'limit': (['start', 'stop', 'step'], lambda args, e: range(args['start'], args['stop'], args['step'])),
		'about': (['obj'], lambda args, e: dir(args['obj'])),		
		'typeof': (['obj'], lambda args, e: type(args['obj'])),
		'enum': (['obj'], lambda args, e: enumerate(args['obj'])),
		'all': (['obj'], lambda args, e: all(args['obj'])),
		'any': (['obj'], lambda args, e: any(args['obj'])),
		'merge': (['obj1', 'obj2'], lambda args, e: zip(args['obj1'], args['obj2'])),
		'run': (['code'], lambda args, e: exec(args['code'])),
		'filter': (['obj', 'cond'], lambda args, e: filter(args['cond'], args['obj'])),
		'id': (['obj'], lambda args, e: id(args['obj'])),

	}
	for key, (params, func) in builtins.items():
		env.set(key, AST.BuiltinFunction(params, func))


def create_global_env():
	env = Environment()
	add_builtins(env)
	return env


def evaluate_env(s, env, verbose=False):
	lexer = Lexer()
	try: tokens = lexer.tokenize(s)
	except CupSyntaxError as err:
		report_error(lexer, err)
		if verbose: raise
		else: return

	if verbose:
		print('Tokens')
		print_tokens(tokens)
		print()

	token_stream = TokenStream(tokens)

	try: program = Parser().parse(token_stream)
	except CupSyntaxError as err:
		report_error(lexer, err)
		if verbose: raise
		else: return

	if verbose:
		print('AST')
		print_AST(program.body)
		print()

	ret = eval_statements(program.body, env)

	if verbose:
		print('Environment')
		print_env(env)
		print()

	return ret


def evaluate(s, verbose=False):
	return evaluate_env(s, create_global_env(), verbose)
