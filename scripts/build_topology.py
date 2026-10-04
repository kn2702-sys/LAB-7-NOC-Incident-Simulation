#!/usr/bin/env python3
"""Build Lab 7's fictional company network (Meridian Logistics Pvt. Ltd).

A single working topology that all 8 incident reports reference:
HQ (Mumbai) with VLANs 10/20 on a router-on-a-stick, a branch office
(Pune) across a simulated WAN cloud, and an ISP transit router.

Usage:
    python3 scripts/build_topology.py

Output:
    Lab-7-Meridian-Corp-Network.pkt
"""
from __future__ import annotations

import sys
from pathlib import Path

PT_CODEC_SRC = Path("/tmp/ctt/src")
LIBRARY_DIR = Path("/tmp/ctt/samples/library")
SKELETON_PKT = Path("/tmp/ctt/samples/template.pkt")

sys.path.insert(0, str(PT_CODEC_SRC))

from pt_codec import Topology  # noqa: E402

OUT_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------

HQ_EDGE_CONFIG = """!
! Meridian Logistics - HQ-Edge (Mumbai HQ internet/WAN edge)
! Router-on-a-stick: G0/0/0.10 = VLAN 10 (users), G0/0/0.20 = VLAN 20 (servers)
!
hostname HQ-Edge
!
no ip domain-lookup
!
interface GigabitEthernet0/0/0
 description *** Trunk to HQ-SW ***
 no shutdown
!
interface GigabitEthernet0/0/0.10
 description *** VLAN 10 - HQ Users 10.0.10.0/24 ***
 encapsulation dot1Q 10
 ip address 10.0.10.1 255.255.255.0
!
interface GigabitEthernet0/0/0.20
 description *** VLAN 20 - HQ Servers 10.0.20.0/24 ***
 encapsulation dot1Q 20
 ip address 10.0.20.1 255.255.255.0
!
interface GigabitEthernet0/0/1
 description *** WAN to ISP 203.0.113.0/30 ***
 ip address 203.0.113.1 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/0/2
 description *** UNUSED ***
 shutdown
!
ip route 10.1.10.0 255.255.255.0 203.0.113.2
ip route 0.0.0.0 0.0.0.0 203.0.113.2
!
end
"""

HQ_SW_CONFIG = """!
! Meridian Logistics - HQ-SW (access switch, VLANs 10 + 20)
!
hostname HQ-SW
!
vlan 10
 name HQ-Users
vlan 20
 name HQ-Servers
!
interface FastEthernet0/1
 description *** PC-HQ1 ***
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
!
interface FastEthernet0/2
 description *** PC-HQ2 ***
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
!
interface FastEthernet0/3
 description *** SRV (DNS + apps) ***
 switchport mode access
 switchport access vlan 20
 spanning-tree portfast
!
interface FastEthernet0/24
 description *** Trunk to HQ-Edge ***
 switchport mode trunk
!
end
"""

ISP_CONFIG = """!
! Meridian Logistics - simulated WAN cloud / ISP transit
!
hostname ISP-Router
!
no ip domain-lookup
!
interface GigabitEthernet0/0/0
 description *** to HQ-Edge 203.0.113.0/30 ***
 ip address 203.0.113.2 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/0/1
 description *** to BR-Router 198.51.100.0/30 ***
 ip address 198.51.100.1 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/0/2
 description *** UNUSED ***
 shutdown
!
ip route 10.0.10.0 255.255.255.0 203.0.113.1
ip route 10.0.20.0 255.255.255.0 203.0.113.1
ip route 10.1.10.0 255.255.255.0 198.51.100.2
!
end
"""

BR_ROUTER_CONFIG = """!
! Meridian Logistics - BR-Router (Pune branch office gateway)
!
hostname BR-Router
!
no ip domain-lookup
!
interface GigabitEthernet0/0/0
 description *** Branch LAN 10.1.10.0/24 ***
 ip address 10.1.10.1 255.255.255.0
 no shutdown
!
interface GigabitEthernet0/0/1
 description *** WAN to ISP 198.51.100.0/30 ***
 ip address 198.51.100.2 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/0/2
 description *** UNUSED ***
 shutdown
!
ip route 10.0.0.0 255.255.0.0 198.51.100.1
!
end
"""

BR_SW_CONFIG = """!
! Meridian Logistics - BR-SW (branch access switch, flat LAN)
!
hostname BR-SW
!
interface FastEthernet0/1
 description *** PC-BR1 ***
 switchport mode access
 spanning-tree portfast
!
interface FastEthernet0/2
 description *** PC-BR2 ***
 switchport mode access
 spanning-tree portfast
!
interface FastEthernet0/24
 description *** Uplink to BR-Router ***
 switchport mode access
!
end
"""


