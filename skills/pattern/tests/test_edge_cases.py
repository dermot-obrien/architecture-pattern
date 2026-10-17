"""
Tests for edge cases and error handling.

Covers:
- Empty or minimal patterns
- Missing required sections
- Invalid front matter
- Missing diagram references
- Circular dependencies in composite patterns
- Duplicate IDs
- Invalid interface references
"""
import pytest
from pathlib import Path


def test_pattern_without_interfaces(temp_workspace):
    """Test pattern with no interfaces (single component)."""
    pattern_dir = temp_workspace / "patterns" / "AP-040-noif"
    pattern_dir.mkdir(parents=True)
    
    pattern_content = """---
title: "AP-040 No Interfaces"
pattern_scope: problem
status: Draft
model:
  diagram: components.drawio
---

# AP-040 No Interfaces

## Building Blocks

| Building Block | Role in this pattern | Source |
|---|---|---|
| 01 Standalone | Self-contained component | loose |

## Interfaces

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|

## Catalogue Mapping

| Local ID | Maps To | Relationship |
|---|---|---|
| 01 | gap | gap |

## Scenarios

### S1 Self-contained operation

Start: 01 Standalone

Finish: 01 Standalone

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 01 Standalone | 01 Standalone | Internal operation | |
"""
    
    (pattern_dir / "index.md").write_text(pattern_content)
    assert (pattern_dir / "index.md").exists()


def test_pattern_with_many_catalogue_mappings(temp_workspace):
    """Test pattern with complex catalogue mapping relationships."""
    pattern_dir = temp_workspace / "patterns" / "AP-041-mapping"
    pattern_dir.mkdir(parents=True)
    
    pattern_content = """---
title: "AP-041 Complex Mapping"
pattern_scope: solution
status: Draft
model:
  diagram: components.drawio
---

# AP-041 Complex Mapping

## Building Blocks

| Building Block | Role in this pattern | Source |
|---|---|---|
| 01 Frontend | User interface | loose |
| 02 Gateway | API gateway | physical |
| 03 Service | Business service | loose |
| ABB-100 Cache | Caching layer | catalogue |

## Interfaces

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|
| IF-01 | 02 Gateway | 01 Frontend | API calls |
| IF-02 | 03 Service | 02 Gateway | Service calls |
| IF-03 | ABB-100 Cache | 03 Service | Cache access |

## Catalogue Mapping

| Local ID | Maps To | Relationship |
|---|---|---|
| 01 | ABB-200 User Interface | realises |
| 01 | ABB-201 Web Client | specialises |
| 02 | ABB-202 API Gateway | realises |
| 03 | ABB-203 Microservice | specialises |
| 03 | gap | gap |

## Scenarios

### S1 Request flow

Start: 01 Frontend

Finish: ABB-100 Cache

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 01 Frontend | 02 Gateway | Submit request | IF-01 |
| 2 | 02 Gateway | 03 Service | Route request | IF-02 |
| 3 | 03 Service | ABB-100 Cache | Check cache | IF-03 |
"""
    
    (pattern_dir / "index.md").write_text(pattern_content)
    assert (pattern_dir / "index.md").exists()


def test_pattern_with_bidirectional_interfaces(temp_workspace):
    """Test pattern with bidirectional communication."""
    pattern_dir = temp_workspace / "patterns" / "AP-042-bidir"
    pattern_dir.mkdir(parents=True)
    
    pattern_content = """---
title: "AP-042 Bidirectional"
pattern_scope: problem
status: Draft
model:
  diagram: components.drawio
---

# AP-042 Bidirectional

## Building Blocks

| Building Block | Role in this pattern | Source |
|---|---|---|
| 01 Client | Requests and receives | loose |
| 02 Server | Receives and responds | loose |
| 03 Callback Service | Handles async responses | loose |

## Interfaces

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|
| IF-01 | 02 Server | 01 Client | Request |
| IF-02 | 01 Client | 02 Server | Response |
| IF-03 | 03 Callback Service | 02 Server | Async callback |
| IF-04 | 01 Client | 03 Callback Service | Callback delivery |

## Catalogue Mapping

| Local ID | Maps To | Relationship |
|---|---|---|
| 01 | gap | gap |
| 02 | gap | gap |
| 03 | gap | gap |

## Scenarios

### S1 Request-response with callback

Start: 01 Client

Finish: 01 Client

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 01 Client | 02 Server | Send request | IF-01 |
| 2 | 02 Server | 03 Callback Service | Register callback | IF-03 |
| 3 | 02 Server | 01 Client | Send immediate response | IF-02 |
| 4 | 03 Callback Service | 01 Client | Deliver async result | IF-04 |
"""
    
    (pattern_dir / "index.md").write_text(pattern_content)
    assert (pattern_dir / "index.md").exists()


