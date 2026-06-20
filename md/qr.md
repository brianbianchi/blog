# QR Codes

QR codes can do a lot more than link to a website. They can connect a phone to Wi-Fi, add a calendar event, or share a contact from your native camera app. Here are the formats for each use case.

## Formats

### URL
```
https://www.example.com/
```

### Phone
```
tel:+12345678900
```

### SMS
```
SMSTO:+12345678900:Message text here
SMSTO::Message text here
```

Omit the number to let the user choose the recipient after scanning.

### Wi-Fi
```
WIFI:S:<SSID>;T:<WEP|WPA|blank>;P:<PASSWORD>;H:<true|false|blank>;
```

| Param | Required | Description                          |
| ----- | -------- | ------------------------------------ |
| S     | Yes      | SSID                                 |
| T     | No       | Auth type: WEP, WPA, or blank (open) |
| P     | No       | Password                             |
| H     | No       | `true` if SSID is hidden             |

### Email
```
mailto:info@example.com?subject=Subject%20Here&body=Body%20here
```

### vCard
```
BEGIN:VCARD
VERSION:3.0
N:Smith;John;
TEL;TYPE=work,VOICE:(111) 555-1212
EMAIL:smith.j@smithdesigns.com
ORG:Smith Designs LLC
TITLE:Lead Designer
URL:https://www.smithdesigns.com
END:VCARD
```

| Field       | Required? | Description                               |
| :---------- | :-------- | :---------------------------------------- |
| BEGIN / END | Yes       | Start and end tags for the vCard block    |
| VERSION     | Yes       | vCard spec version (commonly `3.0`)       |
| N           | No        | Full name                                 |
| TEL;TYPE    | No        | Phone numbers and types (work, home, fax) |
| EMAIL       | No        | Email address                             |
| ORG         | No        | Company name                              |
| TITLE       | No        | Professional title                        |
| ADR         | No        | Address in structured format              |
| URL         | No        | Website link                              |

### Calendar Event
```
BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART:20240101T120000Z
DTEND:20240101T130000Z
SUMMARY:Event Title
END:VEVENT
END:VCALENDAR
```

[iCalendar spec →](https://en.wikipedia.org/wiki/ICalendar)

### Geo
```
geo:48.8588443,2.2943506?q=Eiffel%20Tower
```

### Crypto
```
bitcoin:1GdK9UzpHBzqzX2A9JFP3Di4weBwqgmoQA?amount=0.015&label=Bob%27s%20Cafe
```

### App Store
```
https://apps.apple.com/app/id000000000
https://play.google.com/store/apps/details?id=com.example.app
```

### Plain Text
```
Hello World!
```