def build() -> Topology:
    t = Topology.open(SKELETON_PKT)
    t.clear()

    # ---- devices ----
    t.add_device_by_model(LIBRARY_DIR, "ISR4331", "HQ-Edge", x=300, y=220)
    t.add_device_by_model(LIBRARY_DIR, "2960-24TT", "HQ-SW", x=300, y=420)
    t.add_device_by_model(LIBRARY_DIR, "ISR4331", "ISP-Router", x=600, y=220)
    t.add_device_by_model(LIBRARY_DIR, "ISR4331", "BR-Router", x=900, y=220)
    t.add_device_by_model(LIBRARY_DIR, "2960-24TT", "BR-SW", x=900, y=420)
    t.add_device_by_model(LIBRARY_DIR, "PC-PT", "PC-HQ1", x=180, y=580)
    t.add_device_by_model(LIBRARY_DIR, "PC-PT", "PC-HQ2", x=320, y=580)
    t.add_device_by_model(LIBRARY_DIR, "Server-PT", "SRV", x=460, y=580)
    t.add_device_by_model(LIBRARY_DIR, "PC-PT", "PC-BR1", x=800, y=580)
    t.add_device_by_model(LIBRARY_DIR, "PC-PT", "PC-BR2", x=1000, y=580)

    # ---- links ----
    t.add_link("HQ-SW", "FastEthernet0/1", "PC-HQ1", "FastEthernet0")
    t.add_link("HQ-SW", "FastEthernet0/2", "PC-HQ2", "FastEthernet0")
    t.add_link("HQ-SW", "FastEthernet0/3", "SRV", "FastEthernet0")
    t.add_link("HQ-SW", "FastEthernet0/24", "HQ-Edge", "GigabitEthernet0/0/0")
    t.add_link("HQ-Edge", "GigabitEthernet0/0/1",
               "ISP-Router", "GigabitEthernet0/0/0",
               cable_type="eCopperCrossOver")
    t.add_link("ISP-Router", "GigabitEthernet0/0/1",
               "BR-Router", "GigabitEthernet0/0/1",
               cable_type="eCopperCrossOver")
    t.add_link("BR-Router", "GigabitEthernet0/0/0", "BR-SW", "FastEthernet0/24")
    t.add_link("BR-SW", "FastEthernet0/1", "PC-BR1", "FastEthernet0")
    t.add_link("BR-SW", "FastEthernet0/2", "PC-BR2", "FastEthernet0")

    # ---- configs ----
    t.set_running_config("HQ-Edge", HQ_EDGE_CONFIG)
    t.set_running_config("HQ-SW", HQ_SW_CONFIG)
    t.set_running_config("ISP-Router", ISP_CONFIG)
    t.set_running_config("BR-Router", BR_ROUTER_CONFIG)
    t.set_running_config("BR-SW", BR_SW_CONFIG)

    # ---- end devices ----
    t.set_pc_network("PC-HQ1", ip="10.0.10.10", mask="255.255.255.0", gateway="10.0.10.1")
    t.set_pc_network("PC-HQ2", ip="10.0.10.11", mask="255.255.255.0", gateway="10.0.10.1")
    t.set_pc_network("SRV", ip="10.0.20.53", mask="255.255.255.0", gateway="10.0.20.1")
    t.set_pc_network("PC-BR1", ip="10.1.10.10", mask="255.255.255.0", gateway="10.1.10.1")
    t.set_pc_network("PC-BR2", ip="10.1.10.11", mask="255.255.255.0", gateway="10.1.10.1")
    return t


def verify(t: Topology) -> None:
    names = {d.name for d in t.list_devices()}
    expected = {"HQ-Edge", "HQ-SW", "ISP-Router", "BR-Router", "BR-SW",
                "PC-HQ1", "PC-HQ2", "SRV", "PC-BR1", "PC-BR2"}
    assert expected <= names, f"missing: {expected - names}"
    assert len(t.list_links()) == 9, f"expected 9 links, got {len(t.list_links())}"
    edge = t.get_running_config("HQ-Edge")
    for needle in ["interface GigabitEthernet0/0/0.10", "encapsulation dot1Q 10",
                   "interface GigabitEthernet0/0/0.20", "encapsulation dot1Q 20",
                   "ip route 10.1.10.0 255.255.255.0 203.0.113.2"]:
        assert needle in edge, f"HQ-Edge missing: {needle!r}"
    sw = t.get_running_config("HQ-SW")
    assert "switchport mode trunk" in sw and "switchport access vlan 20" in sw
    assert "ip route 10.0.0.0 255.255.0.0 198.51.100.1" in t.get_running_config("BR-Router")
    assert t.get_pc_network("SRV")["ip"] == "10.0.20.53"
    assert t.get_pc_network("PC-BR1")["gateway"] == "10.1.10.1"
    print(f"  verify: OK ({len(t.list_devices())} devices, {len(t.list_links())} links)")


def main() -> int:
    t = build()
    verify(t)
    out = OUT_DIR / "Lab-7-Meridian-Corp-Network.pkt"
    t.save(out)
    print(f"  saved {out} ({out.stat().st_size} bytes)")
    probe = Topology.open(out)
    assert len(probe.list_devices()) == 10 and len(probe.list_links()) == 9
    print("round-trip decode: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
