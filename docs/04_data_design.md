# Data Design

## 1. Purpose

This document defines the data design for the Enterprise Agent Platform PoC.

The data design supports four product capabilities:

1. Enterprise knowledge retrieval
2. Business data query
3. Cross-source analysis
4. Business action workflows

The PoC uses realistic synthetic data rather than real customer data so that the project is reproducible, safe to publish, and suitable for deterministic evaluation.

## 2. Design Principles

### 2.1 Realistic but Synthetic

Synthetic data should preserve realistic business relationships:

- Orders reference existing customers and products.
- Sales follow controlled regional and product-level patterns.
- Tickets are associated with valid customers and products.
- Policy documents align with the business rules encoded in the database.

### 2.2 Structured + Unstructured Data

The platform contains two major data domains:

```text
Enterprise Data
├── Knowledge Data
│   └── Documents for RAG
└── Business Data
    └── Relational data for SQL tools
```

### 2.3 Ground Truth Must Be Constructible

Every evaluation task must have a known expected result.

Therefore:

- Knowledge questions map to known source passages.
- SQL questions have deterministic expected query results.
- Complex analysis tasks are built from controlled business patterns.
- Security tasks specify expected allow/block behavior.

### 2.4 Metadata Is Part of the Data Model

Each knowledge chunk must preserve metadata for:

- source tracking
- citation
- version control
- department ownership
- access control
- product / region scope

---

## 3. Enterprise Knowledge Data

Directory:

```text
data/documents/
├── product_manual/
├── sales_policy/
├── after_sales/
├── faq/
└── operation_sop/
```

Recommended PoC scale:

- 20-50 documents
- approximately 50,000-200,000 Chinese characters
- Markdown, TXT, and PDF
- selected documents with multiple versions

This is large enough to exercise retrieval and reranking while still allowing manual verification.

---

## 4. Knowledge Document Categories

### 4.1 Product Manuals

Example:

```text
X100_product_manual.md
X200_product_manual.pdf
X300_product_manual.md
```

Suggested contents:

- product overview
- specifications
- maintenance
- warranty
- troubleshooting

Example deterministic fact:

```text
X200 standard warranty: 3 years
```

### 4.2 Sales Policies

Example:

```text
2026_q1_sales_policy.md
2026_q2_sales_policy.md
2026_channel_discount_policy.md
```

Suggested contents:

- regional sales rules
- discount ranges
- promotion periods
- incentive conditions
- product-specific campaigns

These documents support the Hero Workflow:

> Analyze why South China sales decreased in Q2 and combine sales data with marketing policies.

### 4.3 After-sales Policies

Example:

```text
after_sales_sla.md
warranty_policy_2026.md
return_and_repair_policy.md
```

### 4.4 FAQ

Example:

```text
internal_faq.md
```

### 4.5 Operating Procedures

Example:

```text
ticket_escalation_sop.md
customer_followup_sop.md
discount_approval_sop.md
```

These support business-action and Human-in-the-loop scenarios.

---

## 5. Knowledge Metadata Schema

Recommended chunk metadata:

```json
{
  "document_id": "DOC-0001",
  "document_name": "2026_q2_sales_policy.md",
  "document_type": "sales_policy",
  "department": "sales",
  "version": "2026-Q2",
  "effective_date": "2026-04-01",
  "product": null,
  "region": "South China",
  "allowed_roles": ["sales", "management"],
  "section": "Regional Incentive Policy",
  "page": null,
  "source_path": "data/documents/sales_policy/2026_q2_sales_policy.md"
}
```

Important fields:

- `document_id`: stable identifier used by citation and evaluation
- `document_type`: manual / policy / FAQ / SOP
- `version`: distinguishes historical and current policies
- `allowed_roles`: retrieval-time authorization filter
- `section` / `page`: evidence tracing

---

## 6. Chunking Strategy

Initial strategy:

- chunk size: approximately 500-800 tokens
- overlap: approximately 80-120 tokens
- preserve section headings
- avoid breaking tables or ordered procedure steps

Each chunk should preserve:

```text
section title
+
chunk text
+
metadata
```

The exact chunk size is not considered final. It will be tuned during evaluation.

---

## 7. Embedding and Vector Storage

Initial embedding model:

```text
BGE-M3
```

Initial vector store:

```text
PostgreSQL + pgvector
```

Reasons:

- supports local deployment
- suitable for Chinese enterprise documents
- supports metadata filtering
- reduces PoC infrastructure complexity

The project must not claim BGE-M3 is universally optimal. Later evaluation should compare retrieval configurations if time permits.

---

## 8. Retrieval Data Flow

```text
User Query
↓
Query Embedding
↓
Vector Search
↓
Metadata / ACL Filter
↓
Top-N Candidate Chunks
↓
Reranker
↓
Top-K Evidence Chunks
↓
LLM Context
```

Initial parameters:

- vector retrieval: Top 20
- reranker output: Top 5

Final values are determined through evaluation.

---

## 9. Enterprise Business Database

Database:

```text
PostgreSQL
```

Core tables:

```text
customers
products
orders
sales
tickets
```

The schema is intentionally small enough to understand but rich enough to support joins, aggregation, trends, permissions, and multi-step analysis.

---

## 10. customers

Suggested schema:

