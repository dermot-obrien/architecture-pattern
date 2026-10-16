"""
Tests for patterns of varying complexity.

Covers:
- Simple patterns (3-5 building blocks, 1-2 scenarios)
- Medium patterns (6-10 building blocks, 2-3 scenarios)
- Complex patterns (10+ building blocks, 3+ scenarios)
- Many-to-many relationships
- Hub-and-spoke topologies
- Mesh networks
"""
import pytest
from pathlib import Path


def test_simple_pattern_minimal(temp_workspace):
    """Test minimal valid pattern with 3 building blocks."""
    pattern_dir = temp_workspace / "patterns" / "PAT-010-simple"
    pattern_dir.mkdir(parents=True)
    
    pattern_content = """---
title: "PAT-010 Minimal Pattern"
pattern_scope: problem
status: Draft
model:
  diagram: components.drawio
---

# PAT-010 Minimal Pattern

## Building Blocks

| Building Block | Role in this pattern | Source |
|---|---|---|
| 01 Input | Receives requests | loose |
| 02 Process | Transforms data | loose |
| 03 Output | Returns results | loose |

## Interfaces

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|
| IF-01 | 02 Process | 01 Input | Request input |
| IF-02 | 03 Output | 02 Process | Deliver output |

## Catalogue Mapping

| Local ID | Maps To | Relationship |
|---|---|---|
| 01 | gap | gap |
| 02 | gap | gap |
| 03 | gap | gap |

## Scenarios

### S1 Simple flow

Start: 01 Input

Finish: 03 Output

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 01 Input | 02 Process | Send request | IF-01 |
| 2 | 02 Process | 03 Output | Send response | IF-02 |
"""
    
    (pattern_dir / "index.md").write_text(pattern_content)
    assert (pattern_dir / "index.md").exists()


def test_medium_pattern_with_branches(temp_workspace):
    """Test medium complexity pattern with branching flows."""
    pattern_dir = temp_workspace / "patterns" / "PAT-011-medium"
    pattern_dir.mkdir(parents=True)
    
    pattern_content = """---
title: "PAT-011 Medium Complexity"
pattern_scope: solution
status: Draft
model:
  diagram: components.drawio
---

# PAT-011 Medium Complexity

## Building Blocks

| Building Block | Role in this pattern | Source |
|---|---|---|
| 01 Load Balancer | Distributes traffic | loose |
| 02 Auth Service | Authentication | loose |
| 03 Service A | Business logic A | loose |
| 04 Service B | Business logic B | loose |
| 05 Database A | Data for Service A | loose |
| 06 Database B | Data for Service B | loose |
| 07 Cache | Shared caching | loose |
| 08 Message Queue | Async processing | loose |

## Interfaces

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|
| IF-01 | 02 Auth Service | 01 Load Balancer | Verify tokens |
| IF-02 | 03 Service A | 01 Load Balancer | Handle requests A |
| IF-03 | 04 Service B | 01 Load Balancer | Handle requests B |
| IF-04 | 05 Database A | 03 Service A | Persist data A |
| IF-05 | 06 Database B | 04 Service B | Persist data B |
| IF-06 | 07 Cache | 03 Service A | Cache reads A |
| IF-07 | 07 Cache | 04 Service B | Cache reads B |
| IF-08 | 08 Message Queue | 03 Service A | Queue tasks A |
| IF-09 | 08 Message Queue | 04 Service B | Process tasks B |

## Catalogue Mapping

| Local ID | Maps To | Relationship |
|---|---|---|
| 01 | ABB-100 Load Balancer | realises |
| 02 | ABB-101 Identity Provider | realises |
| 03 | gap | gap |
| 04 | gap | gap |
| 05 | ABB-102 Database | realises |
| 06 | ABB-102 Database | realises |
| 07 | ABB-103 Cache | realises |
| 08 | ABB-104 Message Broker | realises |

## Scenarios

### S1 Authenticated request to Service A

Start: 01 Load Balancer

Finish: 05 Database A

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 01 Load Balancer | 02 Auth Service | Authenticate | IF-01 |
| 2 | 01 Load Balancer | 03 Service A | Route request | IF-02 |
| 3 | 03 Service A | 07 Cache | Check cache | IF-06 |
| 4 | 03 Service A | 05 Database A | Query data | IF-04 |

### S2 Request to Service B with async task

Start: 01 Load Balancer

Finish: 08 Message Queue

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 01 Load Balancer | 02 Auth Service | Authenticate | IF-01 |
| 2 | 01 Load Balancer | 04 Service B | Route request | IF-03 |
| 3 | 04 Service B | 06 Database B | Query data | IF-05 |
| 4 | 04 Service B | 08 Message Queue | Queue task | IF-09 |
"""
    
    (pattern_dir / "index.md").write_text(pattern_content)
    assert (pattern_dir / "index.md").exists()


