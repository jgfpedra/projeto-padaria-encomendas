import socket
from static.py.config.db import get_db_connection
from datetime import datetime

def print_receipt(receipt_content):
    host = "192.168.0.20"  # Your printer's IP
    port = 9100  # Common port for ESC/POS printers

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            
            # Split the receipt into lines
            lines = receipt_content.split('\n')
            for line in lines:
                # Send each line followed by a newline
                s.sendall(line.encode() + b'\n')  # Send each line
            
            # Add 10 new lines
            for _ in range(10):
                s.sendall(b'\n')  # Sending 10 newlines

            # Send cut command at the end
            s.sendall(b'\x1D\x69\x00')  # Cut command for ESC/POS
            print("Receipt printed successfully.")
    except Exception as e:
        print(f"An error occurred while printing: {e}")

def format_receipt_encomenda(conn, conn_vr, encomenda_id):
    # Create a formatted string for the receipt
    receipt_lines = []
    receipt_lines.append("----- TESTE - DESCONSIDERAR -----")
    
    # Get today's date
    data = datetime.now().date()

    with conn.cursor() as cur:
        # Fetch order data
        cur.execute("SELECT * FROM encomenda WHERE encomenda_id = %s AND data_criacao::date = %s",
                    (encomenda_id, data))
        encomenda_data = cur.fetchone()
        
        if not encomenda_data:
            return "Encomenda not found."
        
        # Determine bakery name
        if encomenda_data[5] == 1:
            receipt_lines.append("PANIFICADORA PAO DO CAMBUI")
        else:
            receipt_lines.append("PANIFICADORA PAO DA PRIMAVERA")

        receipt_lines.append("-------------------")
        receipt_lines.append(f"DATA: {encomenda_data[12]}")
        receipt_lines.append(f"HORA: {encomenda_data[13]}")
        receipt_lines.append(f"PEDIDO: {encomenda_data[11]}")
        receipt_lines.append("-------------------")
        receipt_lines.append(f"DATA ENCOMENDA: {encomenda_data[2]}")
        receipt_lines.append(f"HORA ENCOMENDA: {encomenda_data[3]}")
        receipt_lines.append("---------SEM VALOR FISCAL----------")

        # Fetch items data
        cur.execute("SELECT * FROM itens_encomenda WHERE id_encomenda = %s AND data_criacao = %s", 
                    (encomenda_data[11], encomenda_data[12]))
        itens_data = cur.fetchall()

        with conn_vr.cursor() as cur_vr:
            for item in itens_data:
                item_id = item[2]
                quantity = item[3]
                cur_vr.execute("SELECT id, descricaoreduzida FROM produto WHERE id = %s", (item_id,))
                product_info = cur_vr.fetchone()

                # Append product info to receipt
                receipt_lines.append(f"{product_info[0]} - {product_info[1]}")
                receipt_lines.append(f"{quantity} - x{item[6]} = {item[5]}")
                receipt_lines.append("\n")

        receipt_lines.append("-------------------")
        receipt_lines.append(f"ENTREGA: {encomenda_data[7]}")
        receipt_lines.append(f"DESCONTO: {encomenda_data[8]}")
        receipt_lines.append(f"TOTAL: {encomenda_data[9]}")
        receipt_lines.append("-------------------")

        # Fetch client data
        cur.execute("SELECT * FROM cliente WHERE id = %s", (int(encomenda_data[6]),))
        client_data = cur.fetchone()

        if client_data:
            receipt_lines.append(f"ENDERECO: {client_data[2]}")
            receipt_lines.append(f"NUM: {client_data[3]}")
            receipt_lines.append(f"BAIRRO: {client_data[4]}")
            receipt_lines.append(f"COMPLEMENTO: {client_data[5]}")
        
            cur.execute("SELECT * FROM telefone WHERE cliente_id = %s", (int(encomenda_data[6]),))
            telefones = cur.fetchall()
            telefone_line = []

            for count, telefone in enumerate(telefones):
                if count == 0:
                    telefone_line.append(f"TELEFONE: {telefone[2]}")
                else:
                    telefone_line.append(telefone[2])  # Append subsequent phone numbers

            # Join the lines to create a single string if needed
            receipt_lines.append(", ".join(telefone_line))
            receipt_lines.append("OBS: " + client_data[2])
        
        receipt_lines.append("-------------------")

    return "\n".join(receipt_lines)
