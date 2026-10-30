# PROCESS DIAGRAMS (filled in P1-02 — Mermaid; export PNG/SVG for the final report)

Required by the course: overall process diagram + explanation per web app. Start from these skeletons.

## Overall
```mermaid
flowchart TD
  V[Visitor] -->|register / login| AUTH{Role?}
  AUTH -->|Hotel manager| M[Manager dashboard]
  AUTH -->|Guest| G[Guest home / search]
  M --> M1[Define hotel] --> M2[Define room types] --> M3[Define discount codes]
  M --> M4[View bookings] 
  M --> M5[View booked / free rooms]
  G --> S[Search: city, dates, capacity] --> L[Hotel list] --> D[Hotel & room details]
  D --> Q[Choose dates, rooms, discount code] --> B{Available?}
  B -->|yes| C[Booking confirmed] --> MY[My bookings] --> X[Cancel]
  B -->|no| S
```
TODO(P1-02, owner B): per-app diagrams — accounts (register/login/verify), hotels (manager CRUD, public search),
bookings (availability check, discount, create, cancel), reviews (bonus); plus a sequence diagram of "guest books a room".
