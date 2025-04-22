import pandas as pd
import config


def create_recession_indicators(tracks_df, sahm_df, threshold=0.5, save_path="", columns_to_drop=["observation_date_x", "observation_date_y", "release_month"]):
    config.VERBOSE and print(tracks_df.head())
    config.VERBOSE and print(tracks_df["SAHMCURRENT"].value_counts())

    sahm_df["observation_date"] = pd.to_datetime(sahm_df["observation_date"])
    sahm_df = sahm_df.sort_values("observation_date")
    sahm_df['sahm_12mo_avg'] = sahm_df['SAHMREALTIME'].rolling(window=12, min_periods=12).mean()
    sahm_df['sahm_12mo_min'] = sahm_df['sahm_12mo_avg'].expanding().min()

    tracks_df['release_month'] = pd.to_datetime(tracks_df['release_date']).dt.to_period('M').dt.to_timestamp()

    df = pd.merge(
        tracks_df,
        sahm_df[['observation_date', 'sahm_12mo_min']],  
        left_on='release_month',
        right_on='observation_date',
        how='left'
    )
    df['sahm_diff'] = df['SAHMCURRENT'] - df['sahm_12mo_min']

    df['recession'] = df['sahm_diff'] > 0.5

    config.VERBOSE and print(df.head())
    config.VERBOSE and print(df["recession"].value_counts())
    df.drop(columns=columns_to_drop, inplace=True)
    df.to_parquet(save_path) if save_path else ""
    return df
# danceability, energy, loudness, speechiness, acousticness, instrumentalness, liveness, valence
if __name__ == "__main__":
    df = create_recession_indicators(pd.read_parquet("data/tracks_genres_sahm.parquet"), pd.read_csv("data/SAHMREALTIME.csv"), save_path="tracks_genres_sahm_recession.parq")
    print(df.head())