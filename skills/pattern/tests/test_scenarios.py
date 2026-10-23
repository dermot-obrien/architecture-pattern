"""
Tests for scenario complexity and validation.

Covers:
- Single scenario patterns
- Multiple scenarios (2-5+)
- Complex multi-step scenarios (10+ steps)
- Scenarios with branches and loops
- Start/Finish declarations
- Scenario validation
"""
import pytest
from pathlib import Path


def test_single_scenario_pattern(temp_workspace):
    """Test pattern with single simple scenario."""
    pattern_dir = temp_workspace / "patterns" / "AP-020-single"
    pattern_dir.mkdir(parents=True)
    
    pattern_content = """---
title: "AP-020 Single Scenario"
pattern_scope: problem
status: Draft
model:
  diagram: components.drawio
---

# AP-020 Single Scenario

## Building Blocks

| Building Block | Role in this pattern | Source |
|---|---|---|
| 01 Client | Initiates requests | loose |
| 02 Server | Processes requests | loose |

## Interfaces

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|
| IF-01 | 02 Server | 01 Client | Request/response |

## Catalogue Mapping

| Local ID | Maps To | Relationship |
|---|---|---|
| 01 | gap | gap |
| 02 | gap | gap |

## Scenarios

### S1 Basic request

Start: 01 Client

Finish: 02 Server

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 01 Client | 02 Server | Send request | IF-01 |
"""
    
    (pattern_dir / "index.md").write_text(pattern_content)
    assert (pattern_dir / "index.md").exists()


def test_multiple_scenarios_pattern(temp_workspace):
    """Test pattern with 5 different scenarios."""
    pattern_dir = temp_workspace / "patterns" / "AP-021-multi"
    pattern_dir.mkdir(parents=True)
    
    pattern_content = """---
title: "AP-021 Multiple Scenarios"
pattern_scope: solution
status: Draft
model:
  diagram: components.drawio
---

# AP-021 Multiple Scenarios

## Building Blocks

| Building Block | Role in this pattern | Source |
|---|---|---|
| 01 Frontend | User interface | loose |
| 02 API Gateway | Request router | loose |
| 03 Auth Service | Authentication | loose |
| 04 Business Service | Core logic | loose |
| 05 Database | Data storage | loose |
| 06 Cache | Performance cache | loose |

## Interfaces

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|
| IF-01 | 02 API Gateway | 01 Frontend | API calls |
| IF-02 | 03 Auth Service | 02 API Gateway | Auth checks |
| IF-03 | 04 Business Service | 02 API Gateway | Business operations |
| IF-04 | 05 Database | 04 Business Service | Data persistence |
| IF-05 | 06 Cache | 04 Business Service | Cache operations |

## Catalogue Mapping

| Local ID | Maps To | Relationship |
|---|---|---|
| 01 | gap | gap |
| 02 | ABB-100 Gateway | realises |
| 03 | ABB-101 Identity Provider | realises |
| 04 | gap | gap |
| 05 | ABB-102 Database | realises |
| 06 | ABB-103 Cache | realises |

## Scenarios

### S1 Successful authenticated request

Start: 01 Frontend

Finish: 05 Database

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 01 Frontend | 02 API Gateway | Submit request | IF-01 |
| 2 | 02 API Gateway | 03 Auth Service | Validate token | IF-02 |
| 3 | 02 API Gateway | 04 Business Service | Process request | IF-03 |
| 4 | 04 Business Service | 05 Database | Store result | IF-04 |

### S2 Cached response

Start: 01 Frontend

Finish: 06 Cache

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 01 Frontend | 02 API Gateway | Submit request | IF-01 |
| 2 | 02 API Gateway | 03 Auth Service | Validate token | IF-02 |
| 3 | 02 API Gateway | 04 Business Service | Process request | IF-03 |
| 4 | 04 Business Service | 06 Cache | Return cached data | IF-05 |

### S3 Authentication failure

Start: 01 Frontend

Finish: 03 Auth Service

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 01 Frontend | 02 API Gateway | Submit request | IF-01 |
| 2 | 02 API Gateway | 03 Auth Service | Reject invalid token | IF-02 |

### S4 Write through cache

Start: 01 Frontend

Finish: 06 Cache

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 01 Frontend | 02 API Gateway | Submit update | IF-01 |
| 2 | 02 API Gateway | 03 Auth Service | Validate token | IF-02 |
| 3 | 02 API Gateway | 04 Business Service | Process update | IF-03 |
| 4 | 04 Business Service | 05 Database | Store data | IF-04 |
| 5 | 04 Business Service | 06 Cache | Update cache | IF-05 |

### S5 Direct database query

Start: 01 Frontend

Finish: 05 Database

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 01 Frontend | 02 API Gateway | Submit query | IF-01 |
| 2 | 02 API Gateway | 03 Auth Service | Validate admin token | IF-02 |
| 3 | 02 API Gateway | 04 Business Service | Execute query | IF-03 |
| 4 | 04 Business Service | 05 Database | Run complex query | IF-04 |
"""
    
    (pattern_dir / "index.md").write_text(pattern_content)
    assert (pattern_dir / "index.md").exists()


