from .ChatAi import register
from .blacklist import register
from .grup import register

def register(app):
    for mod in [ai_handler, blacklist, whitelist]:
        if hasattr(mod, "register"):
            mod.register(app)
