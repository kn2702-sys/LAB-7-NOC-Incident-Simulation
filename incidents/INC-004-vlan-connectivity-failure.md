# INC-004 — VLAN connectivity failure (VLAN 20)

**Incident ID:** INC-004
**Severity:** Sev 2 (server segment isolated)
**Start Time:** 2026-09-22 10:20 IST
**Detection:** Monitoring: all VLAN 20 checks red; helpdesk: "can't reach the file server / intranet"
**Impact:** HQ server segment (10.0.20.0/24) unreachable from user VLAN — intranet, file shares, internal DNS down for users. Servers themselves healthy.
**Symptoms:**
- PC-HQ1 (VLAN 10) → `ping 10.0.20.53`: 100% loss
- PC-HQ1 → `ping 10.0.10.1` (own gateway): OK; → `ping 8.8.8.8`: OK
- From SRV itself: everything local fine — the segment isn't down, it's *isolated*

## Investigation

1. Scoped it: only *cross-VLAN* to VLAN 20 fails; intra-VLAN 10 fine; server NIC fine → the break is in the VLAN 20 path between HQ-SW and HQ-Edge (the trunk).
2. On HQ-SW: `show vlan brief` → VLAN 20 exists, Fa0/3 in VLAN 20, port up. Switch config looks right.
3. On HQ-SW: `show interfaces trunk` → Fa0/24 trunking, **but VLANs allowed: 1,10** — VLAN 20 missing from the allowed list.
4. Change history: last night's switch maintenance re-applied a "standard" trunk template that only allowed VLANs 1 and 10. VLAN 20 was pruned at the trunk — frames tagged 20 were dropped at Fa0/24.

## Root Cause

VLAN 20 removed from the trunk's allowed-VLAN list during maintenance (template overwrite). The VLAN existed on the switch and the router subinterface was up — but no VLAN 20 frame could cross the trunk, isolating the server segment.

## Resolution

```
configure terminal
interface FastEthernet0/24
 switchport trunk allowed vlan add 20
end
```
- Verified: `show interfaces trunk` → allowed 1,10,20
- Immediate recovery of cross-VLAN traffic

## Verification

- PC-HQ1 → `ping 10.0.20.53` OK; intranet loads; file share accessible
- `traceroute` shows the expected HQ-Edge subinterface hop
- NMS VLAN 20 checks green

## Preventive Action

- Trunk allowed-VLAN lists now managed from the config template repo — no hand-edited trunks; the template includes *all* production VLANs
- Added a post-change check: `show interfaces trunk` output saved to the change record
- NMS: per-VLAN synthetic checks already existed (they caught it) — kept

## Escalation

- L2: reviewed the template fix; no user-facing escalation needed beyond the standard Sev2 notifications
