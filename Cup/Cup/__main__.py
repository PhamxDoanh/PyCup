

import argparse # từ python
from Cup import __version__ as ver, __documents__ as docs, Interpreter


try: input = raw_input
except NameError: pass


def parse_args():
	argparser = argparse.ArgumentParser()
	argparser.add_argument('-v', '--verbose', action='store_true')
	argparser.add_argument('file', nargs='?')
	return argparser.parse_args()


def runFile(path, verbose = False):
	with open(path) as f:
		print(str(Interpreter.evaluate(f.read(), verbose = verbose)).removesuffix('None')) # removesuffix() | giải pháp tạm thời


def runPrompt():
	print(f'Welcome to Cup {ver}! Type "help" for more information.')
	env = Interpreter.create_global_env()
	while True:
		try:
			inp = input('[Cup] ')
			if inp.strip().lower() == 'exit()': break
			if inp.replace(' ', '')[-1] == ':':
				while True:
					nxtinp = input('[...] ')
					if not nxtinp: break
					else: inp += '\n' + nxtinp
			print(str(Interpreter.evaluate_env(inp, env)).removesuffix("None"))
		except KeyboardInterrupt: print('[Suggest] Type "exit()" for end!')


def main():
	args = parse_args()
	extensions = ['cup', 'cp', 'u']
	if args.file:
		if args.file.split('.')[-1] in extensions: runFile(args.file, args.verbose)
		else: print("Invalid fileType for Cup (.cup, .cp, .u)")
	else: runPrompt()

if __name__ == '__main__': main()
