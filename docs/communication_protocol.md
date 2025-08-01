

# 📡 Communication Protocols

This document defines the communication protocols used between the components of the Smart Shelf LED Controller system.

---

## 🔄 Overview

The system consists of three main communicating components:

1. **Geotraqr Data Port** →  Shelf Light Switch and Location messages routed through geotraqr
2. **Geotraqr Command Port** → LED Commands
3. **App** → LED Controller

All messages are sent over **UDP** as **comma-separated values (CSV)**, with each message terminated by a **carriage return + newline (`\r\n`)**.

---

## 📥 1. Shelf Switch Message (Inbound)

Sent when a light switch on a shelf is activated.

### Protocol
- **Transport**: TCP
- **Port**: `9000`
- **Format**:'<timestamp>, SEN0,<Cabinet Controller ID>,LTSW,<Shelf Number>,<State>\r\n`

### Example

```
SWITCH,2,2025-07-24T14:15:22Z\r\n
```


### Fields
| Position | Field Name | Type   | Description                    |
|----------|------------|--------|--------------------------------|
| 1        | `timestamp`| int    | Milliseconds UTC timestamp     |
| 1        | `"SEN0"`   | string | Message type identifier        |
| 2        | `Cabinet Controller ID` | int    | ID of the cabinet controller     |
| 1        | `"LTSW"` | string | Message type identifier        |
| 2        | `Shelf Number` | int    | Shlef identifier 1-6    |
| 2        | `State` | int    | 1-Beam Broken,  0-Beam Unbroken    |

---

## 📥 2. RFID Location Message (Inbound)

Sent when an RFID tag reports its location.

### Protocol
- **Transport**: UDP
- **Port**: `9001`
- **Format**: `RFID,<tag_id>,<x>,<y>,<z>,<timestamp>\r\n`

### Example

```

RFID,abc123,10.3,4.8,1.9,2025-07-24T14:15:21Z\r\n

```

### Fields
| Position | Field Name | Type    | Description                    |
|----------|------------|---------|--------------------------------|
| 1        | `"RFID"`   | string  | Message type identifier        |
| 2        | `tag_id`   | string  | Unique RFID tag ID             |
| 3–5      | `x, y, z`  | float   | Coordinates in meters          |
| 6        | `timestamp`| string  | ISO8601 UTC timestamp          |

---

## 📤 3. LED Control Message (Outbound)

Sent from the app to the LED controller to update a shelf’s LED state.

### Protocol
- **Transport**: UDP
- **Port**: `9100`
- **Format**: `LED,<shelf_id>,<color>,<duration>\r\n`

### Example

```

LED,2,blue,5\r\n

````

### Fields
| Position | Field Name | Type   | Description                          |
|----------|------------|--------|--------------------------------------|
| 1        | `"LED"`    | string | Message type identifier              |
| 2        | `shelf_id` | int    | Shelf to control                     |
| 3        | `color`    | string | `"red"`, `"blue"`, `"white"`, `"off"`|
| 4        | `duration` | int    | Optional: how long to keep LED on (seconds) |

---

## ❌ Error Handling

- Malformed or incomplete messages are logged and ignored.
- Messages with invalid types or incorrect number of fields are discarded.
- Extra whitespace is trimmed from field values before processing.

---

## 🛡️ Security Considerations

- Assumes local network trust.
- Recommended mitigations (optional for future versions):
  - Limit accepted IP addresses or subnet
  - Validate input types strictly
  - Monitor for invalid frequency patterns (flooding)

---

## 🧪 Test Utilities

You can simulate messages using `netcat`:

```bash
# Send test shelf switch message
echo -ne "SWITCH,2,2025-07-24T14:15:22Z\r\n" | nc -u 127.0.0.1 9000

# Send test RFID location
echo -ne "RFID,abc123,10.3,4.8,1.9,2025-07-24T14:15:21Z\r\n" | nc -u 127.0.0.1 9001
````

---

## 📎 Appendix

* Message terminator: `\r\n` (carriage return + newline)
* Shelf and tag mappings: see `config/config.yaml`
* Application behavior logic: see [PRD](prd.md)

