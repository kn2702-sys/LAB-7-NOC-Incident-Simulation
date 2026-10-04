# INC-002 — DNS outage

**Incident ID:** INC-002
**Severity:** Sev 1 (name resolution down = everything "down")
**Start Time:** 2026-09-15 11:05 IST
**Detection:** Helpdesk ticket surge ("internet not working") + NMS synthetic DNS check failing for `intranet.meridian.local`
**Impact:** All HQ users — internal apps, intranet, and internet browsing by name all failing. IP-based connectivity fine.
**Symptoms:**
- `nslookup intranet.meridian.local` → timeout
- `ping 8.8.8.8` works; `ping google.com` fails ("could not resolve")
- Classic split: **IPs work, names don't** → DNS, not the network

## Investigation

1. From a user PC: `nslookup` pointed at the corporate DNS `10.0.20.53` — timed out. Switched test to `8.8.8.8` → resolved fine. So the problem is *our* DNS server, not DNS as a concept.
2. Pinged `10.0.20.53` → OK. Server is up; the *service* is not.
3. Checked the server: the `named` (BIND) service was stopped. Attempted restart → failed immediately.
4. Checked logs: `named` failed to start after the 10:30 change window — a zone file edit introduced a syntax error (missing closing parenthesis in the forward zone).
5. Confirmed with the change record: a junior admin pushed the zone edit without running a config check.

## Root Cause

BIND failed to start due to a zone file syntax error introduced during a routine DNS change. The change had no pre-validation, and there was no service-level monitoring on the DNS *process* — only on the server's ping.

## Resolution

- Rolled the zone file back to the pre-change version from backup
- Ran `named-checkconf` + `named-checkzone` → clean
- Restarted `named`; verified `nslookup`/`dig` for internal + external names from multiple VLANs

## Verification

- NMS synthetic DNS check green
- Spot-checked 5 users across VLAN 10/20: intranet + internet names resolving
- `dig` response times normal (~5ms internal)

## Preventive Action

- **Mandatory `named-checkconf`/`named-checkzone` before any DNS change** — added to the change template as a checklist item
- Added process-level monitoring: alert if port 53/TCP+UDP stops responding, not just ping
- Deployed a secondary DNS (10.0.20.54) so a single named failure can't take down resolution — clients now get both via DHCP

## Escalation

- L2 / Server team: owned the zone fix and the secondary DNS build
- Change manager: flagged the unvalidated change for process review
