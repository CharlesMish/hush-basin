# District Zero P1A v1.2.4I adjudication ledger

| Item | Disposition | Evidence / authority |
|---|---|---|
| H evidence identity | ACCEPT | `8d8555882890146509723a4608180614293d2719811453d513e51660c981ca90`; 80/80 root checksum records pass. |
| H selected-project copy | ACCEPT | 1,375/1,375 byte-identical, zero mismatches. |
| H terminal status | ACCEPT | `FAIL / FAST_ROUTE_GATE / TEST_DRIVER`. |
| V5 candidate selection | ACCEPT AS COMPLETED FAILURE | Performed under exact Godot; 3/3 valid FAIL/1; no candidate selected. |
| V5 simultaneous throttle/full-brake feasibility | REJECT AS ACTIVE LAW | H traces show speed rising under full brake plus fixed throttle floors; containment aggressiveness was not monotonic. |
| A1 11 m limit / fast-distance contract | PRESERVE | All three V5 candidates exceeded the fast-distance requirement, so later decisive slowing is compatible with unchanged A1. |
| Fourth V5 candidate | REJECT | H falsifies the shared structure; do not tune the same law again. |
| V6 successor | AUTHORIZE BOUNDED TEST | New algorithm `DZP1A_DECEL_CONSTRAINED_THRUST_VECTOR_V1` with conservative net-deceleration constraint and 12-candidate factorial A1 study. |
| World / movement / thresholds | FROZEN | No change authorized. |
| Human World Gate / P1B | LOCKED | Human `NOT PERFORMED`; P1B frozen. |
