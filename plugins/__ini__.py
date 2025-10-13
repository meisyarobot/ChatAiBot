from . import ChatAi
from . import blacklist
from . import grup

def register(app):
    modules = [ChatAi, blacklist, grup]
    for mod in modules:
        if hasattr(mod, "register") and callable(mod.register):
            mod.register(app)
