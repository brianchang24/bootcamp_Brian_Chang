# ML Model Packaging Repository

This repository shows how to package a small ML model for handoff & reuse:

- Clean repo structure
- Saved model artifact (`model.pkl`)
- Tiny Flask API (`app.py`)
- Simple notebook tests
- Clear README for anyone to rerun

---

## Repository Structure

    project/
      data/               # raw and processed data
        raw/
        processed/
      notebooks/          # training + API test notebooks
      src/                # reusable helpers (e.g., utils.py)
      model/              # saved model (model.pkl)
      deliverables/       # stakeholder summary / images (optional)
      app.py              # Flask API entry point
      requirements.txt    # dependencies
      README.md           # this file

---

## Setup

Create and activate a virtual environment, then install requirements:

    python -m venv .venv
    # macOS/Linux:
    source .venv/bin/activate
    # Windows:
    # .venv\Scripts\activate
    pip install -r requirements.txt

Verify installation:

    python -V
    pip show flask scikit-learn pandas numpy joblib matplotlib

---

## Train & Save the Model

Open and run the notebook:

    notebooks/train_and_save.ipynb

What it does:

- Loads the latest processed features from `data/processed/`
- Trains a simple `StandardScaler → LogisticRegression` pipeline
- Saves a bundle to `model/model.pkl` with:
  - `pipeline` (sklearn Pipeline)
  - `features` (required feature names)
  - `threshold` (default `0.44`)
  - `trained_on` (source file name)
  - `version`
- Performs a quick reload **smoke test**.

---

## Run the API

From the repo root:

    python app.py

The server runs at: http://127.0.0.1:5000

### Endpoints

- `GET /health` — status + model/feature info
- `POST /predict` — JSON body with named features → prediction and probability
- `GET /predict/<float>` — toy endpoint (doubles the input)
- `GET /predict/<float>/<float>` — toy endpoint (sums the inputs)
- `GET /plot` — small PNG chart (as HTML `\<img\>`) showing probability vs the first feature

---

## Example: `POST /predict`

    curl -X POST http://127.0.0.1:5000/predict \
      -H "Content-Type: application/json" \
      -d '{
        "features": {
          "gap_pct": 0.01,
          "daily_range_pct": 0.02,
          "ma_ratio_5_20": 1.01,
          "ret_vol_10": 0.015,
          "volume_z20": -0.2,
          "rsi_14": 48.0,
          "macd": 0.03,
          "macd_signal": 0.01
        }
      }'

Example response:

    {
      "prediction": 1,
      "p_up": 0.642,
      "threshold": 0.44
    }

---

## Test the API from a Notebook

Open and run:

    notebooks/api_test.ipynb

The notebook:

- Calls `GET /health`, `POST /predict`, `GET /predict/<...>`, `GET /plot`
- Prints JSON responses and confirms the API is working

---

## Assumptions & Risks

- **Feature contract**: The model expects the same engineered features it was trained with (see `GET /features` or the features list in the saved bundle). Missing or renamed features will cause errors.
- **Threshold choice**: The default decision threshold (`0.44`) may need retuning if the data distribution shifts.
- **Scope**: This is a homework demo, not production-hardened. Calibration, drift monitoring, and robust validation are out of scope here.

---

## Next Steps

- Replace the simple baseline with your latest/best model and feature set.
- Add batch prediction and richer error handling to the API.
- Optional: create a Streamlit dashboard for interactive inputs and plots.
- Consider Dockerization and CI checks for reproducibility.
- Add basic monitoring (data schema checks, feature drift alerts) if used beyond homework.

---

## Stakeholder Summary (Where to Find)

A short decision-oriented summary (PDF or Markdown) should live in `deliverables/`.

Include:

- Key metric(s)
- High-level assumptions
- Risks
- Sensitivity
- “What this means” for next steps
