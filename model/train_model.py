"""
PASCI – Advanced ML Training Module
Trains multiple classifiers, compares them, saves the best as model.pkl
and also saves individual models separately.

Models trained:
    1. RandomForestClassifier      → model.pkl  (primary / best)
    2. GradientBoostingClassifier  → gradient_boost.pkl
    3. LogisticRegression          → logistic.pkl
    4. KNeighborsClassifier        → knn.pkl

Outputs:
    model/model.pkl            ← best model (used by the API)
    model/gradient_boost.pkl
    model/logistic.pkl
    model/knn.pkl
    model/scaler.pkl           ← StandardScaler (for models that need it)
    model/evaluation_report.txt
"""

import os, sys
import pandas as pd
import numpy as np
import joblib

from sklearn.ensemble          import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model      import LogisticRegression
from sklearn.neighbors         import KNeighborsClassifier
from sklearn.preprocessing     import StandardScaler
from sklearn.model_selection   import train_test_split, cross_val_score
from sklearn.metrics           import (
    classification_report, accuracy_score,
    confusion_matrix, roc_auc_score
)

ROOT      = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PATH = os.path.join(ROOT, "data", "data.csv")
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))


def load_data(path: str):
    df = pd.read_csv(path)
    X  = df[["distance", "traffic", "weather"]]
    y  = df["delay"]
    return X, y


def evaluate(name: str, clf, X_test, y_test, scaler=None) -> dict:
    X_in  = scaler.transform(X_test) if scaler else X_test
    preds = clf.predict(X_in)
    proba = clf.predict_proba(X_in)[:, 1]
    acc   = accuracy_score(y_test, preds)
    auc   = roc_auc_score(y_test, proba)
    cm    = confusion_matrix(y_test, preds)
    rep   = classification_report(y_test, preds, target_names=["On-time","Delayed"])
    return {"name": name, "accuracy": acc, "auc": auc, "cm": cm, "report": rep}


def train_all():
    print("=" * 60)
    print("  PASCI – Multi-Model ML Training")
    print("=" * 60)

    if not os.path.exists(DATA_PATH):
        print("[train_all] Generating dataset first ...")
        sys.path.insert(0, ROOT)
        from model.generate_data import generate_dataset
        generate_dataset(save_path=DATA_PATH)

    X, y = load_data(DATA_PATH)
    print(f"\n[data] {len(X)} samples | class balance: {y.value_counts().to_dict()}")

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

    # Scaler for LR and KNN
    scaler   = StandardScaler()
    X_tr_sc  = scaler.fit_transform(X_tr)
    X_te_sc  = scaler.transform(X_te)
    joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.pkl"))
    print("[scaler] StandardScaler saved -> model/scaler.pkl")

    models = [
        {
            "name":   "RandomForest",
            "clf":    RandomForestClassifier(n_estimators=200, max_depth=None,
                                              random_state=42, n_jobs=-1),
            "file":   "model.pkl",
            "scaled": False,
        },
        {
            "name":   "GradientBoosting",
            "clf":    GradientBoostingClassifier(n_estimators=200, learning_rate=0.1,
                                                  max_depth=4, random_state=42),
            "file":   "gradient_boost.pkl",
            "scaled": False,
        },
        {
            "name":   "LogisticRegression",
            "clf":    LogisticRegression(max_iter=1000, random_state=42),
            "file":   "logistic.pkl",
            "scaled": True,
        },
        {
            "name":   "KNeighbors",
            "clf":    KNeighborsClassifier(n_neighbors=7),
            "file":   "knn.pkl",
            "scaled": True,
        },
    ]

    results      = []
    report_lines = [
        "PASCI - ML Evaluation Report",
        "=" * 60,
        f"Dataset: {len(X)} rows | Train: {len(X_tr)} | Test: {len(X_te)}",
        "",
    ]

    for m in models:
        name   = m["name"]
        clf    = m["clf"]
        sc     = scaler if m["scaled"] else None
        X_fit  = X_tr_sc if m["scaled"] else X_tr
        X_eval = X_te_sc if m["scaled"] else X_te

        print(f"\n[train] {name} ...")
        clf.fit(X_fit, y_tr)

        cv_X = X_tr_sc if m["scaled"] else X_tr
        cv   = cross_val_score(clf, cv_X, y_tr, cv=5, scoring="accuracy")

        ev            = evaluate(name, clf, X_te, y_te, scaler=sc)
        ev["cv_mean"] = cv.mean()
        ev["cv_std"]  = cv.std()
        results.append(ev)

        save_path = os.path.join(MODEL_DIR, m["file"])
        joblib.dump(clf, save_path)
        print(f"  Accuracy  : {ev['accuracy']:.4f}")
        print(f"  AUC       : {ev['auc']:.4f}")
        print(f"  CV 5-fold : {cv.mean():.4f} +/- {cv.std():.4f}")
        print(f"  Saved     -> model/{m['file']}")

        report_lines += [
            f"Model: {name}",
            "-" * 40,
            f"  Accuracy    : {ev['accuracy']:.4f}",
            f"  ROC-AUC     : {ev['auc']:.4f}",
            f"  CV Accuracy : {ev['cv_mean']:.4f} +/- {ev['cv_std']:.4f}",
            f"  Saved to    : model/{m['file']}",
            "",
            "  Classification Report:",
            ev["report"],
            f"  Confusion Matrix:\n{ev['cm']}",
            "",
        ]

    print("\n" + "=" * 60)
    print("  LEADERBOARD")
    print("=" * 60)
    ranked = sorted(results, key=lambda r: r["auc"], reverse=True)
    for i, r in enumerate(ranked, 1):
        print(f"  {i}. {r['name']:<22} Accuracy={r['accuracy']:.4f}  AUC={r['auc']:.4f}")

    best = ranked[0]
    report_lines += [
        "=" * 60,
        "LEADERBOARD (sorted by AUC)",
        "-" * 40,
    ]
    for i, r in enumerate(ranked, 1):
        report_lines.append(
            f"  {i}. {r['name']:<22} Acc={r['accuracy']:.4f}  AUC={r['auc']:.4f}"
        )
    report_lines += ["", f"Best model: {best['name']} (AUC={best['auc']:.4f})"]

    rpt_path = os.path.join(MODEL_DIR, "evaluation_report.txt")
    with open(rpt_path, "w") as f:
        f.write("\n".join(report_lines))
    print(f"\n[report] Saved -> model/evaluation_report.txt")
    print("\nAll models trained and saved successfully.")
    print(f"  Primary model (model.pkl)  = RandomForest")
    print(f"  Best by AUC               = {best['name']}")
    return results


def predict(distance: int, traffic: int, weather: int) -> dict:
    """Load primary model and predict delay probability."""
    model_path = os.path.join(MODEL_DIR, "model.pkl")
    clf  = joblib.load(model_path)
    X    = pd.DataFrame([[distance, traffic, weather]],
                        columns=["distance", "traffic", "weather"])
    delay = int(clf.predict(X)[0])
    risk  = round(float(clf.predict_proba(X)[0][1]), 4)
    return {"delay": delay, "risk": risk}


if __name__ == "__main__":
    train_all()
