"""
ScriptsBoard is an extension for quickly launching your favorite scripts.
The script is run as an imported module, so it must follow this format:
```
from fontParts.world import *

def main():
	print ("hello world") # optional :)
	# place your code here

if __name__ == "__main__":
	main()

```
* Also, in the code, you must explicitly import all the modules used.

"""

import os, sys, importlib
from vanilla import *
from vanilla.dialogs import getFile

from mojo.subscriber import Subscriber, registerRoboFontSubscriber
from mojo.extensions import getExtensionDefault, setExtensionDefault
from mojo.UI import OpenScriptWindow, OutputWindow, HelpWindow, Message

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
		self.w.flex1 = Group('auto')
		self.w.flex2 = Group('auto')
		self.w.btnEdit = Button('auto',
		                       title = '􀤏',
		                       callback = self.btnEditCallback,
		                       sizeStyle = 'regular'
		                       )
		self.w.btnOutput = Button('auto',
		                        title = '􀓕',
		                        callback = self.btnOutputWindowCallback,
		                        sizeStyle = 'regular'
		                        )
		self.w.btnAdd = Button('auto',
		                       title = '􀣗',
		                       callback = self.btnAddCallback,
		                       sizeStyle = 'regular'
		                       )
		self.w.btnDel = Button('auto',
		                       title = '􀈑',
		                       callback = self.btnDelCallback,
		                       sizeStyle = 'regular'
		                       )
		self.w.btnHelp = Button('auto',
		                          title = '􀁜',
		                          callback = self.btnHelpCallback,
		                          sizeStyle = 'regular'
		                          )
		self.w.scriptsList = List('auto',
		                          items = [],
		                          allowsMultipleSelection = False,
		                          selectionCallback = self.scriptsListSelectionCallback,
		                          doubleClickCallback = self.scriptsListDblClickCallback
		                          )

		self.w.textBox = EditText('auto', 'ScriptsBoard version: %s' % _version) # readOnly = True
		self.w.btnRun = Button('auto', title = '􀊄', callback = self.scriptsListDblClickCallback)


		rules = [
			# Horizontal
			"H:|-border-[btnEdit]-border-[btnOutput]-border-[flex1]-border-[btnAdd]-border-[btnDel]-border-[flex2(==flex1)]-border-[btnHelp]-border-|",
			"H:|-0-[scriptsList]-0-|",
			"H:|-0-[textBox(==scriptsList)]-0-|",
			"H:|-border-[btnRun]-border-|",
			# Vertical
			"V:|-border-[btnEdit]-border-[scriptsList]-space-[textBox(==60)]-border-[btnRun]-border-|",
			"V:|-border-[btnOutput]-border-[scriptsList]-space-[textBox(==60)]-border-[btnRun]-border-|",
			"V:|-border-[flex1]-border-[scriptsList]-space-[textBox(==60)]-border-[btnRun]-border-|",
			"V:|-border-[btnAdd]-border-[scriptsList]-space-[textBox(==60)]-border-[btnRun]-border-|",
			"V:|-border-[btnDel]-border-[scriptsList]-space-[textBox(==60)]-border-[btnRun]-border-|",
			"V:|-border-[flex2]-border-[scriptsList]-space-[textBox(==60)]-border-[btnRun]-border-|",
			"V:|-border-[btnHelp]-border-[scriptsList]-space-[textBox(==60)]-border-[btnRun]-border-|",

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


	def btnEditCallback(self, sender):
		idx = self.w.scriptsList.getSelection()
		if not idx: return
		_name, scriptpath = self._prefs.get('scripts')[idx[0]]
		OpenScriptWindow(scriptpath)


	def btnOutputWindowCallback(self, sender):
		OutputWindow().show()


	def btnHelpCallback(self, sender):
		HelpWindow("https://github.com/typedev/ScriptsBoard#readme")


	def loadScriptsList(self):
		self.w.scriptsList.set([])
		scriptslist = self._prefs.get('scripts')
		toDelete = []
		toSet = []
		for scriptdata in scriptslist:
			name, path = scriptdata
			if os.path.exists(path):
				toSet.append(name)
			else:
				toDelete.append((name, path))
		self.w.scriptsList.set(toSet)
		if toDelete:
			for (name, path) in toDelete:
				Message(title = 'ScriptsBoard', message = 'ScriptsBoard: %s not found..\ncheck file exists: %s' % (name,path))
				self.deleteScriptFromPrefs(idname = (name, path))


	def addScriptToList(self, path):
		namefile = os.path.basename(path)
		name, ext = namefile.split('.')
		scriptslist = self._prefs.get('scripts')
		nameslist = []
		for scriptdata in scriptslist:
			_name, _path = scriptdata
			nameslist.append(_name)
		if ext == 'py':
			if name in nameslist:
				i = 2
				while name + " (%s)" % i in nameslist:
					i += 1
				name = name + " (%s)" % i
			scriptslist.append((name, path))
			self._prefs.set('scripts', scriptslist)
			self.loadScriptsList()
		else:
			print ('ScriptsBoard cannot add this file\n%s' % path)


	def scriptsListDblClickCallback(self, sender):
		idx = self.w.scriptsList.getSelection()
		if not idx: return
		_name, scriptpath = self._prefs.get('scripts')[idx[0]]
		namefile = os.path.basename(scriptpath)
		name, ext = namefile.split('.')
		path = scriptpath.replace('%s.py' % name, '')
		if path not in sys.path:
			sys.path.append(path)
		print('ScriptsBoard launching: %s\n%s' % (name, scriptpath))
		m = importlib.import_module(name)
		importlib.reload(m)
		if hasattr(m, 'main'):
			m.main()
		else:
			print (__doc__)
			OutputWindow().show()
			#TODO It looks like this method doesn't work.
			# print('Running shell: %s\n%s' % (name, scriptpath))
			# _path = '/usr/local/bin/robofont -p "%s"' % scriptpath
			# os.system(_path)


	def scriptsListSelectionCallback(self, sender):
		idx = sender.getSelection()
		if not idx: return
		_name, scriptpath = self._prefs.get('scripts')[idx[0]]
		# namefile = os.path.basename(scriptpath)
		# name, ext = namefile.split('.')
		# path = scriptpath.replace('%s.py' % name, '')
		# if path not in sys.path:
		# 	sys.path.append(path)
		# m = importlib.import_module(name)
		# importlib.reload(m)
		# if m.__doc__:
		# 	self.w.textBox.set(m.__doc__)
		self.w.textBox.set(scriptpath)


	def btnAddCallback(self, sender):
		paths = getFile(allowsMultipleSelection=True, fileTypes = ['py'])
		if paths:
			for path in paths:
				self.addScriptToList( path )


	def deleteScriptFromPrefs(self, idname):
		scriptslist = self._prefs.get('scripts')
		for idx, scriptdata in enumerate(scriptslist):
			name, path = scriptdata
			if (name, path) == idname:
				del scriptslist[idx]
				self._prefs.set('scripts', scriptslist)
				break


	def btnDelCallback(self, sender):
		idx = self.w.scriptsList.getSelection()
		if not idx: return
		name, path = self._prefs.get('scripts')[idx[0]]
		self.deleteScriptFromPrefs(idname = (name, path))
		self.loadScriptsList()
		self.w.textBox.set('')


def main ():
	registerRoboFontSubscriber(ScriptsBoardEmbedded)


if __name__ == "__main__":
	main ()