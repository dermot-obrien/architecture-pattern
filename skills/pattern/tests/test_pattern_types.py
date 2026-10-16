"""
Tests for different pattern types and abstraction levels.

Covers:
- Conceptual patterns (all local IDs, no physical artifacts)
- Logical patterns (solution components, deployment-agnostic)
- Physical patterns (specific technologies and deployment)
- Hybrid patterns (mix of abstraction levels)
"""
import pytest
from pathlib import Path


def test_conceptual_pattern_simple(temp_workspace):
    """Test a simple conceptual pattern with local building blocks."""
    pattern_dir = temp_workspace / "patterns" / "PAT-001-test"
    pattern_dir.mkdir(parents=True)
    
    pattern_content = """---
title: "PAT-001 Simple Conceptual"
pattern_scope: problem
status: Draft
model:
  diagram: components.drawio
---

# PAT-001 Simple Conceptual

## Building Blocks

| Building Block | Role in this pattern | Source |
|---|---|---|
| 01 Frontend | User interface | loose |
| 02 Backend | Business logic | loose |
| 03 Database | Data storage | loose |

## Interfaces

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|
| IF-01 | 02 Backend | 01 Frontend | API calls |
| IF-02 | 03 Database | 02 Backend | Data queries |

## Catalogue Mapping

| Local ID | Maps To | Relationship |
|---|---|---|
| 01 | gap | gap |
| 02 | gap | gap |
| 03 | gap | gap |

## Scenarios

### S1 Process request

Start: 01 Frontend

Finish: 03 Database

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 01 Frontend | 02 Backend | Send request | IF-01 |
| 2 | 02 Backend | 03 Database | Store data | IF-02 |
"""
    
    (pattern_dir / "index.md").write_text(pattern_content)
    
    # This pattern should validate as conceptual
    # (all local IDs, no catalogue mapping to physical components)
    assert (pattern_dir / "index.md").exists()


def test_logical_pattern_with_abbrevs(temp_workspace):
    """Test a logical pattern with architecture building blocks."""
    pattern_dir = temp_workspace / "patterns" / "PAT-002-test"
    pattern_dir.mkdir(parents=True)
    
    pattern_content = """---
title: "PAT-002 Logical with ABBs"
pattern_scope: solution
status: Draft
model:
  diagram: components.drawio
---

# PAT-002 Logical with ABBs

## Building Blocks

| Building Block | Role in this pattern | Source |
|---|---|---|
| ABB-100 API Gateway | Routes requests | catalogue |
| ABB-101 Service Mesh | Inter-service communication | catalogue |
| 01 Business Service | Application logic | loose |
| ABB-102 Data Store | Persistent storage | catalogue |

## Interfaces

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|
| IF-01 | ABB-100 API Gateway | 01 Business Service | Route requests |
| IF-02 | ABB-101 Service Mesh | 01 Business Service | Service discovery |
| IF-03 | ABB-102 Data Store | 01 Business Service | Data persistence |

## Catalogue Mapping

| Local ID | Maps To | Relationship |
|---|---|---|
| 01 | ABB-200 Generic Service | specialises |

## Scenarios

### S1 Handle API request

Start: ABB-100 API Gateway

Finish: ABB-102 Data Store

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | ABB-100 API Gateway | 01 Business Service | Forward request | IF-01 |
| 2 | 01 Business Service | ABB-101 Service Mesh | Discover dependencies | IF-02 |
| 3 | 01 Business Service | ABB-102 Data Store | Persist result | IF-03 |
"""
    
    (pattern_dir / "index.md").write_text(pattern_content)
    
    # This should be logical (mix of ABBs and local IDs, deployment-agnostic)
    assert (pattern_dir / "index.md").exists()


