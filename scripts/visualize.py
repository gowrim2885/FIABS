import pandas as pd
import matplotlib.pyplot as plt
import os

# Create outputs directory if it doesn't exist
if not os.path.exists("outputs"):
    os.makedirs("outputs")

# Load dataset
df = pd.read_csv("data/processed/final_dataset.csv")

# Plot GDP trend
plt.figure(figsize=(10, 6))
plt.plot(df["Year"], df["GDP"], marker='o', linestyle='-', color='b', label="Historical GDP")

plt.title("GDP Trend Over Years (2021-2023)")
plt.xlabel("Year")
plt.ylabel("GDP (USD)")
plt.xticks(df["Year"])
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()

# Save the plot
plt.savefig("outputs/gdp_trend.png")
print("✅ Visualization saved to outputs/gdp_trend.png")

# Show plot (optional)
# plt.show()
