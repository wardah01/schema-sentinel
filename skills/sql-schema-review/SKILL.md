---
name: sql-schema-review
description: Reviews SQL database schemas (CREATE TABLE scripts) for normalization problems, weak data types, missing keys and constraints, missing indexes, and security risks such as plaintext passwords or stored card numbers. Use when the user shares a .sql schema file or asks to critique, audit, or improve a database design.
---

# SQL Schema Review

## When to use this skill

Use it when the user provides a SQL schema or asks for a database design review.

## How to review

Read the whole schema first, then check each category below. Report only issues actually present in the schema; do not invent problems.

1. **Keys and constraints**
   - Every table needs a PRIMARY KEY.
   - Relationships need FOREIGN KEY constraints.
   - Fields that must always have a value need NOT NULL.
   - Natural-unique fields (email, username) need UNIQUE.

2. **Normalization**
   - Flag repeated data that belongs in its own table (e.g. a user's name and phone copied into another table).
   - Flag columns that hold several values in one field.

3. **Data types**
   - Money should use DECIMAL, never FLOAT.
   - Dates and times should use DATE/TIMESTAMP, never VARCHAR.
   - Phone numbers should be text, not integers.
   - Status fields should use an ENUM or CHECK constraint, or a lookup table.

4. **Indexes**
   - Foreign key columns and frequently searched columns should be indexed.

5. **Security**
   - Passwords must be stored as salted hashes, never plaintext.
   - Full card numbers must not be stored; use a payment provider's token instead.
   - Flag other sensitive personal data that needs protection.

## Output format

For each issue, give:

- **Severity:** High, Medium, or Low
- **Where:** table and column
- **Problem:** one sentence
- **Fix:** one concrete suggestion, with corrected SQL if short

End with a short summary of the three most important fixes.
