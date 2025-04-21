# DNS Command and Control Covert Channel  
**By: Gavin Hunsinger**

This repository includes the code and configuration files for a DNS covert channel that allows a DNS server to use TXT resource records to execute commands on a client device and receive responses.

---

## Client Files

### covert_channel_service  
**Location:** `/etc/systemd/system/`  
A systemd unit file that ensures the Python script runs at system startup with network dependencies and automatic restarts for persistence.  
This service executes `covert_execution.py`.

### covert_execution.py  
**Location:** `/opt/covert_channel/`  
The client-side Python script that:
- Resolves DNS TXT records from the server.
- Decodes and executes received commands.
- Sends the base64-encoded output back by updating a DNS resource record (`Response2`).

### resolv.conf  
**Location:** `/etc/`  
Custom `resolv.conf` used to point the client DNS resolution toward the controlled DNS server.

---

## Server Files

### covert_commander.py  
**Location:** `/home/user/`  
A command-and-control script that:
- Accepts command input from the operator.
- Base64 encodes the command and updates the `CovertMessage2` TXT resource record using the `dns` module (`update`, `query`, `resolver`).
- Clears the record after update to prevent re-execution.
- Waits 10 seconds for the response via the `Response2` record, decodes it, and displays the output.

### named.conf.local  
**Location:** `/etc/bind/`  
- Defines the forward and reverse lookup zones.  
- Allows any host to perform dynamic updates in the forward zone, enabling live command injection and response retrieval.

### named.conf.options  
**Location:** `/etc/bind/`  
- Specifies the authoritative address space for the domain.  
- Defines upstream DNS forwarders, enables recursion, and sets the port for the DNS server to listen on.

### research.net (Forward Lookup Zone)  
**Location:** `/etc/bind/research/`  
- Contains `A` records for the honest and test clients.  
- Includes **base64-encoded TXT records**:  
  - `CovertMessage1`: Sends an initial `nslookup` command to the client.  
  - `CovertMessage2`: Delivers commands dynamically from server to client.  
  - `Response2`: Used by the client to send command output back to the server.

### research.net.rev (Reverse Lookup Zone)  
**Location:** `/etc/bind/research/`  
- Contains reverse DNS mappings for IP-to-hostname resolution.

---
