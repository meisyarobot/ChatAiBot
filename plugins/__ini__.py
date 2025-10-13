# Mengimpor semua modul plugins otomatis
from . import ai_handler
from . import blacklist
from . import whitelist

def register(app):
    for mod in [ai_handler, blacklist, whitelist]:
        if hasattr(mod, "register"):
            mod.register(app)
