

class CupSyntaxError(Exception):

	def __init__(self, mess, ln, col):
		super(CupSyntaxError, self).__init__(mess)
		self.mess = mess
		self.ln = ln
		self.col = col

def report_error(lexer, error):
	ln = error.ln
	col = error.col
	src_ln = lexer.source_lines[ln - 1]
	print(f'Syntax error: {error.mess} at line {ln}, column {col}')
	print(f'{src_ln}\n{" " * (col - 1)}^')
