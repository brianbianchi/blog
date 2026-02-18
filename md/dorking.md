# Google Dorking

Google dorking involves using special operators and filters in search queries to uncover information that isn’t immediately visible through standard searches. It’s an intelligence-gathering technique that helps cybersecurity researchers, digital investigators, and power users discover hidden files, configurations, and data accidentally exposed to the internet.

## Useful Tools

If you want to automate or scale your exploration, check out:

- [**pagodo (Passive Google Dorking)**](https://github.com/opsdisk/pagodo): Automates Google dork queries.
- [**Google Hacking Database (GHDB)**](https://www.exploit-db.com/google-hacking-database): A public collection of Google dorks.

## Essential Search Filters

| Filter               | Description                                                         | Example                              |
| :------------------- | :------------------------------------------------------------------ | :----------------------------------- |
| `allintext:`         | Finds all keywords appearing in page text.                          | `allintext:"login admin"`            |
| `intext:`            | Finds any of the terms appearing in page text.                      | `intext:"password"`                  |
| `inurl:`             | Searches for keywords in URLs.                                      | `inurl:"admin"`                      |
| `allinurl:`          | Finds pages containing multiple keywords in the URL.                | `allinurl:"php?id="`                 |
| `intitle:`           | Finds pages with certain words in the title.                        | `intitle:"index of"`                 |
| `allintitle:`        | Requires multiple keywords in the title.                            | `allintitle:"dashboard login"`       |
| `site:`              | Limits results to a specific domain or site.                        | `site:example.com`                   |
| `filetype:`          | Searches for specific file formats (pdf, docx, xls, etc.).          | `filetype:pdf`                       |
| `link:`              | Lists pages that link to a specific page.                           | `link:example.com`                   |
| `numrange:`          | Finds results containing numbers within a range.                    | `camera $300..$600`                  |
| `before:` / `after:` | Filters results published before or after specific dates.           | `before:2021-01-01 after:2020-01-01` |
| `related:`           | Finds sites similar to the one specified.                           | `related:bbc.com`                    |
| `cache:`             | Displays Google’s cached version of a page.                         | `cache:example.com`                  |
| `map:`               | Runs a query through Google Maps.                                   | `map:coffee shops Charleston`        |
| `define:`            | Returns dictionary definitions.                                     | `define:entropy`                     |
| `source:`            | Restricts results to a specific news source (works in Google News). | `source:reuters "market update"`     |
| `location:`          | Filter news results by region                                       | `location:US`                        |


*(Try combining filters for powerful precision — see examples below.)*

***

## Operators and Combinations

| Operator    | Description                                | Example                                             |
| :---------- | :----------------------------------------- | :-------------------------------------------------- |
| `" "`       | Exact phrase search                        | `"project report"`                                  |
| `OR`        | Returns results with either keyword        | `site:facebook.com OR site:twitter.com`             |
| `AND`       | Returns results with both terms            | `filetype:pdf AND cybersecurity`                    |
| `( )`       | Groups multiple conditions                 | `(inurl:login OR inurl:portal) AND intitle:"admin"` |
| `+` / `-`   | Include or exclude results                 | `+cybersecurity -reddit`                            |
| `~`         | Searches for synonyms                      | `~backup`                                           |
| `*`         | Wildcard placeholder for any word          | `"best * tools for OSINT"`                          |
| `AROUND(n)` | Finds keywords within `n` words each other | `"password" AROUND(5) "login"`                      |

***

## Example Combinations

Here are a few practical examples of dorks:

```
site:gov filetype:xls "password"
intitle:"index of" "admin"
(site:facebook.com OR site:twitter.com) intext:"login"
```

These examples illustrate how combining operators can surface data that would otherwise be buried deep in the web.

***