# INC-007 — High latency to cloud applications

**Incident ID:** INC-007
**Severity:** Sev 2 (degraded, business hours)
**Start Time:** 2026-09-26 10:30 IST
**Detection:** User complaints ("everything is slow") + NMS latency probe to cloud apps: 300ms+ vs 40ms baseline
**Impact:** All cloud/SaaS apps sluggish for HQ users during business hours; VoIP quality dipping. No packet loss — just slow.
**Symptoms:**
- `ping` to cloud: high RTT, **0% loss** (contrast with INC-003's loss)
- `traceroute`: latency jumps *at the ISP hop* and stays high after — the delay is introduced at/after our edge
- Internal (VLAN 10 ↔ 20) latency normal → not the LAN

## Investigation

1. Ruled out the LAN (internal RTT normal) and ruled out loss (0% — so not a duplex/physical issue).
2. `show interfaces GigabitEthernet0/0/1` on HQ-Edge: **output drops incrementing**, output queue filling — the WAN uplink is saturated *outbound*.
3. Top talkers (NetFlow / `show ip flow top-talkers`): a single internal host pushing a massive outbound sync to cloud storage — an unsanctioned full-drive backup started at 10:15, consuming ~95% of uplink.
4. Correlated: latency spike began within minutes of the sync start; business-hours overlap is the entire problem.

## Root Cause

Unsanctioned bulk data sync saturated the internet uplink during business hours. Queuing delay on the congested egress interface added ~260ms to every packet — high latency with zero loss, the classic congestion signature.

## Resolution

- Immediately rate-limited the syncing host at the edge (temporary ACL rate-limit) → latency dropped to ~45ms within minutes
- Rescheduled the backup to the 22:00–06:00 window with the data owner
- Applied a QoS policy: VoIP EF marked traffic priority-queued so voice survives the next saturation event

## Verification

- NMS latency probe back to ~40ms baseline, sustained through the afternoon
- Test VoIP call: clean
- Backup completed overnight without impacting the morning peak

## Preventive Action

- **Bandwidth utilization alert at 80%** on the WAN uplink (we only had up/down before — we were blind to saturation)
- QoS policy now standard on the edge: voice priority, bulk-data scavenger class
- Backup/sync windows documented and approved — no bulk transfers 08:00–20:00 without change approval

## Escalation

- L2: approved the QoS policy change
- The data owner's manager: briefed on the business-hours transfer policy (no blame — no policy had existed)
