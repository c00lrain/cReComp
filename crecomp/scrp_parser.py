# -*- coding: utf-8 -*-
import ply.lex as lex
import ply.yacc as yacc
import os
import verilog as vl
import component as cp
import communication as com
import userlogic as ul

tokens = [
	'INPUT',
	'OUTPUT',
	'INOUT',
	'REG',
	'WIRE',
	'EQUALL',
	'LBRACES',
	'RBRACES',
	'STRING',
	'LBRACKET',
	'RBRACKET',
	'NUMBER',

	'COMPONENT_NAME',
	'COMMUNICAITION',

	'XILLYBUS',
	'XILLYBUS32_RCV',
	'XILLYBUS32_SND',
	'XILLYBUS8_RCV',
	'XILLYBUS8_SND',

	'USERLOGIC_PATH',
	'INSTANCE_NAME',
	'USERLOGIC_INPUT',
	'USERLOGIC_OUTPUT',
	'USERLOGIC_INOUT',

	'END'
]

t_INPUT = r'input'
t_OUTPUT = r'output'
t_INOUT = r'inout'
t_REG = r'reg'
t_WIRE = r'wire'

t_EQUALL = r'\='
t_LBRACES = r'{'
t_RBRACES = r'}'
LBRACKET = r'\['
RBRACKET = r'\]'

t_COMPONENT_NAME = r'component_name'
t_COMMUNICAITION = r'communication'

t_XILLYBUS = r'xillybus'
t_XILLYBUS32_RCV = r'xillybus32_snd'
t_XILLYBUS32_SND = r'xillybus32_rcv'
t_XILLYBUS8_RCV = r'xillybus8_snd'
t_XILLYBUS8_SND = r'xillybus8_rcv'

t_USERLOGIC_PATH = r'userlogic_path'
t_INSTANCE_NAME = r'instance_name'
t_END = r'end'

def t_NUMBER(t):
	r'\d+'
	t.value = int(t.value)
	return t
def t_STRING(t):
	r'\".*?\"'
	t.value = str(t.value).translate(None,"\"")
	return t
def t_newline(t):
	r'\n+'
	t.lexer.lineno += len(t.value)
def t_COMMENT(t):
	r'\#.*'
	pass

t_ignore = ' \t\n'

def t_error(t):
	print u"Illegal '%s'" % t.value[0]

lexer = lex.lex()

# ======================================

class ParseScrp():
	def __init__(self, scrp_path):
		self.component = None
		self.parser = None
		self.scrp_path = scrp_path
		self.scrp = open(scrp_path)

		def p_expression_component(p):
			'expression : COMPONENT_NAME STRING'
			self.component = cp.Component(p[2])
			print "start generation", p[2]

		def p_expression_rbraces(p):
			'expression : RBRACES'
			p[0] = "}"
		def p_expression_lbraces(p):
			'expression : LBRACES'
			p[0] = "{"

		def p_expression_signal(p):
			'''expression : INPUT NUMBER STRING
							| OUTPUT NUMBER STRING
							| INOUT NUMBER STRING
							| REG NUMBER STRING
							| WIRE NUMBER STRING
			'''
			bit = p[2]
			name = p[3]
			if p[1] == "input":
				self.component.add_input(name, bit)
				print "added input", p[2], p[3]
			elif p[1] == "output":
				self.component.add_output(name, bit)
				print "added output", p[2], p[3]
			elif p[1] == "inout":
				self.component.add_inout(name, bit)
				print "added inout", p[2], p[3]
			elif p[1] == "reg":
				self.component.add_reg(name, bit)
				print "added reg", p[2], p[3]
			elif p[1] == "wire":
				self.component.add_wire(name, bit)
				print "added wire", p[2], p[3]

		def p_expression_communication_xillybus(p):
			'''expression : COMMUNICAITION XILLYBUS NUMBER NUMBER STRING NUMBER
			'''
			if p[6] != 32 and p[6] != 8:
				raise Exception("Error. Xillybus fifo width is 8 bit or 32 bit")
			com_ = com.Xillybus_fifo(p[3],p[4],p[5],p[6])
			self.component.add_com(com_)

		def p_expression_xillybus_assign(p):
			'''expression : XILLYBUS32_RCV STRING
						| XILLYBUS32_SND STRING
						| XILLYBUS8_RCV STRING
						| XILLYBUS8_SND STRING
			'''
			for com_ in self.component.module["communication"]:
				name = p[2]
				if com_.__class__.__name__ == "Xillybus_fifo" and com_.fifo_width == 32:
					if p[1] == "xillybus32_rcv":
						com_.assign("rcv", name)
						break
					elif p[1] == "xillybus32_snd":
						com_.assign("snd", name)
						break
				elif com_.__class__.__name__ == "Xillybus_fifo" and com_.fifo_width == 8:
					if p[1] == "xillybus8_rcv":
						com_.assign("rcv", name)
						break
					elif p[1] == "xillybus8_snd":
						com_.assign("snd", name)
						break

		def p_expression_userlogic(p):
			'expression : USERLOGIC_PATH STRING INSTANCE_NAME STRING'
			name =os.path.basename(p[2]).replace(".v","")
			ul_ = ul.UserlogicBase(name,p[4])
			info = ul.Info()
			info.get_userlogicinfo(p[2])
			ul_.ports = info.ports

			print ul_.get_portnames()


		def p_expression_end(p):
			'expression : END'
			p[0] = -1

		self.parser = yacc.yacc()

		line = ""
		while True:
			line = self.scrp.readline()
			if self.parser.parse(line) == -1:
				break


if __name__ == '__main__':

	paser = ParseScrp("sample.scrp")
	paser.component.show_myinfo()
	paser.component.componentize()