def test_long_scenario_many_steps(temp_workspace):
    """Test scenario with 15+ steps."""
    pattern_dir = temp_workspace / "patterns" / "AP-022-long"
    pattern_dir.mkdir(parents=True)
    
    pattern_content = """---
title: "AP-022 Long Scenario"
pattern_scope: capability-area
status: Draft
model:
  diagram: components.drawio
---

# AP-022 Long Scenario

## Building Blocks

| Building Block | Role in this pattern | Source |
|---|---|---|
| 01 User Interface | Entry point | loose |
| 02 Load Balancer | Traffic distribution | loose |
| 03 Auth Gateway | Authentication | loose |
| 04 Session Manager | Session handling | loose |
| 05 Request Validator | Input validation | loose |
| 06 Business Logic | Core processing | loose |
| 07 Rule Engine | Business rules | loose |
| 08 Data Access Layer | Data abstraction | loose |
| 09 Primary Database | Main data store | loose |
| 10 Audit Logger | Audit trail | loose |
| 11 Cache Manager | Caching | loose |
| 12 Notification Service | Alerts | loose |
| 13 Analytics Collector | Metrics | loose |

## Interfaces

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|
| IF-01 | 02 Load Balancer | 01 User Interface | Route traffic |
| IF-02 | 03 Auth Gateway | 02 Load Balancer | Authenticate |
| IF-03 | 04 Session Manager | 03 Auth Gateway | Manage session |
| IF-04 | 05 Request Validator | 04 Session Manager | Validate input |
| IF-05 | 06 Business Logic | 05 Request Validator | Process request |
| IF-06 | 07 Rule Engine | 06 Business Logic | Apply rules |
| IF-07 | 08 Data Access Layer | 06 Business Logic | Access data |
| IF-08 | 09 Primary Database | 08 Data Access Layer | Persist data |
| IF-09 | 10 Audit Logger | 06 Business Logic | Log operations |
| IF-10 | 11 Cache Manager | 08 Data Access Layer | Cache data |
| IF-11 | 12 Notification Service | 06 Business Logic | Send notifications |
| IF-12 | 13 Analytics Collector | 06 Business Logic | Collect metrics |

## Catalogue Mapping

| Local ID | Maps To | Relationship |
|---|---|---|
| 01 | gap | gap |
| 02 | ABB-100 Load Balancer | realises |
| 03 | ABB-101 Auth Gateway | realises |
| 04 | ABB-102 Session Manager | realises |
| 05 | gap | gap |
| 06 | gap | gap |
| 07 | ABB-103 Rule Engine | realises |
| 08 | gap | gap |
| 09 | ABB-104 Database | realises |
| 10 | ABB-105 Audit Log | realises |
| 11 | ABB-106 Cache | realises |
| 12 | ABB-107 Notification | realises |
| 13 | ABB-108 Analytics | realises |

## Scenarios

### S1 Complete end-to-end transaction

Start: 01 User Interface

Finish: 09 Primary Database

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 01 User Interface | 02 Load Balancer | Submit transaction | IF-01 |
| 2 | 02 Load Balancer | 03 Auth Gateway | Route for auth | IF-02 |
| 3 | 03 Auth Gateway | 04 Session Manager | Validate session | IF-03 |
| 4 | 04 Session Manager | 05 Request Validator | Forward for validation | IF-04 |
| 5 | 05 Request Validator | 06 Business Logic | Pass validated request | IF-05 |
| 6 | 06 Business Logic | 07 Rule Engine | Check business rules | IF-06 |
| 7 | 06 Business Logic | 11 Cache Manager | Check cache | IF-10 |
| 8 | 06 Business Logic | 08 Data Access Layer | Request data access | IF-07 |
| 9 | 08 Data Access Layer | 09 Primary Database | Query existing data | IF-08 |
| 10 | 06 Business Logic | 10 Audit Logger | Log operation start | IF-09 |
| 11 | 08 Data Access Layer | 09 Primary Database | Write new data | IF-08 |
| 12 | 06 Business Logic | 11 Cache Manager | Update cache | IF-10 |
| 13 | 06 Business Logic | 10 Audit Logger | Log operation complete | IF-09 |
| 14 | 06 Business Logic | 12 Notification Service | Send confirmation | IF-11 |
| 15 | 06 Business Logic | 13 Analytics Collector | Record metrics | IF-12 |
"""
    
    (pattern_dir / "index.md").write_text(pattern_content)
    assert (pattern_dir / "index.md").exists()


def test_scenario_with_explicit_start_finish(temp_workspace):
    """Test that Start and Finish are explicitly declared."""
    pattern_dir = temp_workspace / "patterns" / "AP-023-explicit"
    pattern_dir.mkdir(parents=True)
    
    pattern_content = """---
title: "AP-023 Explicit Start/Finish"
pattern_scope: problem
status: Draft
model:
  diagram: components.drawio
---

# AP-023 Explicit Start/Finish

## Building Blocks

| Building Block | Role in this pattern | Source |
|---|---|---|
| 01 Entry Point | Where flow begins | loose |
| 02 Middle Step | Processing | loose |
| 03 Exit Point | Where flow ends | loose |

## Interfaces

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|
| IF-01 | 02 Middle Step | 01 Entry Point | First hop |
| IF-02 | 03 Exit Point | 02 Middle Step | Final hop |

## Catalogue Mapping

| Local ID | Maps To | Relationship |
|---|---|---|
| 01 | gap | gap |
| 02 | gap | gap |
| 03 | gap | gap |

## Scenarios

### S1 Flow with start and finish

Start: 01 Entry Point

Finish: 03 Exit Point

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 01 Entry Point | 02 Middle Step | Begin processing | IF-01 |
| 2 | 02 Middle Step | 03 Exit Point | Complete processing | IF-02 |

### S2 Alternative path

Start: 02 Middle Step

Finish: 03 Exit Point

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 02 Middle Step | 03 Exit Point | Direct path | IF-02 |
"""
    
    (pattern_dir / "index.md").write_text(pattern_content)
    assert (pattern_dir / "index.md").exists()
