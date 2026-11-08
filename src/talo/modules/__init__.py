"""Built-in modules shipped with Talo."""

from talo.core.manifest import ModuleManifest
from talo.modules.tests_diff import MANIFEST as TESTS_DIFF

BUILTIN_MANIFESTS: dict[str, ModuleManifest] = {m.id: m for m in (TESTS_DIFF,)}
