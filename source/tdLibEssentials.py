import random
import string

def cutUniqName (glyphname):
	if 'uuid' in glyphname:
		a = glyphname.split('.')[:-1]
		return '.'.join(a)
	return glyphname



def getUniqName(cut=32):
	def ran_gen (size, chars=string.ascii_uppercase + string.digits):
		return ''.join(random.choice(chars) for x in range(size))
	return 'uuid' + ran_gen(cut, "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")

def uniqueName(name = None, cut = 32):
	if name:
		return '%s.uuid%s' % (name, ran_gen(cut, "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"))
	return 'uuid%s' % ran_gen(cut, "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
