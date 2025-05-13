import pandas as pd
from scipy.stats import shapiro

from scipy.stats import mannwhitneyu

import numpy as np

import matplotlib.pyplot as plot

# might need to implement from scratch
FEATURES = ["danceability", "energy", "loudness", "speechiness", "acousticness", "instrumentalness", "liveness", "valence"]

df = pd.read_parquet("tracks_genres_sahm_recession.parq")
recession = df[df['recession']].dropna()
not_recession = df[~df['recession']].dropna()

def shapiro_wilk_test(data, group_name, feature_name):
    stat, p = shapiro(data[feature_name].dropna())
    print(f"{group_name} group ({feature_name}): p = {p}")
    return float(p)

def check_normality(groups={}, features=[], p_thres = 0.05):
    groups_w_p = {}
    for group in groups.items():
        print(f"--> {group[0]}")
        for feature in features:
            print(f"--! {feature}")
            p = shapiro_wilk_test(group[1], group[0], feature)
            print(f"p : {p}")
            print("NORMAL") if p > p_thres else print("NOT NORMAL")
            groups_w_p[group[0], feature] = p
    return groups_w_p

def effect_size(group_1, group_2):
    group_1 = np.asarray(group_1)
    group_2 = np.asarray(group_2)
    n_1, n_2 = len(group_1), len(group_2)
    sorted_group_2 = np.sort(group_2)
    less = np.searchsorted(sorted_group_2, group_1, side='right')
    greater = n_2 - np.searchsorted(sorted_group_2, group_1, side='left')
    return (less.sum() - greater.sum()) / (n_1 * n_2)

def mann_whitney(group_1, group_2, features, a=0.05):
    results = []
    for feature in features:
        group_1_data = group_1[feature].dropna().values
        group_2_data = group_2[feature].dropna().values

        stat, p = mannwhitneyu(group_1_data, group_2_data, alternative="two-sided")
        results.append({
            "feature" : feature,
            "statistic" : stat,
            "p" : p,
            "d" : effect_size(group_1_data, group_2_data),
            "median_1" : np.median(group_1_data),
            "median_2" : np.median(group_2_data),
            "len_1" : len(group_1_data),
            "len_2" : len(group_2_data)
        })
    df = pd.DataFrame(results)
    # think you gotta do this if you compare multiple features at once???
    n_tests = len(features)
    df["adj_p"] = np.minimum(df["p"] * n_tests, 1.0)
    
    df["significant?"] = df["adj_p"] < a
    
    return df

def print_results(df):
    print("Mann-Whitney U Test Results with Effect Sizes:")
    print("-----------------------------------------------")
    for _, row in df.iterrows():
        print(f"\nFeature: {row["feature"]}")
        print(f"U Statistic: {row["statistic"]:.0f}")
        print(f"Unadjusted p-value: {row["p"]}")
        print(f"Adjusted p-value: {row["adj_p"]}")
        print(f"Significant: {'Yes' if row["significant?"] else 'No'}")
        print(f"Effect size: {row["d"]:.3f}")
        print(f"Medians - Recession: {row["median_1"]:.3f}, Non-Recession: {row["median_2"]:.3f}")
        print(f"Sample Sizes - Recession: {row["len_1"]}, Non-Recession: {row["len_2"]}")

def plot_effect_sizes(results_df, figsize=(10, 6)):
    results_df = results_df.sort_values('d', ascending=False)
    
    fig, ax = plot.subplots(figsize=figsize)
    
    colors = []
    for _, row in results_df.iterrows():
        if row['significant?']:
            color = '#1f77b4' if row['d'] > 0 else '#d62728' # blue good red bad 
        else:
            color = 'gray'
        colors.append(color)
    
    y_pos = np.arange(len(results_df))
    ax.barh(y_pos, results_df['d'], color=colors, alpha=0.8)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(results_df['feature'])
    ax.set_xlabel("Cliff's Delta Effect Size", fontsize=12)
    ax.set_title("Effect Sizes of Song Features During Recessions", fontsize=14, pad=20)
    
    for delta, label in [(0.147, "0.147"), (0.33, "0.33"), (0.474, "0.474")]:
        ax.axvline(delta, color='k', linestyle='--', alpha=0.3)
        ax.axvline(-delta, color='k', linestyle='--', alpha=0.3)
        ax.text(delta+0.01, 0.1, label, rotation=90, va='bottom', alpha=0.7)
    
    for i, (delta, adj_p) in enumerate(zip(results_df['d'], results_df['adj_p'])):
        ax.text(delta/2 if delta > 0 else delta/2, i, 
                f"Δ={delta:.2f}\n(p={adj_p:.4f})", 
                va='center', ha='center' if abs(delta) < 0.3 else 'left',
                fontsize=9, color='white' if abs(delta) > 0.2 else 'black')
    
    plot.tight_layout()
    return fig, ax

def volcano_plot(results_df):
    fig, ax = plot.subplots(figsize=(10, 6))
    
    results_df['neg_log_p'] = -np.log10(results_df['adj_p'])
    
    colors = ['#1f77b4' if sig else 'gray' for sig in results_df['significant?']]
    
    ax.scatter(results_df['d'], results_df['neg_log_p'], c=colors, alpha=0.7)
    
    ax.axhline(-np.log10(0.05), color='red', linestyle='--', label='p=0.05')
    ax.axvline(0, color='black', linestyle='-', alpha=0.5)
    ax.set_xlabel("Cliff's Delta")
    ax.set_ylabel("-log10(adjusted p-value)")
    ax.set_title("Volcano Plot: Effect Size vs. Statistical Significance")
    
    top_features = results_df.nlargest(3, 'neg_log_p')
    for _, row in top_features.iterrows():
        ax.text(row['d'], row['neg_log_p'], row['feature'], 
                fontsize=9, ha='center', va='bottom')
    
    plot.legend()
    return fig, ax


# danceability, energy, loudness, speechiness, acousticness, instrumentalness, liveness, valence
# check if normal
groups_w_p = check_normality({"Recession" : recession, "Not Recession" : not_recession}, 
                FEATURES)

print(groups_w_p)

# oops not normal
df = mann_whitney(recession, not_recession, FEATURES)

print_results(df)

fig, ax = plot_effect_sizes(df)
plot.savefig("effect_sizes.png", dpi=300, bbox_inches='tight')
plot.show()

fig, ax = volcano_plot(df)
plot.savefig("volcano_plot.png", dpi=300, bbox_inches='tight')
plot.show()