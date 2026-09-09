import pandas as pd
from pathlib import Path

# Your Desktop path
RESULTS_CSV = (
    Path.home()
    / "Desktop"
    / "BOX_PLOTS_DATA"
    / "boxplots_testes_feitos"
    / "best_robots"
    / "horizontal"
    / "Husky_like_robot&controllers"
    / "evaluation_results_99_1_best_simetrico_seed_44.csv"
)

# Output file: eval_aqui.csv in the folder where the script is executed
SUMMARY_CSV = RESULTS_CSV.parent / "eval_aqui.csv"

# Check that the input exists
if not RESULTS_CSV.exists():
    raise FileNotFoundError(
        f"\nCSV not found:\n{RESULTS_CSV}\n\n"
        "Check that the file is actually stored in this Desktop path."
    )

# Load results
results = pd.read_csv(RESULTS_CSV)

# Calculate summary using exactly the same formulas
# as evaluation_summary_all_robots.csv
summary_df = pd.DataFrame([{
    "Robot": "99_1_best_simetrico_seed_44",
    "Episodes": len(results),
    "MeanReward": results["Reward"].mean(),
    "StdReward": results["Reward"].std(ddof=1),
    "MeanDistance": results["Distance"].mean(),
    "StdDistance": results["Distance"].std(ddof=1),
    "MeanMaxDistance": results["MaxDistance"].mean(),
    "StdMaxDistance": results["MaxDistance"].std(ddof=1),
    "MeanSteps": results["Steps"].mean(),
    "StdSteps": results["Steps"].std(ddof=1),
}])

# Save
summary_df.to_csv(SUMMARY_CSV, index=False)

print("\n" + "=" * 78)
print("Run evaluation completed.")
print(f"Input CSV:   {RESULTS_CSV}")
print(f"Summary CSV: {SUMMARY_CSV}")

print("\nSummary:")
print(summary_df.to_string(index=False))