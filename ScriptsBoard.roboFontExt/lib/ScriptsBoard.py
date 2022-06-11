"""
ScriptBoard is an extension for quickly launching your favorite scripts. 
In order for scripts to run, they must follow this format:
```
	__doc__ = 'description'

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



class ScriptBoardSettings(object):
	_fallbackData = {'pos': (200,200,200,400), 'scripts': []}

	def __init__ (self, settings):
		self.settings = settings
		self.load()

	def load (self):
		self.data = getExtensionDefault(self.settings['_dataDefaultKey'], self._fallbackData)

	def save (self):
		setExtensionDefault(self.settings['_dataDefaultKey'], self.data)

	def get (self, key):
		try:
			return self.data[key]
		except:
			return None

	def set (self, key, value):
		self.data[key] = value



class ScriptsBoard:
	def __init__(self, parent = None):
		_version = '0.4'
		self.parent = parent
		if not parent:
			_baseDefaultKey = "com.typedev.ScriptBoard"
			_dataDefaultKey = "%s.data" % _baseDefaultKey
		else:
			_baseDefaultKey = "com.typedev.ScriptBoard.%s" % self.parent.idName
			_dataDefaultKey = "%s.data" % _baseDefaultKey

		settings = dict(
			_baseDefaultKey = _baseDefaultKey,
			_dataDefaultKey = _dataDefaultKey
		)

		self._prefs = ScriptBoardSettings(settings)
		self._prefs.load()
		self._pos = self._prefs.get('pos')
		x, y, w, h = self._pos
		self.w = FloatingWindow((w, h),minSize = (100, 200), title = 'Scripts Board %s' % _version)
		self.w.setPosSize(self._pos)
		# self.w.toolbar = Group('auto')

		self.w.scriptsListing = List((0,0,-0,-0),
		                             items=[],
		                             allowsMultipleSelection = False,
		                             selectionCallback = self.scriptsListSelectionCallback,
		                             doubleClickCallback=self.scriptsListDblClickCallback
		                             )
		self.w.btnAdd = Button((-65, 5, 27, 20),title='+',
		                           callback=self.btnAddCallback,
		                           sizeStyle='regular',
		                           )
		self.w.btnDel = Button((-35, 5, 27, 20), title = '-',   callback=self.btnDelCallback,
		                       sizeStyle = 'regular',
		)
		self.w.textBox = TextEditor((0, 0, 0,-0), '', readOnly = True)

		paneDescriptors = [
			dict(view = self.w.scriptsListing, identifier = "pane1", minSize = (100), canCollapse = False),
			dict(view = self.w.textBox, identifier = "pane2", minSize = (100), canCollapse = False),
		]
		self.w.splitView = SplitView((0, 30, -0, -32), paneDescriptors,
		                                     isVertical = False,
		                                     dividerStyle = 'thin',
		                                     dividerThickness = 5)

		self.w.btnRun = Button((5,-28,-5,20), title = 'Run', callback = self.scriptsListDblClickCallback)


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
		path = path.replace('%s.py' % name, '')
		print ('Running',name,path)
		sys.path.append(path)
		m = importlib.import_module(name)
		importlib.reload(m)
		if self.parent:
			m.main(self.parent)
		else:
			m.main()
		# path = '/usr/local/bin/robofont -p "%s"' % path
		# print (path)
		# os.system(path)
	def scriptsListSelectionCallback(self, sender):
		idx = sender.getSelection()
		if not idx: return
		name, scriptpath = self._prefs.get('scripts')[idx[0]]
		path = scriptpath.replace('%s.py' % name, '')
		sys.path.append(path)
		m = importlib.import_module(name)
		importlib.reload(m)
		txt = ''
		if m.__doc__:
			txt = m.__doc__
		txt += '\n---\n%s' % scriptpath
		self.w.textBox.set(txt)

	def btnAddCallback(self, sender):
		paths = getFile(allowsMultipleSelection=True)
		if paths:
			for path in paths:
				self.addScriptToList( path )

	def btnDelCallback(self, sender):
		idx = self.w.scriptsListing.getSelection()
		s = self._prefs.get('scripts')
		for id in idx:
			s.pop()
		self.loadScriptsList()


def main (parent = None):
	ScriptsBoard(parent)


if __name__ == "__main__":
	main ()