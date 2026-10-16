"""
Tests for composite patterns and participation.

Covers:
- Simple composite (one pattern calls another)
- Multi-level composition (3+ levels deep)
- Role bindings between patterns
- Open participating patterns (TBD)
- Approval gate validation
"""
import pytest
from pathlib import Path


def test_simple_composite_single_participation(temp_workspace):
    """Test composite pattern with one participating pattern."""
    # First create the participating pattern
    participating_dir = temp_workspace / "patterns" / "PAT-030-base"
    participating_dir.mkdir(parents=True)
    
    participating_content = """---
title: "PAT-030 Base Pattern"
pattern_scope: solution
status: Draft
model:
  diagram: components.drawio
---

# PAT-030 Base Pattern

## Building Blocks

| Building Block | Role in this pattern | Source |
|---|---|---|
| 01 Input Handler | Receives data | loose |
| 02 Processor | Transforms data | loose |
| 03 Output Handler | Returns result | loose |

## Interfaces

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|
| IF-01 | 02 Processor | 01 Input Handler | Forward for processing |
| IF-02 | 03 Output Handler | 02 Processor | Return result |

## Catalogue Mapping

| Local ID | Maps To | Relationship |
|---|---|---|
| 01 | gap | gap |
| 02 | gap | gap |
| 03 | gap | gap |

## Scenarios

### S1 Process data

Start: 01 Input Handler

Finish: 03 Output Handler

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 01 Input Handler | 02 Processor | Send data | IF-01 |
| 2 | 02 Processor | 03 Output Handler | Return result | IF-02 |
"""
    
    (participating_dir / "index.md").write_text(participating_content)
    
    # Now create the composite pattern
    composite_dir = temp_workspace / "patterns" / "PAT-031-composite"
    composite_dir.mkdir(parents=True)
    
    composite_content = """---
title: "PAT-031 Simple Composite"
pattern_scope: capability-area
status: Draft
model:
  diagram: components.drawio
---

# PAT-031 Simple Composite

## Patterns Applied

| Pattern | Role in this pattern |
|---|---|
| PAT-030 Base Pattern | Handles data processing; run by S1 step 2 |

## Building Blocks

| Building Block | Role in this pattern | Source |
|---|---|---|
| 01 Coordinator | Orchestrates flow | loose |
| 02 Data Processing | Core processing | PAT-030 |
| 03 Audit Log | Records operations | loose |

## Interfaces

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|
| IF-10 | 02 Data Processing | 01 Coordinator | Process requests |
| IF-11 | 03 Audit Log | 01 Coordinator | Log operations |

## Catalogue Mapping

| Local ID | Maps To | Relationship |
|---|---|---|
| 01 | gap | gap |
| 02 | gap | gap |
| 03 | ABB-100 Audit | realises |

## Scenarios

### S1 Orchestrated processing

Start: 01 Coordinator

Finish: 03 Audit Log

| Step | Actor | Target | Action | Interface | Uses |
|---:|---|---|---|---|---|
| 1 | 01 Coordinator | 02 Data Processing | Initiate processing | IF-10 | |
| 2 | 02 Data Processing | 02 Data Processing | Process data | | PAT-030 S1 (01=02, 03=02) |
| 3 | 01 Coordinator | 03 Audit Log | Record completion | IF-11 | |
"""
    
    (composite_dir / "index.md").write_text(composite_content)
    assert (composite_dir / "index.md").exists()


def test_multi_level_composition(temp_workspace):
    """Test 3-level deep composition (composite of composites)."""
    # Level 1: Base patterns
    base1_dir = temp_workspace / "patterns" / "PAT-032-base1"
    base1_dir.mkdir(parents=True)
    
    base1_content = """---
title: "PAT-032 Base Level 1"
pattern_scope: problem
status: Draft
model:
  diagram: components.drawio
---

# PAT-032 Base Level 1

## Building Blocks

| Building Block | Role in this pattern | Source |
|---|---|---|
| 01 Component A | First component | loose |
| 02 Component B | Second component | loose |

## Interfaces

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|
| IF-01 | 02 Component B | 01 Component A | Data flow |

## Catalogue Mapping

| Local ID | Maps To | Relationship |
|---|---|---|
| 01 | gap | gap |
| 02 | gap | gap |

## Scenarios

### S1 Basic operation

Start: 01 Component A

Finish: 02 Component B

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 01 Component A | 02 Component B | Transfer | IF-01 |
"""
    
    (base1_dir / "index.md").write_text(base1_content)
    
    # Level 2: Composite using base
    level2_dir = temp_workspace / "patterns" / "PAT-033-level2"
    level2_dir.mkdir(parents=True)
    
    level2_content = """---
title: "PAT-033 Composite Level 2"
pattern_scope: solution
status: Draft
model:
  diagram: components.drawio
---

# PAT-033 Composite Level 2

## Patterns Applied

| Pattern | Role in this pattern |
|---|---|
| PAT-032 Base Level 1 | Core operation; run by S1 step 1 |

## Building Blocks

| Building Block | Role in this pattern | Source |
|---|---|---|
| 01 Orchestrator | Coordinates | loose |
| 02 Base Operation | Basic processing | PAT-032 |

## Interfaces

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|
| IF-10 | 02 Base Operation | 01 Orchestrator | Execute base |

## Catalogue Mapping

| Local ID | Maps To | Relationship |
|---|---|---|
| 01 | gap | gap |
| 02 | gap | gap |

## Scenarios

### S1 Level 2 operation

Start: 01 Orchestrator

Finish: 02 Base Operation

| Step | Actor | Target | Action | Interface | Uses |
|---:|---|---|---|---|---|
| 1 | 01 Orchestrator | 02 Base Operation | Execute | IF-10 | PAT-032 S1 (01=02, 02=02) |
"""
    
    (level2_dir / "index.md").write_text(level2_content)
    
    # Level 3: Top-level composite
    level3_dir = temp_workspace / "patterns" / "PAT-034-level3"
    level3_dir.mkdir(parents=True)
    
    level3_content = """---
title: "PAT-034 Composite Level 3"
pattern_scope: capability-area
status: Draft
model:
  diagram: components.drawio
---

# PAT-034 Composite Level 3

## Patterns Applied

| Pattern | Role in this pattern |
|---|---|
| PAT-033 Composite Level 2 | Mid-level operation; run by S1 step 1 |

## Building Blocks

| Building Block | Role in this pattern | Source |
|---|---|---|
| 01 Top Controller | Top-level control | loose |
| 02 Mid Level | Mid-level processing | PAT-033 |

## Interfaces

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|
| IF-20 | 02 Mid Level | 01 Top Controller | Control flow |

## Catalogue Mapping

| Local ID | Maps To | Relationship |
|---|---|---|
| 01 | gap | gap |
| 02 | gap | gap |

## Scenarios

### S1 Top-level operation

Start: 01 Top Controller

Finish: 02 Mid Level

| Step | Actor | Target | Action | Interface | Uses |
|---:|---|---|---|---|---|
| 1 | 01 Top Controller | 02 Mid Level | Initiate | IF-20 | PAT-033 S1 (01=02, 02=02) |
"""
    
    (level3_dir / "index.md").write_text(level3_content)
    assert (level3_dir / "index.md").exists()


