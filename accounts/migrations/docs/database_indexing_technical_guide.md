# Database Indexing: Technical Guide

## Table of Contents
1. [Introduction to Database Indexing](#introduction-to-database-indexing)
2. [Indexing Fundamentals](#indexing-fundamentals)
3. [Django Indexing Implementation](#django-indexing-implementation)
4. [Case Study: Accounts Migration Indexes](#case-study-accounts-migration-indexes)
5. [Performance Analysis](#performance-analysis)
6. [Best Practices](#best-practices)
7. [SQL Generation](#sql-generation)

---

## Introduction to Database Indexing

Database indexes are specialized data structures that improve the speed of data retrieval operations on database tables. An index works similarly to an index in a book—instead of scanning every page to find information, you can quickly locate the page number through the index.

### Key Concepts

**Index Structure**: Most databases use B-Tree (Balanced Tree) or B+Tree structures for indexes, which provide O(log n) search complexity.

**Trade-offs**:
- ✅ **Pros**: Faster SELECT queries, efficient filtering and sorting
- ❌ **Cons**: Slower INSERT/UPDATE/DELETE operations, additional storage space, maintenance overhead

---

## Indexing Fundamentals

### 1. Single-Column Index

A single-column index is created on one field and optimizes queries that filter or sort by that specific field.

**Structure**:
```
Index on field 'email':
+------------------+--------+
| Email            | Row ID |
+------------------+--------+
| alice@email.com  | 5      |
| bob@email.com    | 2      |
| carol@email.com  | 7      |
+------------------+--------+
```

**Use Case**: When queries frequently filter by a single field.

### 2. Composite Index (Multi-Column Index)

A composite index is created on multiple fields and optimizes queries that filter by those fields in combination or by the leftmost prefix.

**Structure**:
```
Composite index on (role, email):
+-------------+------------------+--------+
| Role        | Email            | Row ID |
+-------------+------------------+--------+
| patient     | alice@email.com  | 1      |
| patient     | bob@email.com    | 2      |
| psychologist| carol@email.com  | 3      |
+-------------+------------------+--------+
```

**Leftmost Prefix Rule**: A composite index on `(role, email)` can be used for:
- Queries filtering by `role` only
- Queries filtering by `role` AND `email`
- **NOT** for queries filtering by `email` only (unless there's a separate email index)

---

## Django Indexing Implementation

### Method 1: Model Meta Options (Declarative)

```python
class Account(models.Model):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20)
    
    class Meta:
        indexes = [
            models.Index(fields=['role', 'email'], name='accounts_role_email_idx'),
            models.Index(fields=['email'], name='accounts_email_idx'),
        ]
```

### Method 2: Migration Operations (Imperative)

```python
operations = [
    migrations.CreateModel(
        name='Account',
        fields=[...],
        options={
            'indexes': [
                models.Index(fields=['role', 'email'], name='accounts_ac_role_026657_idx'),
                models.Index(fields=['email'], name='accounts_ac_email_b00920_idx')
            ],
        },
    ),
]
```

### Index Naming Convention

Django automatically generates index names with the pattern:
```
{app_label}_{model_name}_{field_names}_{hash}_idx
```

Example: `accounts_ac_role_026657_idx`
- `accounts`: app label
- `ac`: abbreviated model name (Account)
- `role`: field name (first in composite)
- `026657`: hash for uniqueness
- `idx`: index suffix

---

## Case Study: Accounts Migration Indexes

### Migration File Analysis

**File**: `accounts/migrations/0001_initial.py`

**Model**: Account

**Fields**:
```python
('email', models.EmailField(max_length=254, unique=True, verbose_name='Email Address'))
('role', models.CharField(choices=[('patient', 'Patient'), ('psychologist', 'Psychologist')], 
                         max_length=20, verbose_name='Role'))
```

### Index Configuration

#### Index 1: Composite Index on (role, email)

```python
models.Index(fields=['role', 'email'], name='accounts_ac_role_026657_idx')
```

**Technical Details**:
- **Type**: B-Tree composite index
- **Fields**: `role` (VARCHAR(20)), `email` (VARCHAR(254))
- **Order**: role → email (left to right)
- **Cardinality**: 
  - `role`: Low (2 distinct values: 'patient', 'psychologist')
  - `email`: High (unique constraint)

**Optimization Target**:
```python
# Optimized queries
Account.objects.filter(role='patient', email='user@example.com')
Account.objects.filter(role='psychologist').order_by('email')
Account.objects.filter(role='patient')
```

**Storage Impact**:
- Index entry size: ~20 bytes (role) + ~254 bytes (email) + 8 bytes (row pointer) ≈ 282 bytes per row
- For 10,000 records: ~2.8 MB

#### Index 2: Single Index on email

```python
models.Index(fields=['email'], name='accounts_ac_email_b00920_idx')
```

**Technical Details**:
- **Type**: B-Tree single-column index
- **Field**: `email` (VARCHAR(254))
- **Unique Constraint**: Yes (via `unique=True` on field definition)
- **Cardinality**: High (each email is unique)

**Why Both Indexes?**

The composite index `(role, email)` **cannot** efficiently handle queries that filter by `email` alone due to the leftmost prefix rule. The separate `email` index ensures optimal performance for:

```python
# Requires dedicated email index
Account.objects.get(email='user@example.com')
Account.objects.filter(email__icontains='gmail.com')
```

**Storage Impact**:
- Index entry size: ~254 bytes (email) + 8 bytes (row pointer) ≈ 262 bytes per row
- For 10,000 records: ~2.6 MB

### Index Redundancy Analysis

**Question**: Is the email index redundant since it's part of the composite index?

**Answer**: No, because:
1. **Leftmost Prefix Rule**: `(role, email)` index cannot be used for `email`-only queries
2. **Query Patterns**: Email lookups (authentication, uniqueness checks) are common and don't involve `role`
3. **Performance**: Direct email lookup requires O(log n) with single index vs O(n) table scan without it

---

## Performance Analysis

### Benchmark Scenarios

#### Scenario 1: Role-Based Filtering

**Query**: Get all psychologists
```python
Account.objects.filter(role='psychologist')
```

**Without Index**:
- Operation: Full table scan
- Time Complexity: O(n)
- Records Scanned: 10,000 (entire table)
- Estimated Time: 50-100ms

**With Composite Index `(role, email)`**:
- Operation: Index range scan
- Time Complexity: O(log n + k) where k = matching rows
- Records Scanned: ~5,000 (psychologists only)
- Index Lookups: O(log 10,000) ≈ 13 comparisons
- Estimated Time: 5-10ms
- **Speedup**: 10x faster

#### Scenario 2: Email Lookup (Authentication)

**Query**: Find user by email
```python
Account.objects.get(email='user@example.com')
```

**Without Email Index**:
- Operation: Full table scan
- Time Complexity: O(n)
- Records Scanned: 10,000 (average 5,000)
- Estimated Time: 50-100ms

**With Email Index**:
- Operation: Index seek
- Time Complexity: O(log n)
- Records Scanned: 1
- Index Lookups: O(log 10,000) ≈ 13 comparisons
- Estimated Time: 0.5-2ms
- **Speedup**: 50-100x faster

#### Scenario 3: Role + Email Filter

**Query**: Verify psychologist email
```python
Account.objects.filter(role='psychologist', email='doc@example.com')
```

**Without Index**:
- Operation: Full table scan
- Time Complexity: O(n)
- Records Scanned: 10,000
- Estimated Time: 50-100ms

**With Composite Index `(role, email)`**:
- Operation: Index seek (exact match on both fields)
- Time Complexity: O(log n)
- Records Scanned: 1
- Index Lookups: O(log 5,000) ≈ 12 comparisons to role, then direct email lookup
- Estimated Time: 0.3-1ms
- **Speedup**: 100-300x faster

### Write Operation Impact

**INSERT Performance**:

| Operation | Without Indexes | With 2 Indexes | Overhead |
|-----------|----------------|----------------|----------|
| Single INSERT | 1ms | 1.5ms | +50% |
| Bulk INSERT (1000) | 500ms | 750ms | +50% |

**Explanation**: Each INSERT must update both indexes, adding overhead. However, this is acceptable because:
- Account creation is infrequent compared to lookups
- 0.5ms overhead per insert is negligible
- Read performance gains far outweigh write costs

---

## Best Practices

### 1. Composite Index Field Order

**Rule**: Place the most selective (highest cardinality) field first, UNLESS query patterns dictate otherwise.

**Example Analysis**:
```python
# Current: (role, email)
models.Index(fields=['role', 'email'])

# Cardinality:
# - role: 2 distinct values (low)
# - email: 10,000 distinct values (high)
```

**Why `role` comes first?**
- Query patterns often filter by `role='patient'` OR `role='psychologist'` first
- The index efficiently partitions data into two groups
- Email within each group is already sorted for fast lookups
- Supports both `filter(role=...)` and `filter(role=..., email=...)`

**Alternative (email, role) would be worse**:
- Cannot efficiently support `filter(role=...)` queries (most common use case)
- Would require filtering 10,000 emails then checking role

### 2. When to Use Composite Indexes

✅ **Use Composite Index When**:
- Queries frequently filter by multiple fields together
- Fields are commonly used in WHERE clauses together
- ORDER BY uses multiple fields

❌ **Avoid Composite Index When**:
- Fields are queried independently most of the time
- One field is rarely used alone
- Index size becomes prohibitive

### 3. Index Cardinality Guidelines

**High Cardinality** (Good for indexing):
- Email addresses (unique)
- User IDs
- Timestamps with high precision

**Low Cardinality** (Poor standalone index):
- Gender (M/F/O - 3 values)
- Role (patient/psychologist - 2 values)
- Boolean flags

**Medium Cardinality** (Context-dependent):
- Status fields (5-20 values)
- Categories
- Postal codes

### 4. Index Maintenance

**Storage Monitoring**:
```sql
-- Check index sizes (PostgreSQL)
SELECT 
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;
```

**Rebuild Strategy**:
- Indexes automatically maintained by Django/database
- Consider REINDEX for heavily updated tables (monthly/quarterly)
- Monitor index bloat in production

---

## SQL Generation

### PostgreSQL

When Django runs the migration, it generates the following SQL:

#### Create Table with Fields
```sql
CREATE TABLE "accounts_account" (
    "id" bigserial NOT NULL PRIMARY KEY,
    "name" varchar(100) NOT NULL,
    "last_name" varchar(100) NOT NULL,
    "age" integer NOT NULL CHECK ("age" >= 0),
    "gender" varchar(1) NOT NULL,
    "phone" varchar(20) NOT NULL,
    "email" varchar(254) NOT NULL UNIQUE,
    "role" varchar(20) NOT NULL,
    "created_at" timestamp with time zone NOT NULL,
    "updated_at" timestamp with time zone NOT NULL
);
```

#### Create Composite Index
```sql
CREATE INDEX "accounts_ac_role_026657_idx" 
ON "accounts_account" ("role", "email");
```

**Breakdown**:
- `CREATE INDEX`: SQL command to create an index
- `accounts_ac_role_026657_idx`: Unique index name
- `ON "accounts_account"`: Target table
- `("role", "email")`: Indexed columns in order

**Database Behavior**:
1. Creates a B-Tree structure
2. Stores entries as `(role_value, email_value, row_id)`
3. Sorts entries lexicographically: first by role, then by email
4. Maintains index automatically on INSERT/UPDATE/DELETE

#### Create Email Index
```sql
CREATE INDEX "accounts_ac_email_b00920_idx" 
ON "accounts_account" ("email");
```

**Note**: Django also creates an implicit unique constraint index via `UNIQUE` keyword in the email field definition.

### MySQL/MariaDB

```sql
CREATE INDEX `accounts_ac_role_026657_idx` 
ON `accounts_account` (`role`, `email`);

CREATE INDEX `accounts_ac_email_b00920_idx` 
ON `accounts_account` (`email`);
```

### SQLite

```sql
CREATE INDEX "accounts_ac_role_026657_idx" 
ON "accounts_account" ("role", "email");

CREATE INDEX "accounts_ac_email_b00920_idx" 
ON "accounts_account" ("email");
```

**SQLite Note**: SQLite uses the same B-Tree structure but with different internal optimizations due to its embedded nature.

---

## Advanced Concepts

### Index Selectivity

**Definition**: The ratio of distinct values to total rows.

```
Selectivity = Distinct Values / Total Rows
```

**Examples**:
- `email`: 10,000 / 10,000 = 1.0 (perfect selectivity)
- `role`: 2 / 10,000 = 0.0002 (poor selectivity)

**Rule**: Higher selectivity = better index performance

### Covering Indexes

A **covering index** contains all columns needed by a query, eliminating the need to access the table.

**Example**:
```python
# Query
Account.objects.filter(role='patient').values('email')

# Index (role, email) is "covering" - no table access needed
# All required data (role, email) is in the index itself
```

**Performance Gain**: Eliminates random I/O to fetch table rows.

### Index-Only Scans

Modern databases (PostgreSQL 9.2+) support index-only scans where:
1. Query uses only indexed columns
2. Visibility map indicates no dead tuples
3. Database reads only index, not table

**Example**:
```sql
-- Can use index-only scan
SELECT role, email FROM accounts_account WHERE role = 'patient';

-- Cannot use index-only scan (needs 'name' from table)
SELECT role, email, name FROM accounts_account WHERE role = 'patient';
```

---

## Conclusion

The `accounts/migrations/0001_initial.py` migration implements a well-designed indexing strategy:

1. **Composite Index** `(role, email)`: Optimizes role-based filtering and combined lookups
2. **Single Index** `email`: Ensures fast authentication and unique email lookups
3. **No Redundancy**: Both indexes serve distinct query patterns
4. **Balanced Trade-off**: Minimal write overhead for significant read performance gains

This design demonstrates adherence to database optimization best practices and Django's indexing conventions, providing a solid foundation for the accounts application's performance.

---

## References

- Django Documentation: [Model Indexes](https://docs.djangoproject.com/en/stable/ref/models/indexes/)
- PostgreSQL Documentation: [Indexes](https://www.postgresql.org/docs/current/indexes.html)
- Database Internals: B-Tree Index Structures
- Django ORM Query Optimization Guide
