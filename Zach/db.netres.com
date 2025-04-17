$TTL 86400
@	IN	SOA	ns1.netres.com.	admin.netres.com. (
	2024030601	; Serial
	3600		; Refresh
	1800		; Retry
	604800		; Expire
	86400		; Minimum TTL
)
@	IN	NS	ns1.netres.com.
ns1	IN	A	192.168.243.141
@	IN	A	192.168.243.141
www	IN	A	192.168.243.141
mail	IN	A	192.168.243.141
@	IN	MX 10	mail.netres.com.
txt	IN	TXT	"Test text record"
txt2	IN	TXT	"Here is another record"
txt3	IN	TXT	"Third record different now?"
exfil	IN	NS	localhost
