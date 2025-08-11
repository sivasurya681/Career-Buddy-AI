import matplotlib.pyplot as plt

# Module names and average ratings
modules = ['Job Prediction', 'Chatbot', 'Resume Analysis', 'UI Design & Theme']
ratings = [9.2, 8.7, 9.0, 9.5]
colors = ['#76C7C0', '#FFA07A', '#87CEFA', '#FFD700']

# Plotting
plt.figure(figsize=(8, 6))
bars = plt.bar(modules, ratings, color=colors)

# Add labels on bars
for bar, rating in zip(bars, ratings):
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() - 0.2,
             f'{rating:.1f}', ha='center', va='bottom', fontsize=12, fontweight='bold')

# Labels and title
plt.title('CareerBuddy User Interface Experience Ratings', fontsize=14, fontweight='bold')
plt.ylabel('Average User Rating (out of 10)')
plt.ylim(0, 10)
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()

# Show the plot
plt.show()