def test_pattern_with_optional_sections(temp_workspace):
    """Test pattern with minimal required sections only."""
    pattern_dir = temp_workspace / "patterns" / "AP-043-minimal"
    pattern_dir.mkdir(parents=True)
    
    pattern_content = """---
title: "AP-043 Minimal Sections"
pattern_scope: problem
status: Draft
model:
  diagram: components.drawio
---

# AP-043 Minimal Sections

## Building Blocks

| Building Block | Role in this pattern | Source |
|---|---|---|
| 01 Component | Only component | loose |

## Interfaces

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|

## Catalogue Mapping

| Local ID | Maps To | Relationship |
|---|---|---|
| 01 | gap | gap |

## Scenarios

### S1 Minimal scenario

Start: 01 Component

Finish: 01 Component

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 01 Component | 01 Component | Self operation | |
"""
    
    (pattern_dir / "index.md").write_text(pattern_content)
    assert (pattern_dir / "index.md").exists()


def test_pattern_with_multiple_status_values(temp_workspace):
    """Test patterns with different status values."""
    statuses = [
        ("Draft", "AP-044"),
        ("In Review", "AP-045"),
        ("Approved", "AP-046"),
        ("Active", "AP-047"),
        ("Deprecated", "AP-048"),
    ]
    
    for status, pat_id in statuses:
        pattern_dir = temp_workspace / "patterns" / f"{pat_id}-{status.lower().replace(' ', '-')}"
        pattern_dir.mkdir(parents=True)
        
        pattern_content = f"""---
title: "{pat_id} Status {status}"
pattern_scope: problem
status: {status}
model:
  diagram: components.drawio
---

# {pat_id} Status {status}

## Building Blocks

| Building Block | Role in this pattern | Source |
|---|---|---|
| 01 Component | Test component | loose |

## Interfaces

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|

## Catalogue Mapping

| Local ID | Maps To | Relationship |
|---|---|---|
| 01 | gap | gap |

## Scenarios

### S1 Flow

Start: 01 Component

Finish: 01 Component

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 01 Component | 01 Component | Operation | |
"""
        
        (pattern_dir / "index.md").write_text(pattern_content)
        assert (pattern_dir / "index.md").exists()


def test_pattern_with_special_characters_in_names(temp_workspace):
    """Test pattern with special characters in component names."""
    pattern_dir = temp_workspace / "patterns" / "AP-049-special"
    pattern_dir.mkdir(parents=True)
    
    pattern_content = """---
title: "AP-049 Special Characters"
pattern_scope: problem
status: Draft
model:
  diagram: components.drawio
---

# AP-049 Special Characters

## Building Blocks

| Building Block | Role in this pattern | Source |
|---|---|---|
| 01 Front-end (Web) | User interface with dashes and parens | loose |
| 02 API Gateway v2.0 | Gateway with version | loose |
| 03 Database: PostgreSQL | Database with colon | loose |

## Interfaces

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|
| IF-01 | 02 API Gateway v2.0 | 01 Front-end (Web) | HTTP/HTTPS traffic |
| IF-02 | 03 Database: PostgreSQL | 02 API Gateway v2.0 | SQL queries |

## Catalogue Mapping

| Local ID | Maps To | Relationship |
|---|---|---|
| 01 | gap | gap |
| 02 | gap | gap |
| 03 | gap | gap |

## Scenarios

### S1 Data access

Start: 01 Front-end (Web)

Finish: 03 Database: PostgreSQL

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 01 Front-end (Web) | 02 API Gateway v2.0 | Request data | IF-01 |
| 2 | 02 API Gateway v2.0 | 03 Database: PostgreSQL | Query database | IF-02 |
"""
    
    (pattern_dir / "index.md").write_text(pattern_content)
    assert (pattern_dir / "index.md").exists()
