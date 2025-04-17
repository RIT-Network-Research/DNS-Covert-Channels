$ORIGIN .
$TTL 86400	; 1 day
c2.netres.com		IN SOA	ns1.c2.netres.com. admin.c2.netres.com. (
				2024030615 ; serial
				3600       ; refresh (1 hour)
				1800       ; retry (30 minutes)
				604800     ; expire (1 week)
				86400      ; minimum (1 day)
				)
			NS	ns1.c2.netres.com.
$ORIGIN c2.netres.com.
$TTL 60	; 1 minute
message			TXT	""
$TTL 86400	; 1 day
ns1			A	192.168.243.141
$TTL 60	; 1 minute
thing			TXT	"what about this"
