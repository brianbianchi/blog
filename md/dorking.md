# Google Dorking

Google search operators let you be precise in filtering results. They allow you to find exactly the file type you need, limit results to one domain, or exclude noise that pollutes your query. They can also surface things that were never meant to be public, such as exposed `.env` files, open admin panels, and database dumps sitting on misconfigured servers. Understanding how dorking works makes you both a better researcher and more aware of what your own infrastructure might be leaking.

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
