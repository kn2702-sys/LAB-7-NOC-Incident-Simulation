# INC-008 — DHCP exhaustion

**Incident ID:** INC-008
**Severity:** Sev 2 (new devices can't onboard)
**Start Time:** 2026-09-29 09:10 IST
**Detection:** Helpdesk: "new laptops can't get on the network" (Monday morning, post-weekend-hires batch)
**Impact:** New/reconnecting devices in VLAN 10 fail to obtain an IP — no network access. Existing connected users unaffected (they hold leases).
**Symptoms:**
- Affected PC: APIPA address (169.254.x.x) — the universal "DHCP gave me nothing" signal
- `ipconfig /renew` → timeout; Wireshark (cf. Lab 6) would show Discover with **no Offer**
- Existing users fine → server up, scope exists, but nothing left to give

## Investigation

1. APIPA + Discover-without-Offer = the server is reachable but has no addresses (if the server were down, we'd also check relay/helper — but the pattern here is specific).
2. On the DHCP server: `show ip dhcp pool` → **0 free addresses** out of a /24 (254). Pool exhausted.
3. `show ip dhcp binding`: hundreds of bindings, many to devices not seen in days — the lease time was **7 days**, so every transient device (guests, phones, short-stay contractors) squatted an address for a week.
4. Trigger: weekend hiring batch + BYOD influx on Monday morning consumed the last free leases.

## Root Cause

DHCP pool exhaustion: a /24 scope with a 7-day lease time, under-counted device growth (BYOD). Stale leases for long-gone devices occupied the pool; legitimate new devices got nothing.

## Resolution

- Immediate: reduced lease time to 8 hours and cleared stale bindings (`clear ip dhcp binding *` for expired) → ~60 addresses freed within the hour as short leases cycled
- Same day: expanded the scope — added a second /24 for VLAN 10 devices (10.0.11.0/24) via a superscope; updated the helper/DHCP config

## Verification

- New laptops obtaining IPs within seconds; `ipconfig` shows proper 10.0.x.x addresses
- Pool utilization back to ~55%
- Monday-morning re-test with 10 fresh devices: all leased cleanly

## Preventive Action

- **DHCP utilization alert at 80%** (this incident was 100% preventable with a threshold alert)
- Lease times by segment: 8h for user/BYOD VLANs, 24h+ only for infrastructure
- Quarterly capacity review of all scopes against headcount/device trends

## Escalation

- L2: approved the scope expansion (addressing change)
- IT management: FYI on the BYOD growth trend for the next network review
