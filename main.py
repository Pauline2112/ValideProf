from flask import Flask, jsonify, request, render_template
import threading

app = Flask(__name__)

# État initial : "pending"
validation_status = "pending"

# Verrou pour éviter les conflits lors de la mise à jour de l'état
lock = threading.Lock()


@app.route('/')
def home():
    """
    Route principale qui affiche l'interface web.
    """
    return render_template('index.html')  # Renvoie le fichier index.html


@app.route('/validate', methods=['GET'])
def validate():
    """
    Route GET pour récupérer l'état actuel.
    L'état est réinitialisé après un délai de 5 secondes.
    """
    global validation_status

    with lock:
        # Récupère l'état actuel
        current_status = validation_status

        # Réinitialise l'état à "pending" après un délai de 5 secondes
        def reset_status():
            global validation_status
            with lock:
                validation_status = "pending"

        # Utilise un thread pour réinitialiser l'état après 5 secondes
        threading.Timer(5.0, reset_status).start()

        return jsonify({"status": current_status})


@app.route('/validate', methods=['POST'])
def set_validation():
    """
    Route POST pour mettre à jour l'état (validé ou annulé).
    """
    global validation_status

    data = request.json
    if data and "status" in data:
        with lock:
            validation_status = data["status"]
            return jsonify({
                "message": "Validation status updated.",
                "new_status": validation_status
            })
    else:
        return jsonify({"error": "Invalid data"}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001, debug=True)
