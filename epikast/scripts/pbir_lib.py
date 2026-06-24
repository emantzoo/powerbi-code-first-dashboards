"""
epikast/scripts/pbir_lib.py — thin shim.

All visual helpers now live in workflow/pbir_lib.py.
This shim loads that module and injects its public names into this module's
namespace so that callers can do both:

    import pbir_lib as pb
    pb.BASE = ...                    # sets the variable on THIS module
    pb.write_page(...)               # write_page reads shim.BASE via wrapper

    from pbir_lib import uid, ...    # still works

write_page / write_pages_json / write_background are wrapped here so that
setting pb.BASE on the shim is automatically forwarded to the workflow module
before each call.
"""

import importlib.util
import os

# ── Load workflow/pbir_lib.py by absolute path ────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_WORKFLOW_LIB = os.path.normpath(
    os.path.join(_HERE, "..", "..", "workflow", "pbir_lib.py")
)

_spec = importlib.util.spec_from_file_location("_workflow_pbir_lib", _WORKFLOW_LIB)
_wf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_wf)

# ── Inject all public names from the workflow module into this namespace ───────
for _name, _obj in vars(_wf).items():
    if not _name.startswith("__"):
        globals()[_name] = _obj

# ── Module-level BASE (callers set this: `pb.BASE = pb.resolve_pages_base(...)`) ─
BASE = None


# ── write_page / write_pages_json / write_background: bridge shim.BASE ────────
def write_page(page_id, display_name, visuals):
    """Write one report page. Reads BASE from this shim module."""
    _wf.BASE = BASE
    _wf.write_page(page_id, display_name, visuals)


def write_pages_json(page_order):
    """Write pages.json. Reads BASE from this shim module."""
    _wf.BASE = BASE
    _wf.write_pages_json(page_order)


def write_background(page_id, png_path):
    """Embed background PNG. Reads BASE from this shim module."""
    _wf.BASE = BASE
    _wf.write_background(page_id, png_path)
