"""tests.diff: compare a baseline and a current test report by stable test ID."""

from talo.core.manifest import ModuleKind, ModuleManifest

MANIFEST = ModuleManifest(
    id="tests.diff",
    version="0.1.0",
    kind=ModuleKind.NATIVE,
    description="Compare two test reports and list outcome transitions by test ID.",
    accepts=["path", "inline"],
)
