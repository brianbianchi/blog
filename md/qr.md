# QR Codes

Quick Response (QR) codes are a type of two-dimensional barcode that can store URLs, text, contact information, Wi-Fi credentials, and more. They bridge the physical and digital worlds by letting your phone instantly open a URL, send an SMS, or connect to a network by scanning  with your native camera app.

***

## Common QR Code Types

Below are the useful formats you can use to generate a QR code.

***

### 1. URL

Directs users to a specific web page.  
Example:

```
https://www.google.com/
```

***

### 2. Phone Number

Starts a phone call automatically.  

```
tel:+12345678900
```

***

### 3. SMS Message

Sends a pre-filled text message.  

```
SMSTO:+12345678900:This is a sample text message
```

> You can leave out the number—`SMSTO::This is a sample text message`—to let the user choose the recipient after scanning.

***

### 4. Wi-Fi Connection

Let users connect to Wi-Fi instantly without typing credentials.  

```
WIFI:S:<SSID>;T:<WEP|WPA|blank>;P:<PASSWORD>;H:<true|false|blank>;
```

| Parameter | Optional? | Example          | Description                               |
| :-------- | :-------- | :--------------- | :---------------------------------------- |
| S         | Required  | MyNetworkName    | Network SSID.                             |
| T         | Optional  | WPA              | Authentication type (WEP, WPA, or blank). |
| P         | Optional  | ThisIsMyPassword | Password (ignored if T is blank).         |
| H         | Optional  | true             | True if the network SSID is hidden.       |

***

### 5. Email

Generates a pre-written message in the user’s default email client.

```
mailto:info@example.com?subject=Issue%20with%20your%20product&body=Body%20goes%20here
```

***

### 6. vCard (Contact Details)

Encodes professional contact information, which can be saved directly to a phone.

```
BEGIN:VCARD
N:Smith;John;
TEL;TYPE=work,VOICE:(111) 555-1212
EMAIL:smith.j@smithdesigns.com
ORG:Smith Designs LLC
TITLE:Lead Designer
URL:https://www.smithdesigns.com
VERSION:3.0
END:VCARD
```

| Field       | Required? | Description                                 |
| :---------- | :-------- | :------------------------------------------ |
| BEGIN / END | Required  | Start and end tags for the vCard block.     |
| N           | Optional  | Full name.                                  |
| TEL;TYPE    | Optional  | Phone numbers and types (work, home, fax).  |
| EMAIL       | Optional  | Email address.                              |
| ORG         | Optional  | Company name.                               |
| TITLE       | Optional  | Professional title.                         |
| ADR         | Optional  | Address in structured format.               |
| URL         | Optional  | Website link.                               |
| VERSION     | Required  | Version of the vCard spec (commonly `3.0`). |

***

### 7. Calendar Event

Allows users to add events directly to their calendars.

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

[See the iCalendar specification →](https://en.wikipedia.org/wiki/ICalendar)

***

### 8. Cryptocurrency

Used for Bitcoin, Ethereum, and other digital wallets to request payments or display addresses.

```
bitcoin:1GdK9UzpHBzqzX2A9JFP3Di4weBwqgmoQA?amount=0.015&label=Bob%27s%20Cafe&message=Purchase%20at%20Bob%27s%20Cafe
```

***

### 9. App Store

Links directly to specific mobile app store pages.

```
https://apps.apple.com/app/id000000000
https://play.google.com/store/apps/details?id=com.example.app
```

***

### 10. Geolocation

Opens a user’s map app and displays a specific location.

```
geo:48.8588443,2.2943506?q=Eiffel%20Tower
```

***

### 11. Plain Text 

Displays custom text, notes, or a verification code when scanned.

```
Hello World!
```

***