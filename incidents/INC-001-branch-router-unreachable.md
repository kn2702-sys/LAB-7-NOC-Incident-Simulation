# INC-001 — Branch router unreachable

**Incident ID:** INC-001
**Severity:** Sev 1 (site down)
**Start Time:** 2026-09-28 09:42 IST
**Detection:** Monitoring alert — `BR-Router` unreachable (ICMP poll failed 3/3); branch users calling helpdesk within minutes
**Impact:** Pune branch office fully offline — ~35 users unable to reach HQ applications, VoIP, or internet (branch backhauls via HQ)
**Symptoms:**
- NMS shows `BR-Router` (198.51.100.2) down; last response 09:41 IST
- 100% packet loss from HQ-Edge to 198.51.100.2 and to 10.1.10.0/24
- Branch users: "internet not working," phones dead

## Investigation (L1 workflow, step by step)

**1. Acknowledge the alert.** Acked in NMS at 09:44, opened this ticket, posted in #noc-ops: "INC-001 Sev1 — Pune branch down, investigating."

**2. Check scope.** Is it one user, one VLAN, or the site? All branch subnets (10.1.10.0/24) unreachable + router itself unreachable = site-level. HQ unaffected (VLAN 10/20 hosts fine).

**3. Ping the gateway (from the branch side's perspective).** From HQ-Edge: `ping 198.51.100.2` → 100% loss. `ping 198.51.100.1` (ISP side) → OK. So the failure is at or beyond the ISP handoff toward the branch.

**4. Check interface.** `show ip interface brief` on HQ-Edge: G0/0/1 up/up. On ISP-Router: G0/0/1 (toward branch) shows **up/down** — line protocol down. Physical/link issue on the branch-facing side.

**5. Check routing.** `show ip route` on HQ-Edge still has `10.1.10.0/24 via 203.0.113.2` — routing is correct; this is not a routing problem. (If the route were missing, traffic would die differently — with "unreachable," not silence.)

**6. Check upstream.** Called the ISP NOC (circuit ID on file in the dossier): they confirmed a fiber cut on the last-mile segment to the Pune PoP at ~09:40 IST. Their ETR: 4 hours.

**7. Identify probable cause.** Carrier fiber cut — outside our boundary, confirmed by the carrier. Not our router, not our config.

**8. Restore service.** No local fix possible for a cut fiber. Options weighed: (a) wait for carrier, (b) fail branch to the LTE backup link. The branch LTE backup was provisioned for exactly this — activated the backup APN profile on BR-Router via its console-over-LTE OOB (pre-staged config), branch came up on reduced bandwidth at 10:25 IST.

**9. Verify.** From HQ-Edge: `ping 10.1.10.10` OK (higher latency, acceptable). Branch user confirmed apps loading; VoIP re-registered. Monitoring cleared the down alert, opened a degraded-service note.

**10. Document.** This ticket + updated the carrier ticket reference + noted the LTE failover in the branch dossier.

**11. Escalate.** Escalated to L2 (to own the carrier chase and the LTE data usage) and notified the branch manager + IT head per the Sev1 comms matrix. Carrier restored the fiber at 13:50 IST; L2 failed traffic back and closed the loop.

## Root Cause

Carrier fiber cut on the ISP last-mile to the Pune branch (outside Meridian's boundary). Local interfaces, routing, and configs were all healthy — verified before escalating, so no time was lost chasing our own gear.

## Resolution

- Immediate: failed the branch over to the pre-provisioned LTE backup link (10:25 IST, ~45 min after detection).
- Final: carrier spliced the fiber; primary circuit restored 13:50 IST; traffic failed back after L2 verification.

## Verification

- `ping`/`traceroute` HQ → branch LAN clean on both primary (post-restore) and backup paths
- User acceptance: branch confirmed applications + VoIP working
- Monitoring: all branch checks green for 24h before ticket closure

## Preventive Action

- Keep the LTE backup config pre-staged and test failover quarterly (this incident proved its worth — formalize the drill).
- Add a carrier-diversity review for single-homed branches to the annual network review.
- Ensure circuit IDs + ISP NOC numbers are in the dossier (they were — it saved 20 minutes).

## Escalation

- L2 Network Engineering: owned carrier ticket + failback
- IT Head & Branch Manager: Sev1 comms at 10:00 and 14:00 IST
- ISP: carrier ticket #ISP-88412
