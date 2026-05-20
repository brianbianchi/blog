# Google Dorking

Search operators to surface information not visible through standard queries, such as exposed configs, hidden files, accidentally public data.

## Tools

- [pagodo](https://github.com/opsdisk/pagodo) — automates Google dork queries
- [Google Hacking Database (GHDB)](https://www.exploit-db.com/google-hacking-database) — public dork collection

## Filters

| Filter               | Description                        | Example                          |
| :------------------- | :--------------------------------- | :------------------------------- |
| `allintext:`         | All keywords in page text          | `allintext:"login admin"`        |
| `intext:`            | Any term in page text              | `intext:"password"`              |
| `inurl:`             | Keywords in URL                    | `inurl:"admin"`                  |
| `allinurl:`          | Multiple keywords in URL           | `allinurl:"php?id="`             |
| `intitle:`           | Keywords in page title             | `intitle:"index of"`             |
| `allintitle:`        | Multiple keywords in title         | `allintitle:"dashboard login"`   |
| `site:`              | Limit to domain                    | `site:example.com`               |
| `filetype:` / `ext:` | Specific file format               | `filetype:pdf`                   |
| `link:`              | Pages linking to a URL             | `link:example.com`               |
| `numrange:`          | Numbers within a range             | `camera $300..$600`              |
| `before:` / `after:` | Filter by publish date             | `before:2021-01-01`              |
| `related:`           | Similar sites                      | `related:bbc.com`                |
| `cache:`             | Google's cached version            | `cache:example.com`              |
| `define:`            | Dictionary definition              | `define:entropy`                 |
| `source:`            | Specific news source (Google News) | `source:reuters "market update"` |
| `location:`          | Filter news by region              | `location:US`                    |

## Operators

| Operator    | Description             | Example                                             |
| :---------- | :---------------------- | :-------------------------------------------------- |
| `" "`       | Exact phrase            | `"project report"`                                  |
| `OR`        | Either keyword          | `site:facebook.com OR site:twitter.com`             |
| `AND`       | Both terms              | `filetype:pdf AND cybersecurity`                    |
| `( )`       | Group conditions        | `(inurl:login OR inurl:portal) AND intitle:"admin"` |
| `-`         | Exclude results         | `cybersecurity -reddit`                             |
| `*`         | Wildcard                | `"best * tools for OSINT"`                          |
| `AROUND(n)` | Keywords within n words | `"password" AROUND(5) "login"`                      |

## Examples

```
site:gov filetype:xls "password"
intitle:"index of" "admin"
(site:facebook.com OR site:twitter.com) intext:"login"
inurl:".env" DB_PASSWORD
filetype:log username password
site:example.com ext:php inurl:?id=
intitle:"index of" ".ssh"
site:pastebin.com "api_key"
```