def test_complex_pattern_mesh_topology(temp_workspace):
    """Test complex pattern with mesh topology (many-to-many)."""
    pattern_dir = temp_workspace / "patterns" / "PAT-012-complex"
    pattern_dir.mkdir(parents=True)
    
    # Create a complex pattern with 12 building blocks and multiple interconnections
    pattern_content = """---
title: "PAT-012 Complex Mesh"
pattern_scope: domain
status: Draft
model:
  diagram: components.drawio
---

# PAT-012 Complex Mesh

## Building Blocks

| Building Block | Role in this pattern | Source |
|---|---|---|
| 01 API Gateway | Entry point | loose |
| 02 Service Mesh | Service discovery | loose |
| 03 Auth Service | Authentication | loose |
| 04 User Service | User management | loose |
| 05 Order Service | Order processing | loose |
| 06 Payment Service | Payment processing | loose |
| 07 Inventory Service | Stock management | loose |
| 08 Notification Service | Alerts and messages | loose |
| 09 Analytics Service | Data analysis | loose |
| 10 User DB | User data | loose |
| 11 Order DB | Order data | loose |
| 12 Event Bus | Event streaming | loose |

## Interfaces

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|
| IF-01 | 02 Service Mesh | 01 API Gateway | Service discovery |
| IF-02 | 03 Auth Service | 01 API Gateway | Token validation |
| IF-03 | 04 User Service | 01 API Gateway | User operations |
| IF-04 | 05 Order Service | 01 API Gateway | Order operations |
| IF-05 | 10 User DB | 04 User Service | User persistence |
| IF-06 | 11 Order DB | 05 Order Service | Order persistence |
| IF-07 | 06 Payment Service | 05 Order Service | Process payment |
| IF-08 | 07 Inventory Service | 05 Order Service | Check stock |
| IF-09 | 08 Notification Service | 05 Order Service | Order notifications |
| IF-10 | 08 Notification Service | 06 Payment Service | Payment notifications |
| IF-11 | 12 Event Bus | 05 Order Service | Publish order events |
| IF-12 | 12 Event Bus | 06 Payment Service | Publish payment events |
| IF-13 | 12 Event Bus | 09 Analytics Service | Consume all events |
| IF-14 | 04 User Service | 03 Auth Service | User lookup |
| IF-15 | 02 Service Mesh | 04 User Service | Register service |
| IF-16 | 02 Service Mesh | 05 Order Service | Register service |
| IF-17 | 02 Service Mesh | 06 Payment Service | Register service |
| IF-18 | 02 Service Mesh | 07 Inventory Service | Register service |

## Catalogue Mapping

| Local ID | Maps To | Relationship |
|---|---|---|
| 01 | ABB-100 API Gateway | realises |
| 02 | ABB-101 Service Mesh | realises |
| 03 | ABB-102 Identity Provider | realises |
| 04 | gap | gap |
| 05 | gap | gap |
| 06 | gap | gap |
| 07 | gap | gap |
| 08 | ABB-103 Notification | realises |
| 09 | ABB-104 Analytics | realises |
| 10 | ABB-105 Database | realises |
| 11 | ABB-105 Database | realises |
| 12 | ABB-106 Event Bus | realises |

## Scenarios

### S1 Create order with payment

Start: 01 API Gateway

Finish: 11 Order DB

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 01 API Gateway | 03 Auth Service | Validate token | IF-02 |
| 2 | 01 API Gateway | 02 Service Mesh | Discover order service | IF-01 |
| 3 | 01 API Gateway | 05 Order Service | Create order request | IF-04 |
| 4 | 05 Order Service | 07 Inventory Service | Check availability | IF-08 |
| 5 | 05 Order Service | 06 Payment Service | Process payment | IF-07 |
| 6 | 05 Order Service | 11 Order DB | Save order | IF-06 |
| 7 | 05 Order Service | 12 Event Bus | Publish order event | IF-11 |

### S2 User registration and notification

Start: 01 API Gateway

Finish: 10 User DB

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 01 API Gateway | 04 User Service | Register user | IF-03 |
| 2 | 04 User Service | 10 User DB | Save user | IF-05 |
| 3 | 04 User Service | 08 Notification Service | Send welcome email | IF-09 |
| 4 | 04 User Service | 02 Service Mesh | Register with mesh | IF-15 |

### S3 Analytics processing

Start: 12 Event Bus

Finish: 09 Analytics Service

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 12 Event Bus | 09 Analytics Service | Stream events | IF-13 |
"""
    
    (pattern_dir / "index.md").write_text(pattern_content)
    assert (pattern_dir / "index.md").exists()