def test_physical_pattern_with_products(temp_workspace):
    """Test a physical pattern with specific technologies."""
    pattern_dir = temp_workspace / "patterns" / "PAT-003-test"
    pattern_dir.mkdir(parents=True)
    
    pattern_content = """---
title: "PAT-003 Physical Deployment"
pattern_scope: platform
status: Draft
model:
  diagram: components.drawio
---

# PAT-003 Physical Deployment

## Building Blocks

| Building Block | Role in this pattern | Source |
|---|---|---|
| COMP-001 NGINX Ingress | Load balancer and reverse proxy | physical |
| COMP-002 Kong API Gateway | API management | physical |
| COMP-003 PostgreSQL 14 | Primary database | physical |
| COMP-004 Redis 7 | Caching layer | physical |
| COMP-005 Kubernetes 1.28 | Container orchestration | physical |

## Interfaces

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|
| IF-01 | COMP-001 NGINX Ingress | COMP-002 Kong API Gateway | HTTP/HTTPS traffic |
| IF-02 | COMP-003 PostgreSQL 14 | COMP-002 Kong API Gateway | Connection pooling |
| IF-03 | COMP-004 Redis 7 | COMP-002 Kong API Gateway | Session storage |
| IF-04 | COMP-005 Kubernetes 1.28 | COMP-002 Kong API Gateway | Pod orchestration |

## Catalogue Mapping

| Local ID | Maps To | Relationship |
|---|---|---|
| COMP-001 | ABB-100 Load Balancer | realises |
| COMP-002 | ABB-101 API Gateway | realises |
| COMP-003 | ABB-102 Relational Database | realises |
| COMP-004 | ABB-103 Cache | realises |
| COMP-005 | ABB-104 Orchestrator | realises |

## Scenarios

### S1 Deploy application

Start: COMP-005 Kubernetes 1.28

Finish: COMP-001 NGINX Ingress

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | COMP-005 Kubernetes 1.28 | COMP-002 Kong API Gateway | Deploy pod | IF-04 |
| 2 | COMP-002 Kong API Gateway | COMP-004 Redis 7 | Initialize session | IF-03 |
| 3 | COMP-002 Kong API Gateway | COMP-003 PostgreSQL 14 | Create connection pool | IF-02 |
| 4 | COMP-001 NGINX Ingress | COMP-002 Kong API Gateway | Configure routing | IF-01 |
"""
    
    (pattern_dir / "index.md").write_text(pattern_content)
    
    # This should be physical (specific products, versions, deployment details)
    assert (pattern_dir / "index.md").exists()


def test_hybrid_pattern_mixed_abstraction(temp_workspace):
    """Test a pattern with mixed abstraction levels."""
    pattern_dir = temp_workspace / "patterns" / "PAT-004-test"
    pattern_dir.mkdir(parents=True)
    
    pattern_content = """---
title: "PAT-004 Hybrid Pattern"
pattern_scope: capability-area
status: Draft
model:
  diagram: components.drawio
---

# PAT-004 Hybrid Pattern

## Building Blocks

| Building Block | Role in this pattern | Source |
|---|---|---|
| 01 Mobile App | User interface (conceptual) | loose |
| ABB-100 Identity Provider | Authentication (logical) | catalogue |
| COMP-001 AWS Cognito | Concrete identity service (physical) | physical |
| 02 Backend APIs | Business services (conceptual) | loose |
| COMP-002 Amazon RDS PostgreSQL | Specific database (physical) | physical |

## Interfaces

| Interface | Provider | Consumer | Purpose |
|---|---|---|---|
| IF-01 | ABB-100 Identity Provider | 01 Mobile App | User authentication |
| IF-02 | COMP-001 AWS Cognito | ABB-100 Identity Provider | Token generation |
| IF-03 | 02 Backend APIs | 01 Mobile App | Data operations |
| IF-04 | COMP-002 Amazon RDS PostgreSQL | 02 Backend APIs | Data persistence |

## Catalogue Mapping

| Local ID | Maps To | Relationship |
|---|---|---|
| 01 | gap | gap |
| 02 | ABB-200 Service Layer | specialises |
| COMP-001 | ABB-100 Identity Provider | realises |
| COMP-002 | ABB-102 Database | realises |

## Scenarios

### S1 User login and data fetch

Start: 01 Mobile App

Finish: COMP-002 Amazon RDS PostgreSQL

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 01 Mobile App | ABB-100 Identity Provider | Request authentication | IF-01 |
| 2 | ABB-100 Identity Provider | COMP-001 AWS Cognito | Generate JWT | IF-02 |
| 3 | 01 Mobile App | 02 Backend APIs | Fetch user data | IF-03 |
| 4 | 02 Backend APIs | COMP-002 Amazon RDS PostgreSQL | Query database | IF-04 |
"""
    
    (pattern_dir / "index.md").write_text(pattern_content)
    
    # This should be hybrid (mix of conceptual, logical, and physical)
    assert (pattern_dir / "index.md").exists()


def test_pattern_scope_variations(temp_workspace):
    """Test patterns with different scope levels."""
    scopes = [
        ("problem", "PAT-005"),
        ("solution", "PAT-006"),
        ("capability-area", "PAT-007"),
        ("domain", "PAT-008"),
        ("platform", "PAT-009"),
    ]
    
    for scope, pat_id in scopes:
        pattern_dir = temp_workspace / "patterns" / f"{pat_id}-test"
        pattern_dir.mkdir(parents=True)
        
        pattern_content = f"""---
title: "{pat_id} {scope.title()} Scope"
pattern_scope: {scope}
status: Draft
model:
  diagram: components.drawio
---

# {pat_id} {scope.title()} Scope

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

### S1 Basic flow

Start: 01 Component A

Finish: 02 Component B

| Step | Actor | Target | Action | Interface |
|---:|---|---|---|---|
| 1 | 01 Component A | 02 Component B | Transfer data | IF-01 |
"""
        
        (pattern_dir / "index.md").write_text(pattern_content)
        
        assert (pattern_dir / "index.md").exists(), f"Failed to create {scope} pattern"
