from flask import Flask, request, jsonify, Response
import joblib
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io, base64

from src.model_io import ensure_model, load_bundle, save_bundle, MODEL_PATH, DEFAULT_FEATURES
from src.analysis import validate_features, run_full_analysis

app = Flask(__name__)

# Load or train-once at startup
bundle = ensure_model(features=DEFAULT_FEATURES, threshold=0.44)
pipe = bundle["pipeline"]
FEATURES = bundle["features"]
THRESH = float(bundle.get("threshold", 0.50))

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status":"ok","model":"loaded","features":FEATURES,"threshold":THRESH})

@app.route("/features", methods=["GET"])
def features():
    return jsonify({"features": FEATURES, "threshold": THRESH})

@app.route("/predict", methods=["POST"])
def predict():
    """
    POST JSON:
    {"features": {"gap_pct":..., "daily_range_pct":..., ...}}
    """
    try:
        payload = request.get_json(force=True)
        X = validate_features(payload, FEATURES)
        p_up = float(pipe.predict_proba(X)[:,1])
        yhat = int(p_up >= THRESH)
        return jsonify({"prediction": yhat, "p_up": p_up, "threshold": THRESH})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/predict/<float:input1>", methods=["GET"])
def predict_one(input1: float):
    return jsonify({"prediction": float(input1 * 2.0)})

@app.route("/predict/<float:input1>/<float:input2>", methods=["GET"])
def predict_two(input1: float, input2: float):
    return jsonify({"prediction": float(input1 + input2)})

@app.route("/plot", methods=["GET"])
def plot():
    grid = np.linspace(-2, 2, 60)
    X = np.zeros((len(grid), len(FEATURES)))
    X[:,0] = grid
    p = pipe.predict_proba(X)[:,1]

    fig, ax = plt.subplots(figsize=(5,3))
    ax.plot(grid, p)
    ax.axhline(THRESH, ls="--", color="gray")
    ax.set_title("P(Up) vs first feature")
    ax.set_xlabel(FEATURES[0]); ax.set_ylabel("P(Up)")
    buf = io.BytesIO(); fig.tight_layout(); fig.savefig(buf, format="png", dpi=150); plt.close(fig)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("utf-8")
    return Response(f'<img src="data:image/png;base64,{b64}"/>', mimetype="text/html")

# ---- NEW: run the full analysis and return file paths + metrics
@app.route("/run_full_analysis", methods=["POST", "GET"])
def run_full():
    try:
        payload = request.get_json(silent=True) or {}
        threshold = float(payload.get("threshold", THRESH))
        test_frac = float(payload.get("test_frac", 0.2))
        out = run_full_analysis(threshold=threshold, test_frac=test_frac)
        return jsonify(out)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# optional parameterized route
@app.route("/run_full_analysis/<float:threshold>/<float:test_frac>", methods=["GET"])
def run_full_params(threshold: float, test_frac: float):
    try:
        out = run_full_analysis(threshold=threshold, test_frac=test_frac)
        return jsonify(out)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(port=5000, debug=False, use_reloader=False)
