from flask import Flask, request, jsonify
import pickle
import threading

app = Flask(__name__)
LokasiKm = None
# Load the model
@app.route('/predict', methods=['POST'])
def predict():
    with open('Pred_rtu.sav', 'rb') as file:
        LokasiKM = pickle.load(file)
    if LokasiKM is None:
        return jsonify({
            "status": "error",
            "message": "Model tidak ditemukan."
        }), 500

    try:
        # Ambil input JSON dari request
        data = request.json

        # Pastikan semua input tersedia
        required_keys = [f"spot{i}" for i in range(1, 10)]
        if not all(key in data for key in required_keys):
            return jsonify({
                "status": "error",
                "message": f"Input harus berisi semua titik: {', '.join(required_keys)}"
            }), 400

        # Convert input ke list float
        try:
            inputs = [float(data[key]) for key in required_keys]
        except ValueError:
            return jsonify({
                "status": "error",
                "message": "Semua input harus berupa angka valid."
            }), 400

        # Prediksi lokasi
        prediksi_lokasi = LokasiKM.predict([inputs])
        hasil_prediksi = prediksi_lokasi[0]

        # Bangun hasil prediksi
        results = []
        for i, val in enumerate(hasil_prediksi, start=1):
            if val > 0 and val < 63:
                # Bunyi alarm
                results.append({"titik": i, "lokasi": f"KM {val:.2f}", "status": "kebocoran"})
            else:
                results.append({"titik": i, "lokasi": None, "status": "aman"})

        # Return hasil dalam format JSON
        return jsonify({
            "status": "success",
            "results": results
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error predicting location: {str(e)}"
        }), 500

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)
