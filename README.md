# Spotify Genre Associator
This repository uses Rodoflo Figueroa's "Spotify 1.2M+ Songs" dataset. You can download it here: https://www.kaggle.com/datasets/rodolfofigueroa/spotify-12m-songs?resource=download, though this works for any dataset with Artist IDs. 

# Setup
1. You'll need to use your Spotify Developer account, and configure your own Web API App. After you do so, update the `CLIENT_ID` and `CLIENT_SECRET` variables in `config.py` to match your credentials. 
2. `pip install -r requirements.txt`
3. `python app.py`
    - The original dataset takes around 10 minutes to run, which is the fastest I could get it to go. For speed, it's set up to run in batches and to rebound after it gets redirected or it fails.

 ## Other tips:
- Turn off console logs by changing `VERBOSE` to false
- Convert saved .csv to .parquet by running `python util.py -c folder/file.csv folder/file.parq`
- Convert saved .parquet to .csv by running `python util.py -c folder/file.parq folder/file.csv`
