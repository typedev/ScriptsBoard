"""
ScriptsBoard is an extension for quickly launching your favorite scripts.
In order for scripts to run, they must follow this format:
```
__doc__ = 'description' # optional

def main():
	print ("place your code here")

if __name__ == "__main__":
	main()

```

"""

import os, sys, importlib
from vanilla import *
from vanilla.dialogs import getFile

from mojo.subscriber import Subscriber, registerRoboFontSubscriber
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
			return list(self.data[key])
		except:
			return None

	def set (self, key, value):
		self.data[key] = tuple(value)
		self.save()



class ScriptsBoardEmbedded(Subscriber):
	debug = True

	def build (self):
		_version = '0.7'
		_baseDefaultKey = "com.typedev.ScriptBoard.v%s." % _version
		_dataDefaultKey = "%s.data" % _baseDefaultKey

		settings = dict(
			_baseDefaultKey = _baseDefaultKey,
			_dataDefaultKey = _dataDefaultKey
		)

		self._prefs = ScriptBoardSettings(settings)
		self._prefs.load()
		self.w = Group((0,0,-0,-0))
		self.w.flex = Group('auto')
		self.w.btnAdd = Button('auto',
		                       title = '+',
		                       callback = self.btnAddCallback,
		                       sizeStyle = 'regular'
		                       )
		self.w.btnDel = Button('auto',
		                       title = '-',
		                       callback = self.btnDelCallback,
		                       sizeStyle = 'regular'
		                       )
		self.w.scriptsListing = List('auto',
		                             items = [],
		                             allowsMultipleSelection = False,
		                             selectionCallback = self.scriptsListSelectionCallback,
		                             doubleClickCallback = self.scriptsListDblClickCallback
		                             )

		self.w.textBox = TextEditor('auto', '', readOnly = True)
		self.w.btnRun = Button('auto', title = 'Run', callback = self.scriptsListDblClickCallback)


		rules = [
			# Horizontal
			"H:|-border-[flex]-border-[btnAdd]-border-[btnDel(==btnAdd)]-border-|",
			"H:|-0-[scriptsListing]-0-|",
			"H:|-0-[textBox]-0-|",
			"H:|-border-[btnRun]-border-|",
			# Vertical
			"V:|-border-[flex]-border-[scriptsListing]-space-[textBox(==scriptsListing)]-border-[btnRun]-border-|",
			"V:|-border-[btnAdd]-border-[scriptsListing]-space-[textBox(==scriptsListing)]-border-[btnRun]-border-|",
			"V:|-border-[btnDel]-border-[scriptsListing]-space-[textBox(==scriptsListing)]-border-[btnRun]-border-|",
		]
		metrics = {
			"border": 5,
			"space": 2
		}
		self.w.addAutoPosSizeRules(rules, metrics)

	def started(self):
		self.loadScriptsList()


	def roboFontWantsInspectorViews (self, info):
		registerRoboFontSubscriber(ScriptsBoardEmbedded)
		item = dict(label = "Scripts Board", view = self.w, minSize=200, size=300, collapsed=True, canResize=True)
		info["viewDescriptions"].insert(0, item)
		self.loadScriptsList()


	def loadScriptsList(self):
		self.w.scriptsListing.set([])
		slist = self._prefs.get('scripts')
		# reset = False
		# if reset:
		# 	self._prefs.set('scripts',[])
		toDelete = []
		toSet = []
		for scriptdata in slist:
			name, path = scriptdata
			if os.path.exists(path):
				toSet.append(name)
			else:
				toDelete.append((name, path))
		self.w.scriptsListing.set(toSet)
		if toDelete:
			for idname in toDelete:
				print('ScriptsBoard:',idname,' not found..')
				self.deleteScriptFromPrefs(idname = idname)


	def addScriptToList(self, path):
		namefile = os.path.basename(path)
		name, ext = namefile.split('.')
		slist = self._prefs.get('scripts')
		if ext == 'py' and (name, path) not in slist:
			slist.append((name, path))
			self._prefs.set('scripts', slist)
			self.loadScriptsList()
		# elif ext == 'roboFontExt':
		# 	pass
		# 	# print 'extension', name
		# 	# plist = readPlist('%s/info.plist' % path)
		# 	# name_ext = plist['name']
		# 	# for items in plist['addToMenu']:
		# 	# 	# for key, value in items.items():
		# 	# 	py_path = '%s/lib/%s' % (path, items['path'])
		# 	# 	name_script = items['preferredName']
		# 	# 	# print name_ext, name_script, py_path
		# 	# 	s.append(('%s.%s' % (name_ext, name_script),py_path))
		# 	# self.loadScriptsList()
		else:
			print ('Wrong file format!..')


	def scriptsListDblClickCallback(self, sender):
		idx = self.w.scriptsListing.getSelection()
		name, path = self._prefs.get('scripts')[idx[0]]
		path = path.replace('%s.py' % name, '')
		print ('Running',name,path)
		if path not in sys.path:
			sys.path.append(path)
		m = importlib.import_module(name)
		importlib.reload(m)
		if hasattr(m, 'main'):
			m.main()
		else:
			print (__doc__)
		# path = '/usr/local/bin/robofont -p "%s"' % path
		# os.system(path)


	def scriptsListSelectionCallback(self, sender):
		idx = sender.getSelection()
		if not idx: return
		name, scriptpath = self._prefs.get('scripts')[idx[0]]
		path = scriptpath.replace('%s.py' % name, '')
		if path not in sys.path:
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


	def deleteScriptFromPrefs(self, idname):
		slist = self._prefs.get('scripts')
		for idx, scriptdata in enumerate(slist):
			_name, path = scriptdata
			if (_name, path) == idname:
				del slist[idx]
				self._prefs.set('scripts', slist)
				break
		self.loadScriptsList()


	def btnDelCallback(self, sender):
		idx = self.w.scriptsListing.getSelection()
		name, path = self._prefs.get('scripts')[idx[0]]
		self.deleteScriptFromPrefs(idname = (name, path))


def main ():
	registerRoboFontSubscriber(ScriptsBoardEmbedded)


if __name__ == "__main__":
	main ()