---
name: generating-stored-procedures
description: 'Use when you need to generate, validate, or deploy stored procedures
  for PostgreSQL, MySQL, or SQL Server.

  Creates database functions, triggers, and procedures with proper error handling
  and transaction management.

  Trigger with phrases like "generate stored procedure", "create database function",
  "write SQL procedure",

  "add trigger to table", or "create CRUD procedures".

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(psql:*), Bash(mysql:*), Bash(sqlcmd:*),
  Bash(python3:*)
version: 1.30.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- database
- deployment
- postgresql
- mysql
compatibility: Designed for Claude Code
---
# Stored Procedure Generator

Generate production-ready stored procedures for PostgreSQL, MySQL, and SQL Server with proper error handling, transaction management, and security best practices.

## Prerequisites

- Database connection credentials (host, port, database, user, password)
- Appropriate permissions: CREATE PROCEDURE, CREATE FUNCTION, EXECUTE
- Target database type identified (PostgreSQL, MySQL, or SQL Server)

## Instructions

### Step 1: Identify Database Type and Requirements

Determine the target database and procedure requirements:

```sql
-- PostgreSQL: Check version and extensions
SELECT version();
\dx

-- MySQL: Check version and settings
SELECT VERSION();
SHOW VARIABLES LIKE 'sql_mode';

-- SQL Server: Check version and edition
SELECT @@VERSION;
```

### Step 2: Generate Stored Procedure

**PostgreSQL Function (PL/pgSQL):**

```sql
CREATE OR REPLACE FUNCTION get_user_by_id(p_user_id INTEGER)
RETURNS TABLE(id INTEGER, username VARCHAR, email VARCHAR, created_at TIMESTAMP)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT u.id, u.username, u.email, u.created_at
    FROM users u
    WHERE u.id = p_user_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'User with ID % not found', p_user_id
            USING ERRCODE = 'P0002';
    END IF;
END;
$$;
```

**MySQL Stored Procedure:**

```sql
DELIMITER //
CREATE PROCEDURE GetUserById(IN p_user_id INT)
BEGIN
    DECLARE user_exists INT DEFAULT 0;

    SELECT COUNT(*) INTO user_exists FROM users WHERE id = p_user_id;

    IF user_exists = 0 THEN
        SIGNAL SQLSTATE '45000'  # 45000 = configured value
            SET MESSAGE_TEXT = 'User not found';
    END IF;

    SELECT id, username, email, created_at
    FROM users
    WHERE id = p_user_id;
END //
DELIMITER ;
```

**SQL Server Stored Procedure (T-SQL):**

```sql
CREATE PROCEDURE dbo.GetUserById
    @UserId INT
AS
BEGIN
    SET NOCOUNT ON;

    IF NOT EXISTS (SELECT 1 FROM dbo.Users WHERE Id = @UserId)
    BEGIN
        RAISERROR('User with ID %d not found', 16, 1, @UserId);
        RETURN;
    END

    SELECT Id, Username, Email, CreatedAt
    FROM dbo.Users
    WHERE Id = @UserId;
END;
GO
```

### Step 3: Add Transaction Management

**PostgreSQL with Transaction:**

```sql
CREATE OR REPLACE FUNCTION transfer_funds(
    p_from_account INTEGER,
    p_to_account INTEGER,
    p_amount NUMERIC(15,2)
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    -- Debit source account
    UPDATE accounts SET balance = balance - p_amount
    WHERE id = p_from_account AND balance >= p_amount;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Insufficient funds or invalid source account';
    END IF;

    -- Credit destination account
    UPDATE accounts SET balance = balance + p_amount
    WHERE id = p_to_account;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Invalid destination account';
    END IF;

    RETURN TRUE;
EXCEPTION
    WHEN OTHERS THEN
        RAISE;
END;
$$;
```

**MySQL with Transaction:**

```sql
DELIMITER //
CREATE PROCEDURE TransferFunds(
    IN p_from_account INT,
    IN p_to_account INT,
    IN p_amount DECIMAL(15,2)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    UPDATE accounts SET balance = balance - p_amount
    WHERE id = p_from_account AND balance >= p_amount;

    IF ROW_COUNT() = 0 THEN
        SIGNAL SQLSTATE '45000'  # 45000 = configured value
            SET MESSAGE_TEXT = 'Insufficient funds';
    END IF;

    UPDATE accounts SET balance = balance + p_amount
    WHERE id = p_to_account;

    COMMIT;
END //
DELIMITER ;
```

### Step 4: Validate Syntax

Use the validation script to check procedure syntax:

```bash
# Validate PostgreSQL procedure
python3 ${CLAUDE_SKILL_DIR}/scripts/stored_procedure_syntax_validator.py \
    --db-type postgresql \
    --file procedure.sql

# Validate MySQL procedure
python3 ${CLAUDE_SKILL_DIR}/scripts/stored_procedure_syntax_validator.py \
    --db-type mysql \
    --file procedure.sql
```

### Step 5: Deploy to Database

```bash
# Deploy to PostgreSQL
python3 ${CLAUDE_SKILL_DIR}/scripts/stored_procedure_deployer.py \
    --db-type postgresql \
    --host localhost \
    --database mydb \
    --file procedure.sql

# Deploy to MySQL
python3 ${CLAUDE_SKILL_DIR}/scripts/stored_procedure_deployer.py \
    --db-type mysql \
    --host localhost \
    --database mydb \
    --file procedure.sql
```

## Output

- SQL procedure file with proper syntax for target database
- Validation report confirming syntax correctness
- Deployment confirmation with execution results
- Rollback script for procedure removal

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `permission denied` | Missing CREATE PROCEDURE privilege | `GRANT CREATE PROCEDURE ON database TO user;` |
| `syntax error` | Invalid SQL for database type | Use database-specific syntax validator |
| `function already exists` | Procedure exists without OR REPLACE | Add `OR REPLACE` or `DROP` first |
| `undefined column` | Referenced column doesn't exist | Verify table schema before deployment |
| `transaction aborted` | Error during transaction | Check EXCEPTION handler and ROLLBACK logic |

## Examples

**Generate CRUD procedures for a table:**

```
User: Generate CRUD stored procedures for the 'products' table in PostgreSQL

Claude: I'll create four procedures for the products table:
1. create_product - Insert new product
2. get_product - Retrieve by ID
3. update_product - Update existing product
4. delete_product - Soft delete product
```

**Create audit trigger:**

```
User: Create a trigger to log all changes to the orders table

Claude: I'll create an audit trigger that:
1. Creates an orders_audit table if not exists
2. Captures INSERT, UPDATE, DELETE operations
3. Records old/new values, user, and timestamp
```

## Resources

- [`references/postgresql_stored_procedure_best_practices.md`](references/postgresql_stored_procedure_best_practices.md)
- [`references/mysql_stored_procedure_best_practices.md`](references/mysql_stored_procedure_best_practices.md)
- [`references/sqlserver_stored_procedure_best_practices.md`](references/sqlserver_stored_procedure_best_practices.md)
- [`references/database_security_guidelines.md`](references/database_security_guidelines.md)
- [`references/stored_procedure_optimization_techniques.md`](references/stored_procedure_optimization_techniques.md)

## Overview

Use when you need to generate, validate, or deploy stored procedures for PostgreSQL, MySQL, or SQL Server.
