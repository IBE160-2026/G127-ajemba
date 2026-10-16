# 01 Log in and Register

Reached from: app start when logged out. Leads to: My lectures (02), or the demo lecture (05).

## Wide screen

```
+--------------------------------------------------------------+
|  Recall                                                      |
+--------------------------------------------------------------+
|                                                              |
|        +--------------------------------------------+        |
|        |  Recall                                    |        |
|        |  Upload a lecture. Read the summary.       |        |
|        |  Test what you understand.                 |        |
|        |                                            |        |
|        |   [ Log in ]   [ Register ]    <- tabs     |        |
|        |   ========                                 |        |
|        |                                            |        |
|        |   Email                                    |        |
|        |   [ ______________________________ ]      |        |
|        |                                            |        |
|        |   Password                                 |        |
|        |   [ ______________________________ ]      |        |
|        |   [ ] Show password                        |        |
|        |                                            |        |
|        |   [ Log in ]                               |        |
|        |                                            |        |
|        |   ---------------- or ----------------     |        |
|        |                                            |        |
|        |   [ ▶ Try the demo ]                       |        |
|        |   No account or API key needed.            |        |
|        +--------------------------------------------+        |
+--------------------------------------------------------------+
```

## Register tab (differences)

```
|   Email                    [ ______________________ ]        |
|   Password                 [ ______________________ ]        |
|   [ ] Show password                                          |
|   (i) We can't reset passwords yet. Please remember yours.   |
|   [ Register ]                                               |
```

## Error example

```
|   Email                                                      |
|   [ anna@example.com __________ ]                            |
|   (!) This email is already in use. Log in, or use another.  |
```

## Phone

Same card, full width, 16px margins. The two tabs share the width equally. "Try the demo" stays visible below the main button without scrolling on a normal phone.

## Notes
- Visible labels above fields. No placeholder-only labels.
- No "Forgot password" link (not in v1).
- "Try the demo" is always shown, with or without an API key.
