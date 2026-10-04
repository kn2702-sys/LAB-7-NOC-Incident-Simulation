# INC-003 — High packet loss to branch

**Incident ID:** INC-003
**Severity:** Sev 2 (degraded)
**Start Time:** 2026-09-20 14:15 IST
**Detection:** NMS latency/loss probe to branch crossed threshold (35% loss); VoIP complaints from Pune ("choppy audio")
**Impact:** Branch application sessions dropping, VoIP unusable, file transfers crawling. Link up, but barely usable.
**Symptoms:**
- `ping 10.1.10.10` from HQ: ~35% loss, jittery RTT
- Loss persists across multiple destinations in 10.1.10.0/24 (not one host)
- No loss HQ-internal (VLAN 10 ↔ VLAN 20 clean)

## Investigation

1. Scoped it: loss only on paths crossing the WAN link → problem is on the HQ-Edge ↔ ISP segment, not the LANs.
2. `show interfaces GigabitEthernet0/0/1` on HQ-Edge: **input errors and CRC errors incrementing**, collisions counter moving. On a full-duplex fiber/copper link, collisions should be *zero* — that's the tell.
3. Checked negotiated parameters: HQ-Edge side `Full-duplex, 1000Mb/s`; ISP side `Half-duplex, 1000Mb/s`. **Duplex mismatch.**
4. Change history: a maintenance window last night replaced the ISP handoff switch; the new device came up hardcoded half-duplex while our side auto-negotiated to full.

## Root Cause

Duplex mismatch on the WAN handoff after third-party maintenance — HQ-Edge at full duplex, ISP device at half duplex. Each side's transmissions collide with the other's, producing CRC errors and ~35% effective loss. (Full-duplex doesn't do carrier-sense; half-duplex does — they fundamentally disagree about when it's safe to talk.)

## Resolution

- Coordinated with ISP NOC: set their side to auto-negotiation; both ends came up Full/1000
- Verified counters stopped incrementing: `clear counters` then re-checked after 10 min — zero new errors

## Verification

- Loss probe to branch: 0% over 30 min; RTT stable
- VoIP test call Pune ↔ HQ: clean audio
- `show interfaces` error counters flat

## Preventive Action

- Standard: **auto-negotiation everywhere** unless both ends are explicitly hardcoded as a pair — added to the interface config standard
- NMS now alerts on interface error-counter *rate*, not just up/down (this would have paged at 14:16, not after user complaints)
- Require post-maintenance interface verification (`show interfaces status` both ends) in the change close-out

## Escalation

- ISP NOC: to change their duplex setting (their device, their change)
- L2: reviewed and approved the interface standard update
