# INC-006 — Interface flapping (HQ distribution uplink)

**Incident ID:** INC-006
**Severity:** Sev 3 (intermittent, brief)
**Start Time:** 2026-09-18 16:40 IST (first flap; pattern continued)
**Detection:** NMS flapping alert — HQ-SW Fa0/24 up/down 6 times in 20 minutes
**Impact:** Intermittent 1–3 minute micro-outages for HQ users each time the uplink dropped; spanning-tree reconvergence each flap. Annoying, not catastrophic — yet.
**Symptoms:**
- NMS: interface state oscillating up/down, roughly every 3–5 minutes
- Users: "network keeps dropping for a minute"
- No errors spike on the router side; issue localized to the switch uplink

## Investigation

1. `show logging` on HQ-SW: `%LINK-3-UPDOWN: Interface FastEthernet0/24, changed state to down` / `...to up`, repeating. Confirmed flapping, not a monitoring artifact.
2. `show interfaces Fa0/24 counters errors`: no CRC storm — clean when up. This pointed *away* from duplex (cf. INC-003) and toward physical layer.
3. Checked the far end (HQ-Edge G0/0/0): its logs showed the same flap timestamps → the link itself, not one device's port logic.
4. Physical inspection: the fiber/copper patch lead on HQ-SW Fa0/24 had a **damaged latch** — the connector wasn't seating firmly; vibration/thermal movement broke contact intermittently. (Dirty connectors cause the same signature; either way, it's the patch lead.)

## Root Cause

Faulty patch lead with a broken retaining latch on the HQ-SW uplink — intermittent physical contact caused the link to flap every few minutes.

## Resolution

- Replaced the patch lead with a tested spare; reseated both ends with an audible click
- Observed for 1 hour: zero flaps in logs

## Verification

- `show logging` clean for 24h; NMS flap alert cleared and stayed clear
- User reports stopped

## Preventive Action

- Keep tested spare patch leads (copper + fiber) in the comms room — this fix took 5 minutes once diagnosed; the diagnosis took 40
- Add "inspect + reseat physical connections" as step 1 of the L1 flapping checklist (before any config theory)
- Fiber/copper inspection (visual + cleaning) added to the quarterly maintenance routine

## Escalation

- None required beyond L1 — resolved within L1 scope. Noted to L2 in the weekly review as a "could have been Sev2" lesson on monitoring flap *frequency*, not just state.
