# <img height="48" src="icon.png" width="48"/> ScriptsBoard
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
_Also, in the code, you must explicitly import all the modules used._
