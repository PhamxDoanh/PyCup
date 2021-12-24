


import re
from collections import namedtuple, OrderedDict

from Cup.Errors import CupSyntaxError as LexerError
from Cup.Setup import iteritems


class Token(namedtuple('Token', ['name', 'value', 'line', 'column'])):
	def __repr__(self): return str(tuple(self))

def decode_str(s):
	regex = re.compile(r'\\(r|b|n|t|a|v|f|\\|\'|")')
	chars = {
		'r': '\r', # carriage return
		'b': '\b', # backspace
		'n': '\n', # newline
		't': '\t',# horizontal tab
		'a': '\a', # bell sound
		'v': '\v',# vertical tab
		'f':'\f', # form feed
		'\\': '\\',# backslash
		'"': '"',  # single quote
		"'": "'",  # double quote

	}

	def replace(matches):
		char = matches.group(1)[0]
		if char not in chars: raise Exception(f'Unknown escape character {char}')
		return chars[char]
	
	return regex.sub(replace, s[1:-1])


def decode_num(s):
	try: return int(s)
	except ValueError: return float(s)

# def decode_logic(s):
# 	try: return True
# 	except ValueError: False

class Lexer(object):

	rules = [
		('COMMENT', r'//.*'), # comment line
		('STRING', r'"(\\"|[^"])*"'),
		('STRING', r"'(\\'|[^'])*'"),
		('NUMBER', r'\d*\.\d+|\d+\.\d*|\d+'), # float + integer
		('LOGIC', r'true|false|null'),		
		('NAME', r'[a-zA-Z_]\w*'), # indentifier
		('WHITESPACE', r'[ \t]+'),
		('NEWLINE', r'\n+'),
		('OPERATOR', r'&&|\|\||\^\^|<<|>>'), # bitwises operators 
		('OPERATOR', r'\+|\-|\*|/|\\|%|\^'), # arithmetic operators
		('OPERATOR', r'<=>|><|<=|>=|==|!=|<|>'), # comparison operators
		('OPERATOR', r'&|\||!|and|or|not'), # boolean operators		
		('OPERATOR', r'\?|~|\+|\-'), # unary operator
		('ASSIGN', '='),
		('COLON', ':'),
		('LPAREN', r'\('),
		('RPAREN', r'\)'),
		('LBRACK', r'\['),
		('RBRACK', r'\]'),
		('LCBRACK', '{'),
		('RCBRACK', '}'),
		('COMMA', ','),
		('SEMICOLON', ';'),
		('DOT', '.'),

	]

	keywords = {
		'wait':'WAIT',      'else':'ELSE',      'use':'USE',        'skip':'SKIP',
		'quit':'QUIT',      'of':'OF',         	'throw':'THROW',	'is': 'IS',
		'class':'CLASS',    'last':'LAST',      'return':'RETURN',	'while':'WHILE',
		'for':'FOR',        'when':'WHEN',      'do':'DO',          'continue':'CONTINUE',
		'as':'AS',          'let':'FUNCTION',   'from':'FROM',      'local':'LOCAL',  'global':'GLOBAL',  
		'sync':'SYNC',      'elif':'ELIF',      'if':'IF',			'in': 'IN',  'last': 'LAST', 'unless': 'UNLESS',
	}

	ignore_tokens = [
		'WHITESPACE',
		'COMMENT',
	]

	decoders = {
		'STRING': decode_str,
		'NUMBER': decode_num,
		# 'LOGIC': decode_logic,
	}

	def __init__(self):
		self.source_lines = []
		self._regex = self._compile_rules(self.rules)

	def _convert_rules(self, rules):
		grouped_rules = OrderedDict()
		for name, pattern in rules:
			grouped_rules.setdefault(name, [])
			grouped_rules[name].append(pattern)

		for name, patterns in iteritems(grouped_rules):
			joined_patterns = '|'.join(['({})'.format(p) for p in patterns])
			yield f'(?P<{name}>{joined_patterns})'

	def _compile_rules(self, rules):
		return re.compile('|'.join(self._convert_rules(rules)))

	def _tokenize_line(self, line, line_num):
		pos = 0
		while pos < len(line):
			matches = self._regex.match(line, pos)
			if matches is not None:
				name = matches.lastgroup
				pos = matches.end(name)
				if name not in self.ignore_tokens:
					value = matches.group(name)
					if name in self.decoders:
						value = self.decoders[name](value)
					elif name == 'NAME' and value in self.keywords:
						name = self.keywords[value]
						value = None
					yield Token(name, value, line_num, matches.start() + 1)
			else:
				raise LexerError(f'Unexpected character {line[pos]}', line_num, pos + 1)

	def _count_leading_characters(self, line, char):
		count = 0
		for c in line:
			if c != char: break
			count += 1
		return count

	def _detect_indent(self, line):
		if line[0] in (' ', '\t'):
			return line[0] * self._count_leading_characters(line, line[0])

	def tokenize(self, s):
		indent_symbol = None
		tokens = []
		last_indent_level = 0
		line_num = 0
		for line_num, line in enumerate(s.splitlines(), 1):
			line = line.rstrip()

			if not line:
				self.source_lines.append('')
				continue

			if indent_symbol is None:
				indent_symbol = self._detect_indent(line)

			if indent_symbol is not None:
				indent_level = line.count(indent_symbol)
				line = line[indent_level*len(indent_symbol):]
			else:
				indent_level = 0

			self.source_lines.append(line)

			line_tokens = list(self._tokenize_line(line, line_num))
			if line_tokens:
				if indent_level != last_indent_level:
					if indent_level > last_indent_level:
						tokens.extend([Token('INDENT', None, line_num, 0)] * (indent_level - last_indent_level))
					elif indent_level < last_indent_level:
						tokens.extend([Token('DEDENT', None, line_num, 0)] * (last_indent_level - indent_level))
					last_indent_level = indent_level

				tokens.extend(line_tokens)
				tokens.append(Token('NEWLINE', None, line_num, len(line) + 1))

		if last_indent_level > 0:
			tokens.extend([Token('DEDENT', None, line_num, 0)] * last_indent_level)

		return tokens


class TokenStream(object):

	def __init__(self, tokens):
		self._tokens = tokens
		self._pos = 0

	def consume_expected(self, *args):
		token = None
		for expected_name in args:
			token = self.consume()
			if token.name != expected_name:
				raise LexerError(f'Expected {expected_name}, got {token.name}', token.line, token.column)
		return token

	def consume(self):
		token = self.current()
		self._pos += 1
		return token

	def current(self):
		try:
			return self._tokens[self._pos]
		except IndexError:
			last_token = self._tokens[-1]
			raise LexerError('Unexpected end of input', last_token.line, last_token.column)

	def expect_end(self):
		if not self.is_end():
			token = self.current()
			raise LexerError('End expected', token.line, token.column)

	def is_end(self):
		return self._pos == len(self._tokens)
