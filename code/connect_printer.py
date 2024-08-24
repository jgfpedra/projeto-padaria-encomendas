import socket

# Printer network settings
PRINTER_IP = '192.168.0.66'
PRINTER_PORT = 9100  # Standard port for ESC/POS printers over TCP/IP

def send_to_printer(data):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((PRINTER_IP, PRINTER_PORT))
            s.sendall(data)
            s.close()
    except Exception as e:
        print(f"Error communicating with printer: {e}")

def print_test_page():
    ESC = b'\x1B'
    GS = b'\x1D'
    LF = b'\x0A'
    
    # Commands to initialize the printer and print a test page
    init_printer = ESC + b'@'
    cut_paper = ESC + b'V' + b'\x00'

    # Create test page content
    test_content = (
        ESC + b'!' + b'\x1B' + b'\x21' + b'\x08' +  # Bold text
        b'Test Page\n' +
        ESC + b'!' + b'\x00' +  # Normal text
        b'Printer Test\n' +
        b'Line 1\n' +
        b'Line 2\n' +
        LF +  # Print line feed
        cut_paper
    )
    
    # Send commands to the printer
    send_to_printer(init_printer)
    send_to_printer(test_content)

if __name__ == '__main__':
    print_test_page()