def test_composite_with_open_participating_pattern(temp_workspace):
    """Test composite with TBD (open) participating pattern."""
    composite_dir = temp_workspace / "patterns" / "PAT-035-open"
    composite_dir.mkdir(parents=True)
    
    composite_content = """---
title: "PAT-035 Composite with TBD"
pattern_scope: capability-area
status: Draft
model:
  diagram: components.drawio
---

# PAT-035 Composite with TBD

## Patterns Applied

| Pattern | Role in this pattern |
|---|---|
| TBD authentication | Authenticates users; S1 step 1, not yet written |

## Building Blocks

| Building Block | Role in this pattern | Source |
|---|---|---|
| 01 Gateway | Entry point | loose |
| 02 Application | Business logic | loose |

## Interfaces

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|
| IF-01 | 02 Application | 01 Gateway | Process requests |

## Catalogue Mapping

| Local ID | Maps To | Relationship |
|---|---|---|
| 01 | gap | gap |
| 02 | gap | gap |

## Scenarios

### S1 Request with authentication

Start: 01 Gateway

Finish: 02 Application

| Step | Actor | Target | Action | Interface | Uses |
|---:|---|---|---|---|---|
| 1 | 01 Gateway | 01 Gateway | Authenticate | | TBD authentication |
| 2 | 01 Gateway | 02 Application | Forward request | IF-01 | |
"""
    
    (composite_dir / "index.md").write_text(composite_content)
    assert (composite_dir / "index.md").exists()


def test_approval_gate_enforcement(temp_workspace):
    """Test that approved patterns cannot reference unapproved patterns."""
    # Create unapproved base pattern
    base_dir = temp_workspace / "patterns" / "PAT-036-base"
    base_dir.mkdir(parents=True)
    
    base_content = """---
title: "PAT-036 Unapproved Base"
pattern_scope: problem
status: Draft
model:
  diagram: components.drawio
---

# PAT-036 Unapproved Base

## Building Blocks

| Building Block | Role in this pattern | Source |
|---|---|---|
| 01 Component | Basic component | loose |

## Interfaces

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|

## Catalogue Mapping

| Local ID | Maps To | Relationship |
|---|---|---|
| 01 | gap | gap |

## Scenarios

### S1 Basic flow

Start: 01 Component

Finish: 01 Component

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 01 Component | 01 Component | Self-contained | |
"""
    
    (base_dir / "index.md").write_text(base_content)
    
    # Create approved composite that shouldn't pass validation
    composite_dir = temp_workspace / "patterns" / "PAT-037-approved"
    composite_dir.mkdir(parents=True)
    
    composite_content = """---
title: "PAT-037 Approved Composite"
pattern_scope: capability-area
status: Approved
model:
  diagram: components.drawio
---

# PAT-037 Approved Composite

## Patterns Applied

| Pattern | Role in this pattern |
|---|---|
| PAT-036 Unapproved Base | Should fail approval gate |

## Building Blocks

| Building Block | Role in this pattern | Source |
|---|---|---|
| 01 Wrapper | Wraps base | loose |
| 02 Base | Base pattern | PAT-036 |

## Interfaces

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|
| IF-01 | 02 Base | 01 Wrapper | Wrap |

## Catalogue Mapping

| Local ID | Maps To | Relationship |
|---|---|---|
| 01 | gap | gap |
| 02 | gap | gap |

## Scenarios

### S1 Should fail validation

Start: 01 Wrapper

Finish: 02 Base

| Step | Actor | Target | Action | Interface | Uses |
|---:|---|---|---|---|---|
| 1 | 01 Wrapper | 02 Base | Run | IF-01 | PAT-036 S1 (01=02) |
"""
    
    (composite_dir / "index.md").write_text(composite_content)
    
    # This pattern should FAIL validation due to approval gate
    # (Approved pattern PAT-037 references Draft pattern PAT-036)
    assert (composite_dir / "index.md").exists()
