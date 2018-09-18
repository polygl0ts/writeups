from pwn import *
from sympy.parsing.sympy_parser import parse_expr
from sympy import Eq, Symbol as sym, solve

#Connect to server
r = remote("misc.chal.csaw.io", 9002)
while (True):
	try:
		#Get data from server
		x = r.recv()
		lines = x.split("\n")
		equation = lines[-2]
		#Split equation into L.H.S and R.H.S
		parts = equation.split("=")
		if len(parts) > 1:
			X = sym('X')
			lhs = parts[0].strip()
			rhs = parts[-1].strip()
			#Use parse_expr to convert the two sides of the equation from string to a format accepted by sympy
			lhs = parse_expr(lhs)
			rhs = parse_expr(rhs)
			#Solve equation
			eqa = Eq(lhs, rhs)
			res = solve(eqa)
			print "Result:", res
			#sympy returns answers of 0 and 1 as Boolean type which causes error while sending, handling these use cases 
			if str(res) == "True":
				r.send(str(float(1)) + "\n")
			if str(res) == "False":
				r.send(str(float(0)) + "\n")
			#Sending equation
			r.send(str(float(res[0])) + "\n")
	except EOFError as e:
		print "End"
		break
	