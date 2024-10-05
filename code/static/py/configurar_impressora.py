from flask import Flask, render_template, request, Blueprint, jsonify, flash
import psycopg2
from static.py.config.db import get_db_connection
from static.py.login_required import login_required

impressora_configurar_bp = Blueprint('impressora_configurar_bp', __name__)

@impressora_configurar_bp.route('/impressora_configurar_popup')
@login_required
def show_popup_impressora():
    # Fetch printers from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, descricao FROM impressora")  # Adjust the SQL query based on your table structure
    printers = cursor.fetchall()
    cursor.close()
    conn.close()
    printer_options = [{'id': printer[0], 'nome': printer[1]} for printer in printers]
    popup_html = render_template('pop-ups/impressora_configurar_popup.html', printer_options=printer_options)
    return jsonify({'popup_html': popup_html, 'printer_options': printer_options})

@impressora_configurar_bp.route('/configurar_impressora', methods=['GET', 'POST'])
@login_required
def configurar_impressora():
    if request.method == 'POST':
        id_impressora = request.form.get('id_impressora')

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update the selected printer to TRUE and all others to FALSE
        try:
            # Set the selected printer to TRUE
            cursor.execute("""
                UPDATE impressora
                SET selecionado = TRUE
                WHERE id = %s
            """, (id_impressora,))

            # Set all other printers to FALSE
            cursor.execute("""
                UPDATE impressora
                SET selecionado = FALSE
                WHERE id != %s
            """, (id_impressora,))

            # Commit the changes
            conn.commit()

            # Optionally: You can add a flash message for success
            flash('Printer selection updated successfully.', 'success')

        except Exception as e:
            # Rollback in case of error
            conn.rollback()
            flash('An error occurred while updating printer selection.', 'error')
            print(e)

        finally:
            cursor.close()
            conn.close()

        # Redirect to the desired view after processing
        return redirect()  # Adjust redirection as needed
