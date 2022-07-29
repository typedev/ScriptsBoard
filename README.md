# <img height="48" src="icon.png" width="48"/> ScriptsBoard
ScriptsBoard is an extension that adds a quick launch bar for your favorite scripts to the Inspector.

All scripts will run as imported modules, so it must follow this format:
```
    from fontParts.world import *
    
    def main():
        print ("hello world") # optional :)
        # place your code here
    
    if __name__ == "__main__":
        main()

```
_Also, in the code, you must explicitly import all the modules used._