```sql
CREATE TABLE customers (
    customer_id      BIGSERIAL PRIMARY KEY,
    customer_name    TEXT NOT NULL,
    region           TEXT NOT NULL,
    industry         TEXT NOT NULL,
    account_level    TEXT NOT NULL,
    owner_department TEXT NOT NULL,
    created_at       TIMESTAMP NOT NULL
);
```

Target scale:

```text
~1,000 customers
```

---

## 11. products

```sql
CREATE TABLE products (
    product_id      BIGSERIAL PRIMARY KEY,
    product_name    TEXT NOT NULL,
    category        TEXT NOT NULL,
    unit_price      NUMERIC(12, 2) NOT NULL,
    launch_date     DATE,
    active          BOOLEAN NOT NULL DEFAULT TRUE
);
```

Target scale:

```text
~50-100 products
```

---

## 12. orders

```sql
CREATE TABLE orders (
    order_id        BIGSERIAL PRIMARY KEY,
    customer_id     BIGINT NOT NULL REFERENCES customers(customer_id),
    product_id      BIGINT NOT NULL REFERENCES products(product_id),
    quantity        INTEGER NOT NULL,
    amount          NUMERIC(14, 2) NOT NULL,
    order_date      DATE NOT NULL,
    status          TEXT NOT NULL
);
```

Target scale:

```text
~50,000 orders
```

---

## 13. sales

```sql
CREATE TABLE sales (
    sale_id         BIGSERIAL PRIMARY KEY,
    region          TEXT NOT NULL,
    product_id      BIGINT NOT NULL REFERENCES products(product_id),
    amount          NUMERIC(14, 2) NOT NULL,
    quantity        INTEGER NOT NULL,
    sale_date       DATE NOT NULL,
    channel         TEXT NOT NULL
);
```

Target scale:

```text
~50,000 sales records
```

Controlled patterns should be encoded deliberately. For example:

- South China Q1 baseline sales are strong.
- An X200 promotion ends before Q2.
- South China X200 demand decreases in Q2.
- Other regions remain relatively stable.

This creates a known explanation for the Hero Workflow.

---

## 14. tickets

```sql
CREATE TABLE tickets (
    ticket_id       BIGSERIAL PRIMARY KEY,
    customer_id     BIGINT NOT NULL REFERENCES customers(customer_id),
    product_id      BIGINT REFERENCES products(product_id),
    issue_type      TEXT NOT NULL,
    priority        TEXT NOT NULL,
    status          TEXT NOT NULL,
    created_at      TIMESTAMP NOT NULL,
    resolved_at     TIMESTAMP
);
```

Target scale:

```text
~10,000 tickets
```

---

## 15. Synthetic Data Generation

Synthetic data should use:

- Python
- Faker
- deterministic random seed
- business-rule-based generation

Do not generate all data independently and uniformly.

Recommended deterministic seed:

```python
random.seed(42)
```

Suggested controlled scenarios:

1. South China X200 sales decline in Q2.
2. Q2 X200 incentives are weaker than Q1.
3. Ticket volume increases for one product family.
4. Selected enterprise customers make repeat purchases.
5. Some policies are role-restricted.
6. Old and current policy versions coexist.

These patterns make complex Agent tasks objectively evaluable.

---

## 16. Data Consistency Requirements

The synthetic environment must remain internally consistent:

- orders reference valid customers and products
- sales values align with product-price ranges
- documents reference products present in the database
- documents and database use the same region naming convention
- evaluation ground truth is derived from the seeded data
- current and historical policy versions are distinguishable

---

## 17. Permission Model

Initial roles:

```text
sales
support
management
admin
```

Example access matrix:

| Data / Document | sales | support | management | admin |
|---|---:|---:|---:|---:|
| Product Manual | Yes | Yes | Yes | Yes |
| Sales Policy | Yes | No | Yes | Yes |
| Support SOP | Limited | Yes | Yes | Yes |
| Management Report | No | No | Yes | Yes |
| Customer Data | Scoped | Scoped | Broad | Broad |

The PoC does not implement a complete enterprise IAM product. It implements enough role and scope information to demonstrate authorization-aware retrieval and tool execution.

---

## 18. Data Versioning

Selected documents should contain historical and current versions.

Example:

```text
2025_sales_policy.md
2026_q1_sales_policy.md
2026_q2_sales_policy.md
```

Metadata includes:

- version
- effective_date

Retrieval should prefer the currently effective version unless the user explicitly asks for historical policy.

---

## 19. Planned Data Artifacts

```text
data/
├── documents/
│   ├── product_manual/
│   ├── sales_policy/
│   ├── after_sales/
│   ├── faq/
│   └── operation_sop/
└── seed/
    ├── generate_customers.py
    ├── generate_products.py
    ├── generate_orders.py
    ├── generate_sales.py
    └── generate_tickets.py
```

Database initialization:

```text
infra/
└── init.sql
```

Evaluation data is specified separately in `05_evaluation_plan.md`.

---

## 20. Out of Scope

The first PoC does not require:

- real customer data
- data lake / Spark cluster
- Kafka streaming
- CDC pipeline
- dedicated vector database cluster
- full master-data-management system
- full enterprise IAM integration
- production-scale document ingestion

These can be discussed as production extensions in the final Solution Deck.
