"""
ScriptBoard is an extension for quickly launching your favorite scripts. 
In order for scripts to run, they must follow this format:
```
	def main():
		print ("place your code here")

	if __name__ == "__main__":
		main()

```
"""

import os, sys, importlib
from AppKit import *
from mojo.UI import *
from vanilla import *
from vanilla.dialogs import getFile
# from plistlib import readPlist


from mojo.extensions import getExtensionDefault, setExtensionDefault

_baseDefaultKey = "com.typedev.ScriptBoard"
_dataDefaultKey = "%s.data" % _baseDefaultKey


class ScriptBoardSettings(object):
	_fallbackData = {'pos': (200,200,200,400), 'scripts': []}

	def __init__ (self):
		self.load()

	def load (self):
		self.data = getExtensionDefault(_dataDefaultKey, self._fallbackData)

	def save (self):
		setExtensionDefault(_dataDefaultKey, self.data)

	def get (self, key):
		try:
			return self.data[key]
		except:
			return None

	def set (self, key, value):
		self.data[key] = value



class ScriptsBoard:
	def __init__(self):
		self._prefs = ScriptBoardSettings()
		self._prefs.load()
		self._pos = self._prefs.get('pos')
		x, y, w, h = self._pos
		self.w = FloatingWindow((w, h),minSize = (100, 200), title = 'Scripts Board')
		self.w.setPosSize(self._pos)
		self.w.scriptsListing = List((5,30,-5,-5),
		                             items=[],
		                             allowsMultipleSelection = False,
		                             doubleClickCallback=self.scriptsListDblClickCallback
		                             )
		self.w.btnAdd = Button((-65, 5, 27,20),title='+',
		                           callback=self.btnAddCallback,
		                           sizeStyle='regular',
		                           )
		self.w.btndel = Button((-35, 5, 27, 20), title = '-',   callback=self.btnDelCallback,
		                       sizeStyle = 'regular',
		)

		# self.w.btnCompile.bind(key='r',modifiers=['command'])

		self.w.bind("close", self.windowClose)
		self.loadScriptsList()
		self.w.open()

	def windowClose(self, sender):
		self._prefs.set('pos',self.w.getPosSize())
		self._prefs.save()

	def loadScriptsList(self):
		slist = []
		self.w.scriptsListing.set([])
		slist = self._prefs.get('scripts')
		for scriptdata in slist:
			name, path = scriptdata
			self.w.scriptsListing.append(name)

	def addScriptToList(self, path):
		nameraw = path.split('/')[-1]
		name, ext = nameraw.split('.')
		s = self._prefs.get('scripts')
		if ext == 'py':
			s.append((name,path))
			# self._prefs.set('scripts',s)
			self.loadScriptsList()
		elif ext == 'roboFontExt':
			pass
			# print 'extension', name
			# plist = readPlist('%s/info.plist' % path)
			# name_ext = plist['name']
			# for items in plist['addToMenu']:
			# 	# for key, value in items.items():
			# 	py_path = '%s/lib/%s' % (path, items['path'])
			# 	name_script = items['preferredName']
			# 	# print name_ext, name_script, py_path
			# 	s.append(('%s.%s' % (name_ext, name_script),py_path))
			# self.loadScriptsList()
		else:
			print ('Wrong file format!..')


	def scriptsListDblClickCallback(self, sender):
		idx = self.w.scriptsListing.getSelection()
		name, path = self._prefs.get('scripts')[idx[0]]
		print ('Running',name,path)
		sys.path.append(path)
		m = importlib.import_module(name)
		importlib.reload(m)
		m.main()
		# path = '/usr/local/bin/robofont -p "%s"' % path
		# print (path)
		# os.system(path)

	def btnAddCallback(self, sender):
		path = getFile()[0]
		if path !=None:
			self.addScriptToList( path )

	def btnDelCallback(self, sender):
		idx = self.w.scriptsListing.getSelection()
		s = self._prefs.get('scripts')
		for id in idx:
			s.pop(id)
		self.loadScriptsList()

ScriptsBoard()