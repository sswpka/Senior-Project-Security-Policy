import autosklearn.classification
import pandas as pd
import time
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score

# Load dataset
file_path = "Dataset_normalized.csv"
df = pd.read_csv(file_path)

# Define features and targets
features = ["num_stargazers", "num_watchers", "num_forks", "num_subscribers"]
targets = ["Generic policy", "Reporting mechanism", "Scope of practice", "User guideline"]

# Store results
results = {}

# Train and evaluate a model for each target
for target in targets:
    print(f"\nTraining model for target: {target} ...")
    X = df[features]
    y = df[target]

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # Start time tracking
    start_time = time.time()

    # Define and train the auto-sklearn classifier
    automl = autosklearn.classification.AutoSklearnClassifier(time_left_for_this_task=120, per_run_time_limit=30)
    automl.fit(X_train, y_train)

    # End time tracking
    end_time = time.time()
    training_duration = round(end_time - start_time, 2)

    print(f"Training completed in {training_duration} seconds for {target}")

    # Predict and evaluate
    y_pred = automl.predict(X_test)

    # Calculate Accuracy
    accuracy = accuracy_score(y_test, y_pred)

    # Generate Classification Report
    class_report = classification_report(y_test, y_pred)

    # Compute AUC Score (only if there are at least 2 classes)
    try:
        auc_score = roc_auc_score(y_test, automl.predict_proba(X_test), multi_class="ovr")
    except ValueError:
        auc_score = "Not applicable (only 1 class present)"

    # Store results
    results[target] = {
        "best_model": automl.show_models(),
        "accuracy": accuracy,
        "classification_report": class_report,
        "auc_score": auc_score,
        "training_time": training_duration
    }

# Print results
for target, result in results.items():
    print(f"**Results for Target: {target}**")
    print(f"Best Model:\n{result['best_model']}")
    print(f"Accuracy: {result['accuracy']:.4f}")
    print(f"AUC Score: {result['auc_score']}")
    print(f"Classification Report:\n{result['classification_report']}")
    print("=" * 60)
