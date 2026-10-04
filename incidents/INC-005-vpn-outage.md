# INC-005 — VPN outage (branch ↔ HQ)

**Incident ID:** INC-005
**Severity:** Sev 1 (branch cut off from HQ apps)
**Start Time:** 2026-09-25 08:05 IST
**Detection:** NMS VPN tunnel monitor red; branch users: "can't open HQ applications" (note: underlay ping to branch still worked — see below)
**Impact:** All branch-to-HQ application traffic down. (Ties directly to Lab 5's concepts — this is that lab in production.)
**Symptoms:**
- `ping 10.1.10.10` from HQ: OK (underlay/routing fine!)
- But HQ app traffic to branch fails; `show crypto isakmp sa` on HQ-Edge: **empty** — no Phase 1 SA
- Key discriminator: underlay healthy + no SA = control-plane (VPN) problem, not a network problem

## Investigation

1. Confirmed underlay: `ping` to the VPN peer's public IP OK, `traceroute` clean → not INC-001.
2. `show crypto isakmp sa` → empty; `show crypto ipsec sa` → empty. Tunnel never forms.
3. Compared Phase 1 proposals both ends: HQ-Edge offered AES/SHA/DH2/lifetime 86400; branch end showed **lifetime 3600** — mismatch.
4. Change history: HQ firewall firmware upgrade over the weekend reset the IKE policy to vendor defaults (lifetime 3600); the branch device kept the old agreed value.
5. Also verified PSK and peer IPs matched (they did) — the *only* divergence was the lifetime.

## Root Cause

Firmware upgrade on the HQ firewall reset the IKE Phase 1 lifetime to the vendor default, breaking proposal agreement with the branch end. Phase 1 could never complete, so no tunnel formed — while the underlay stayed perfectly healthy (which is why ping worked and misled the first reporter).

## Resolution

- Aligned the IKE policy on HQ-Edge back to the agreed standard (lifetime 86400, matching the branch)
- Generated interesting traffic (branch user opened the app) → `show crypto isakmp sa` → QM_IDLE; `show crypto ipsec sa` → encaps/decaps moving

## Verification

- Branch users confirmed HQ apps loading
- NMS tunnel monitor green for 24h
- `show crypto ipsec sa` counters stable, no flaps

## Preventive Action

- **Pre/post-upgrade config diff is now mandatory** for any firewall/VPN device change — the diff would have caught the reset instantly
- VPN parameters added to the "golden config" backup taken before every change window
- NMS: tunnel monitor now alerts on *proposal* telemetry where available, not just SA presence

## Escalation

- L2 Network Security: owned the firmware rollback review and the golden-config update
- Vendor TAC: consulted to confirm the default-reset behavior (documented for next upgrade)
