
from . import ChatAi
from . import blacklist
from . import grup

def register(app):
    for mod in [ai_handler, blacklist, whitelist]:
        if hasattr(mod, "register"):
            mod.register(app)
