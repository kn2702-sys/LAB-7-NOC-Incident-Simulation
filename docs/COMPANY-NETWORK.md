# Meridian Logistics Pvt. Ltd. — Network Dossier (fictional)

> Everything here is fictional and built for training. Any resemblance to
> real companies is coincidental. The incidents in `incidents/` all take
> place on this network — open `Lab-7-Meridian-Corp-Network.pkt` in Packet
> Tracer to walk them.

## The company

Meridian Logistics: ~200 HQ staff (Mumbai) + ~35 branch staff (Pune).
Business hours 09:00–18:00 IST. The NOC watches this network 24×7; L1
owns detection → diagnosis → restore-or-escalate.

## Topology

```
HQ Mumbai                          WAN cloud                    Branch Pune
10.0.10.0/24 (VLAN 10 users)                                   10.1.10.0/24
10.0.20.0/24 (VLAN 20 servers)
  PC-HQ1 .10                                                     PC-BR1 .10
  PC-HQ2 .11                                                     PC-BR2 .11
  SRV    .53  (DNS + intranet)
      \                                                            /
    [HQ-SW] (Fa0/24 trunk)                        [BR-SW] (Fa0/24 access)
       | G0/0/0 (router-on-a-stick)                  | G0/0/0 10.1.10.1
    [HQ-Edge]                                    [BR-Router]
  .10→10.0.10.1  .20→10.0.20.1                       |
       | G0/0/1 203.0.113.1                           | G0/0/1 198.51.100.2
       +=========== [ISP-Router] ===========+
              .2 (203.0.113.0/30)   .1 (198.51.100.0/30)
```

## Addressing summary

| Segment | Network | Gateway | Notes |
|---|---|---|---|
| HQ Users (VLAN 10) | 10.0.10.0/24 | 10.0.10.1 (G0/0/0.10) | DHCP pool .100–.200, 8h lease |
| HQ Servers (VLAN 20) | 10.0.20.0/24 | 10.0.20.1 (G0/0/0.20) | SRV .53 = DNS + intranet (static) |
| HQ→ISP WAN | 203.0.113.0/30 | — | HQ-Edge .1 ↔ ISP .2 |
| ISP→Branch WAN | 198.51.100.0/30 | — | ISP .1 ↔ BR-Router .2 |
| Branch LAN | 10.1.10.0/24 | 10.1.10.1 | DHCP pool .100–.200, 8h lease |

Static routing: HQ-Edge → `10.1.10.0/24 via 203.0.113.2`; BR-Router →
`10.0.0.0/16 via 198.51.100.1`; ISP has return routes for all LANs.

## Monitoring (what pages L1)

- ICMP poll every 60s on all router/switch/SRV addresses (3 missed = down)
- Interface state + error-counter rate on WAN links
- Synthetic checks: DNS resolution, intranet HTTP, VPN SA presence
- Latency/loss probes HQ→branch and HQ→cloud
- DHCP pool utilization (alert at 80%), WAN bandwidth (alert at 80%)

## Severity definitions

| Sev | Meaning | Comms |
|---|---|---|
| **Sev 1** | Service/site down | #noc-ops + IT head + affected manager, updates hourly |
| **Sev 2** | Degraded / partial | #noc-ops, updates every 2h |
| **Sev 3** | Minor / intermittent | Ticket + weekly review |

## Escalation matrix

| To | When | Contact of record |
|---|---|---|
| L2 Network Engineering | Beyond L1 scope, config changes, vendor bugs | noc-l2@meridian.local |
| Server team | OS/service issues (DNS, DHCP, apps) | srv-team@meridian.local |
| ISP NOC | Carrier circuit issues | Circuit IDs in the ticket template |
| Facilities | Power/cooling at any site | facilities@meridian.local |
| IT Head | Every Sev 1 | Per the Sev1 comms matrix |

## Key numbers (fictional, for realism)

- ISP NOC: 1800-xxx-xxxx, circuit IDs HQ-WAN-001 / BR-WAN-002
- Branch manager (Pune): on the Sev1 call list
- Change window: Sundays 02:00–06:00 IST
