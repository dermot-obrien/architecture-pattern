"""
Pytest configuration and shared fixtures for pattern skill tests.
"""
import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace with binding configuration."""
    tmpdir = tempfile.mkdtemp()
    workspace = Path(tmpdir)
    
    # Create directory structure
    (workspace / ".agents").mkdir()
    (workspace / "patterns").mkdir()
    
    # Create minimal binding file
    bindings = """bindingsVersion = "1.0"

[model]
node_id_attrs = ["component_id"]
edge_id_attr  = "iface_id"
local_pattern = '[0-9]{1,3}'

[[markdown.tables]]
section    = "Building Blocks"
entity     = "node"
id_pattern = 'COMP-[0-9]{3}|[0-9]{2}'
columns    = { id = "Building Block", label = "Building Block", group = "Source" }

[[markdown.tables]]
section    = "Interfaces"
entity     = "edge"
id_pattern = 'IF-[0-9]{2,3}|COMP-[0-9]{3}'
columns    = { id = "Interface", source = "Provider", target = "Consumer", label = "Purpose" }

[markdown.scenarios]
section = "Scenarios"

[suite.pattern]
outputDir = "../patterns"
"""
    (workspace / ".agents" / "skill-bindings.toml").write_text(bindings)
    
    yield workspace
    
    # Cleanup
    shutil.rmtree(tmpdir)


@pytest.fixture
def model_command():
    """Return path to model.py command (override with environment variable)."""
    import os
    model_path = os.environ.get("MODEL_BIN", "python -m model")
    return model_path
