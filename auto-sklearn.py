import autosklearn.classification
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

file_path = "/dataset/Dataset_normalized.csv"
df = pd.read_csv(file_path)

df.head()

# Define features and targets
features = ["num_stargazers", "num_watchers", "num_forks", "num_subscribers"]
targets = ["Generic policy", "Reporting mechanism", "Scope of practice", "User guideline"]

# Store results
results = {}

# Train and evaluate a model for each target
for target in targets:
    X = df[features]
    y = df[target]

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Define and train the auto-sklearn classifier
    automl = autosklearn.classification.AutoSklearnClassifier(time_left_for_this_task=120, per_run_time_limit=30)
    automl.fit(X_train, y_train)

    # Predict and evaluate
    y_pred = automl.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    # Store results
    results[target] = {
        "best_model": automl.show_models(),
        "accuracy": accuracy
    }

# Print results
for target, result in results.items():
    print(f"Target: {target}")
    print(f"Best Model: {result['best_model']}")
    print(f"Accuracy: {result['accuracy']}\n")