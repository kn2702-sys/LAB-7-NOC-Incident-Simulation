# L1 Runbook: the incident workflow

This is the standard L1 process. Every incident in `incidents/` follows it;
INC-001 shows it step-by-step against a real Sev1.

## The 11 steps

1. **Acknowledge the alert.** Ack in the NMS, open a ticket, announce in
   #noc-ops. An unacked alert is an incident nobody owns.
2. **Check scope.** One user? One VLAN? One site? Everything? Scope decides
   severity and where you look. `Scope wrong = investigation wrong.`
3. **Ping the gateway.** From the affected side, can you reach the first
   hop? This splits "local problem" from "beyond the gateway" in seconds.
4. **Check interface.** `show ip interface brief`, `show interfaces`:
   up/up? Errors incrementing? Duplex/speed sane?
5. **Check routing.** `show ip route`: does a route to the destination
   exist, and does it point the right way? A correct route rules out a
   whole class of theories.
6. **Check upstream.** If local is clean, look past your boundary: ISP
   status, carrier tickets, peer reachability.
7. **Identify probable cause.** State it as a hypothesis tied to evidence
   ("CRC errors + collisions = duplex mismatch"), not a guess.
8. **Restore service.** Fix or work around (failover counts as restore).
   Prefer the *reversible* fix first.
9. **Verify.** Same symptoms re-tested + monitoring green + user
   confirmation. "I think it's fixed" is not verification.
10. **Document.** The ticket is the product. Future-you (and the next L1)
    will thank present-you.
11. **Escalate if necessary.** Escalation is not failure — it's the process
    working. Escalate with evidence and what's been ruled out, never with
    "it's broken, please help."

## The habits that separate L1s

- **Work the path in order.** Random checks waste the golden first 15
  minutes. The order above is deliberate: each step rules out a layer.
- **Change one thing, then re-test.** Two simultaneous changes = you
  learned nothing.
- **Counters are evidence.** "Show me the incrementing counter" beats
  every theory. `show interfaces`, `show access-lists`, DHCP pool stats —
  numbers first.
- **Know the difference between down, degraded, and slow** — they have
  different signatures (no response vs errors vs delay) and different
  suspect lists.
- **Write the ticket like the next shift is reading it** — because they are.
