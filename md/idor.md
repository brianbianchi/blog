# IDOR: When Access Controls Fail

Insecure Direct Object Reference is what happens when an application exposes a reference to an internal resource (a database record, a file, an account) and then fails to verify whether the requesting user is actually allowed to access it. The attacker doesn't exploit a complex vulnerability; they just change a number in a URL and see what happens.

It sounds almost too simple, but IDOR consistently appears among the most impactful bugs found in bug bounty programs. The reason it persists is instructive: developers tend to think carefully about authentication ("is this user logged in?") and much less carefully about authorization ("is this logged-in user allowed to access this specific thing?").

## The Core Pattern

The application exposes a direct identifier for a resource in a way the client can see and modify. That identifier points straight to the backing data with no additional access check.

Some classic examples:

```
GET /invoices/1042
```

Change it to `/invoices/1041`. If that's someone else's invoice and the server returns it without checking ownership, that's IDOR.

```
POST /api/messages
{"user_id": 452, "message": "hello"}
```

Change `user_id` to `451`. If the server sends the message as user 451 without verifying your session owns that account, you've found IDOR.

```
GET /download?file_id=8820
```

Increment the file ID. If you get someone else's file, same problem.

The identifier doesn't have to be a sequential integer. UUIDs are better for obscurity but not a fix (more on that later). The vulnerability is the missing authorization check, not the ID format.

## Where to Look

IDOR can hide anywhere the client sends a reference to a server-side resource. Worth checking:

**URL path parameters**: `/users/452/settings`, `/orders/1042`, `/tickets/7`

**Query string parameters**: `?account=452`, `?report_id=88`, `?token=abc`

**POST body fields**: Form submissions and JSON request bodies often contain IDs that reference records. These are easy to overlook because they're not visible in the URL bar.

**Hidden form fields**: Old-school but still present in legacy applications. The browser renders them invisibly, but they show up in the source and in Burp.

**Cookies**: Sometimes object references are stored directly in cookies rather than derived from the session. Less common, but worth checking.

**API response fields**: Sometimes a response includes IDs for related resources. Those IDs might be usable in subsequent requests to access those resources directly.

## Horizontal vs. Vertical Privilege Escalation

IDOR vulnerabilities lead to two flavors of escalation, and the distinction matters when assessing severity.

**Horizontal privilege escalation**: Accessing resources belonging to another user at the same privilege level. You're a regular user accessing another regular user's data. Changing `/profile/452` to `/profile/451` to read someone else's personal information is horizontal escalation.

**Vertical privilege escalation**: Using an IDOR to access resources or perform actions at a higher privilege level than your own. A regular user accessing an admin-only endpoint, or modifying a request field that sets your account role. This is generally more severe.

Some IDORs are horizontal at first glance but have vertical implications. If you can access any user's profile by ID, and admin accounts are just user records with a different role field, then enumerating to find an admin ID is effectively vertical escalation.

## Mass Assignment

Mass assignment is a related pattern worth understanding alongside IDOR. When a server-side object is populated directly from client-supplied data (common in frameworks that auto-bind request parameters to model attributes), an attacker can set fields they're not supposed to set.

```
POST /api/users/452
{"name": "Alice", "email": "alice@example.com", "role": "admin"}
```

If the server binds all of those fields without an allowlist, the attacker just promoted themselves. This isn't exactly IDOR (there's no reference traversal), but it stems from the same root cause: failing to enforce what clients are allowed to do, not just who they're allowed to be.

## Testing Approach

The standard methodology for finding IDOR is straightforward and doesn't require special tooling.

1. **Create two accounts** at the same privilege level. Call them User A and User B.

2. **Perform an action as User A** that creates or references a resource. Note every identifier in the request and response: URL parameters, body fields, response IDs.

3. **Switch to User B's session**, then replay User A's request using the identifiers from User A's resource. Does User B get access?

4. **Test the inverse**: User B creates a resource, try to access or modify it as User A.

Burp Suite makes this efficient. The "Match and Replace" feature or the Autorize extension can automate swapping session tokens so you can test access control systematically across many endpoints.

Also test unauthenticated access. Sometimes the authorization check is there for authenticated users but the endpoint is accessible without any session at all.

For APIs with predictable integer IDs, test one above and one below the IDs your account generates. If your account creates invoice #1100, try #1099 and #1101. If those belong to other users and you can access them, the vulnerability exists even if you can't enumerate all records.

## Prevention

### Check Authorization at the Object Level

Every time the server retrieves a resource using a client-supplied identifier, it must verify that the authenticated user is authorized to perform the requested action on that specific resource. This check should be server-side, based on the authenticated session, and it should happen every time, not just at login.

The check is conceptually simple:

```python
# Bad: retrieves invoice without checking ownership
invoice = Invoice.get(request.params['id'])
return invoice

# Good: ties the lookup to the authenticated user
invoice = Invoice.get_for_user(request.params['id'], current_user.id)
if invoice is None:
    return 403
return invoice
```

The "bad" version is trivially exploitable. The "good" version makes ownership part of the query itself so there's nothing to bypass at the application layer.

### Use Indirect References

Instead of exposing database primary keys directly, map them to per-user indirect references. The user sees an opaque token; the server maps it back to the real resource.

A common approach is UUIDs. They're not guessable in the way sequential integers are, so casual enumeration fails. But UUIDs are not a security control. If the authorization check is missing, a UUID is just a harder-to-guess identifier. An attacker who finds a UUID through some other means (a leaked URL, an API response, error messages) can still use it. The access check must exist regardless.

A stronger approach: generate a per-user HMAC over the resource ID, using a server-side secret. The client sees the HMAC, not the ID. Even if the HMAC is leaked, it can't be used to derive other valid references.

### Never Trust the Client to Enforce Access Control

This is the underlying principle. Any value the client sends can be modified. Authorization logic must live server-side, based on the authenticated session, not on values supplied in the request. A hidden form field that says `admin=false` is not a security control. A cookie that encodes the user's role is not trustworthy unless it's signed and verified server-side.