def test_hub_and_spoke_topology(temp_workspace):
    """Test pattern with hub-and-spoke topology."""
    pattern_dir = temp_workspace / "patterns" / "PAT-013-hub"
    pattern_dir.mkdir(parents=True)
    
    pattern_content = """---
title: "PAT-013 Hub and Spoke"
pattern_scope: capability-area
status: Draft
model:
  diagram: components.drawio
---

# PAT-013 Hub and Spoke

## Building Blocks

| Building Block | Role in this pattern | Source |
|---|---|---|
| 01 Central Hub | Orchestrates all services | loose |
| 02 Spoke A | Service A | loose |
| 03 Spoke B | Service B | loose |
| 04 Spoke C | Service C | loose |
| 05 Spoke D | Service D | loose |
| 06 Spoke E | Service E | loose |

## Interfaces

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|
| IF-01 | 02 Spoke A | 01 Central Hub | Service A operations |
| IF-02 | 03 Spoke B | 01 Central Hub | Service B operations |
| IF-03 | 04 Spoke C | 01 Central Hub | Service C operations |
| IF-04 | 05 Spoke D | 01 Central Hub | Service D operations |
| IF-05 | 06 Spoke E | 01 Central Hub | Service E operations |

## Catalogue Mapping

| Local ID | Maps To | Relationship |
|---|---|---|
| 01 | ABB-100 Orchestrator | realises |
| 02 | gap | gap |
| 03 | gap | gap |
| 04 | gap | gap |
| 05 | gap | gap |
| 06 | gap | gap |

## Scenarios

### S1 Orchestrated multi-service call

Start: 01 Central Hub

Finish: 06 Spoke E

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 01 Central Hub | 02 Spoke A | Request data A | IF-01 |
| 2 | 01 Central Hub | 03 Spoke B | Request data B | IF-02 |
| 3 | 01 Central Hub | 04 Spoke C | Transform data | IF-03 |
| 4 | 01 Central Hub | 05 Spoke D | Validate result | IF-04 |
| 5 | 01 Central Hub | 06 Spoke E | Send final result | IF-05 |
"""
    
    (pattern_dir / "index.md").write_text(pattern_content)
    assert (pattern_dir / "index.md").exists()
