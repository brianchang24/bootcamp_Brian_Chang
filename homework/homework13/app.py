from flask import Flask, request, jsonify, Response
import joblib
from pathlib import Path
from src.utils import validate_features
import matplotlib
matplotlib.use("Agg") 
import matplotlib.pyplot as plt
import numpy as np
import io, base64

MODEL_PATH = Path("model/model.pkl")
bundle = joblib.load(MODEL_PATH)
pipe = bundle["pipeline"]
FEATURES = bundle["features"]
THRESH = float(bundle.get("threshold", 0.50))

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status":"ok","model":"loaded","features":FEATURES})

@app.route("/predict", methods=["POST"])
def predict():
    """
    POST JSON:
    {"features": {"gap_pct":0.01, "daily_range_pct":0.02, ...}}
    """
    try:
        payload = request.get_json(force=True)
        X = validate_features(payload, FEATURES)
        p_up = float(pipe.predict_proba(X)[:,1])
        yhat = int(p_up >= THRESH)
        return jsonify({"prediction": yhat, "p_up": p_up, "threshold": THRESH})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Homework-required toy endpoints:
@app.route("/predict/<float:input1>", methods=["GET"])
def predict_one(input1: float):
    # simple demo: double it
    return jsonify({"prediction": float(input1 * 2.0)})

@app.route("/predict/<float:input1>/<float:input2>", methods=["GET"])
def predict_two(input1: float, input2: float):
    # simple demo: sum
    return jsonify({"prediction": float(input1 + input2)})

@app.route("/plot", methods=["GET"])
def plot():
    """
    Tiny chart: P(Up) vs first feature, others=0
    """
    try:
        grid = np.linspace(-2, 2, 60)
        X = np.zeros((len(grid), len(FEATURES)))
        X[:,0] = grid
        p = pipe.predict_proba(X)[:,1]

        fig, ax = plt.subplots(figsize=(5,3))
        ax.plot(grid, p)
        ax.axhline(THRESH, ls="--", color="gray")
        ax.set_title("P(Up) vs first feature")
        ax.set_xlabel(FEATURES[0]); ax.set_ylabel("P(Up)")

        buf = io.BytesIO()
        fig.tight_layout()
        fig.savefig(buf, format="png", dpi=150)
        plt.close(fig)
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode("utf-8")
        return Response(f'<img src="data:image/png;base64,{b64}"/>', mimetype="text/html")
    except Exception as e:
        # Return JSON error instead of killing the server
        return jsonify({"error": f"plot_failed: {type(e).__name__}: {e}"}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
