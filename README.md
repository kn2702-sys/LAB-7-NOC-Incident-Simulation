# Lab 7: NOC Incident Simulation

This is not a student lab. It's a month in the life of an L1 network
engineer: a fictional company (**Meridian Logistics Pvt. Ltd.**), a real
Packet Tracer topology of its network, and **8 incident tickets** written
exactly the way a NOC writes them — each with symptoms, a worked
investigation, root cause, resolution, verification, and preventive action.

> **Résumé line:** *Simulated NOC L1 operations for a fictional enterprise
> network — triaged and documented 8 incidents (outages, VPN, VLAN, DHCP,
> latency) following ITIL-style incident workflow with RCAs.*

**Lab series:** [Lab 1](https://github.com/kn2702-sys/enterprise-vlan-lab) · [Lab 2](https://github.com/kn2702-sys/dhcp-dns-failure-lab) · [Lab 3](https://github.com/kn2702-sys/LAB-3-Multi-Router-OSPF-Network) · [Lab 4](https://github.com/kn2702-sys/LAB-4-ACL-NAT-Internet-Edge) · [Lab 5](https://github.com/kn2702-sys/LAB-5-Site-to-Site-VPN-Firewall) · [Lab 6](https://github.com/kn2702-sys/LAB-6-Wireshark-NOC-Troubleshooting) · **Lab 7** · [Lab 8](https://github.com/kn2702-sys/LAB-8-AWS-VPC-Networking)

## Repository contents

```
Lab-7-Meridian-Corp-Network.pkt   # the company network (open in Packet Tracer)
incidents/
  INC-001-branch-router-unreachable.md   # Sev1 - the full 11-step L1 workflow
  INC-002-dns-outage.md                  # Sev1
  INC-003-high-packet-loss.md            # Sev2 - duplex mismatch
  INC-004-vlan-connectivity-failure.md   # Sev2 - trunk pruning
  INC-005-vpn-outage.md                  # Sev1 - IKE proposal mismatch
  INC-006-interface-flapping.md          # Sev3 - bad patch lead
  INC-007-high-latency.md                # Sev2 - uplink saturation
  INC-008-dhcp-exhaustion.md             # Sev2 - pool depletion
docs/
  COMPANY-NETWORK.md   # the fictional company: topology, addressing, monitoring, escalation matrix
  L1-RUNBOOK.md        # the 11-step incident workflow + L1 habits
scripts/
  build_topology.py    # regenerates the .pkt
```

## The network (open the .pkt alongside the tickets)

HQ Mumbai (VLAN 10 users `10.0.10.0/24`, VLAN 20 servers `10.0.20.0/24` on a
router-on-a-stick) → ISP transit → Branch Pune (`10.1.10.0/24`). Full
addressing, monitoring setup, severity definitions and escalation matrix in
[docs/COMPANY-NETWORK.md](docs/COMPANY-NETWORK.md).

## How to use this (interview prep)

1. Read [docs/L1-RUNBOOK.md](docs/L1-RUNBOOK.md) — the 11-step workflow.
2. Pick an incident. Read only down to **Symptoms**, then close the file
   and work it yourself on the `.pkt` topology.
3. Compare with the ticket's Investigation. Note where you diverged —
   that's the gap to close.
4. Read the **Preventive Action** of each ticket and ask yourself: "what
   monitoring would have caught this before users did?" That question is
   pure L1-to-L2 thinking.

Suggested order: 001 (the method) → 004 → 003 → 008 → 007 → 002 → 005 → 006.

## The incident index

| ID | Title | Sev | The lesson |
|----|-------|-----|------------|
| 001 | Branch router unreachable | 1 | Scope first; verify local before blaming the carrier |
| 002 | DNS outage | 1 | IPs work + names don't = DNS; validate changes |
| 003 | High packet loss | 2 | CRC + collisions = duplex mismatch; counters are evidence |
| 004 | VLAN connectivity failure | 2 | Trunk allowed-VLAN lists; templates over hand-edits |
| 005 | VPN outage | 1 | Underlay OK + no SA = control plane; diff configs after upgrades |
| 006 | Interface flapping | 3 | Physical layer first; keep spare patch leads |
| 007 | High latency | 2 | 0% loss + high RTT = congestion; alert at 80%, QoS voice |
| 008 | DHCP exhaustion | 2 | APIPA = no Offer; alert pool utilization, right-size leases |

## Requirements

- Cisco Packet Tracer 8.2.1+ for the topology.
- The incident tickets need nothing but a reader — that's the point. The
  paperwork *is* the deliverable in incident management.
