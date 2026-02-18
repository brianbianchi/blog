# QR codes

Quick response, or QR, is a type of barcode that can store a multitude of information. [docs](https://www.qr-code-generator.com/solutions/)

## URL

```
https://www.google.com/
```

## Phone number

```
tel:+12345678900
```

## SMS message

```
SMSTO:+12345678900:This is a sample text message
SMSTO::This is a sample text message // phone number can be added after scanning
```

## WIFI connection

```
WIFI:S:<SSID>;T:<WEP|WPA|blank>;P:<PASSWORD>;H:<true|false|blank>;
```

| Parameter | Optional? | Example          | Description                                                             |
| --------- | --------- | ---------------- | ----------------------------------------------------------------------- |
| T         | Optional  | WPA              | Authentication type; can be WEP or WPA, or leave empty for no password. |
| S         | Required  | MyNetworkName    | Network SSID. Required.                                                 |
| P         | Optional  | ThisIsMyPassword | Password, ignored if T is left blank.                                   |
| H         | Optional  | true             | True if the network SSID is hidden.                                     |

## Email

```
mailto: info@example.com
?subject=Issue%20with%20your%20product
&body=Body%20goes%20here
```

## Contact

```
BEGIN:VCARD
N:Smith;John;
TEL;TYPE=work,VOICE:(111) 555-1212
TEL;TYPE=home,VOICE:(404) 386-1017
TEL;TYPE=fax:(866) 408-1212
EMAIL:smith.j@smithdesigns.com
ORG:Smith Designs LLC
TITLE:Lead Designer
ADR;TYPE=WORK,PREF:;;151 Moore Avenue;Grand Rapids;MI;49503;United States of America
URL:https://www.smithdesigns.com
VERSION:3.0
END:VCARD
```

| Parameter | Optional? | Description                                                              | Format                                                                                            |
| --------- | --------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------- |
| BEGIN     | Required  | All vCards must start with this parameter                                | BEGIN:VCARD                                                                                       |
| N         | Optional  | Full name                                                                | N:Smith;John;                                                                                     |
| TEL;TYPE  | Optional  | Telephone number and type (work, home, fax)                              | TEL;TYPE=work,VOICE:(111) 555-1212 TEL;TYPE=home,VOICE:(404) 386-1017 TEL;TYPE=fax:(866) 408-1212 |
| EMAIL     | Optional  | Email address                                                            | EMAIL:smith.j@smithdesigns.com                                                                    |
| ORG       | Optional  | Company name                                                             | ORG:Smith Designs LLC                                                                             |
| TITLE     | Optional  | Job title                                                                | TITLE:Lead Designer                                                                               |
| ADR; TYPE | Optional  | Home or work address in order: Street; City; State; Postal Code; Country | ADR;TYPE=WORK,PREF:;;151 Moore Avenue;Grand Rapids;MI;49503;United States of America              |
| URL       | Optional  | Link to a website                                                        | URL:https://www.smithdesigns.com                                                                  |
| VERSION   | Required  | The version of the vCard specification.                                  | VERSION:3.0                                                                                       |
| END       | Required  | All vCards must end with this parameter                                  | END:VCARD                                                                                         |

## Calendar

[docs](https://en.wikipedia.org/wiki/ICalendar)

```
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//hacksw/handcal//NONSGML v1.0//EN
BEGIN:VEVENT
UID:uid1@example.com
DTSTAMP:19970714T170000Z
ORGANIZER;CN=John Doe:MAILTO:john.doe@example.com
DTSTART:19970714T170000Z
DTEND:19970715T035959Z
SUMMARY:Bastille Day Party
GEO:48.85299;2.36885
END:VEVENT
END:VCALENDAR
```

## Crypto

```
bitcoin:1GdK9UzpHBzqzX2A9JFP3Di4weBwqgmoQA?
amount=0.015&
label=Bob%27s%20Cafe&
message=Purchase%20at%20Bob%27s%20Cafe
```
