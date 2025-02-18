import os
import requests

# Define the base URL with placeholders for year
def download_nasa_data(start_year=1950, end_year=2014, save_directory="/Users/vinayakbagdi/Downloads/"):
    base_url = ("https://ds.nccs.nasa.gov/thredds/ncss/grid/AMES/NEX/GDDP-CMIP6/"
                "HadGEM3-GC31-LL/historical/r1i1p1f3/tas/"
                "tas_day_HadGEM3-GC31-LL_historical_r1i1p1f3_gn_{year}.nc"
                "?var=tas&latitude=41.8838&longitude=-87.6321"
                "&time_start={year}-01-01T12:00:00Z&time_end={year}-12-30T12:00:00Z&&&accept=csv_file")
    
    # Create directory if it doesn't exist
    os.makedirs(save_directory, exist_ok=True)
    
    for year in range(start_year, end_year + 1):
        url = base_url.format(year=year)
        filename = os.path.join(save_directory, f"tas_data_{year}.csv")
        
        print(f"Downloading data for {year}...")
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Check if request was successful
            
            with open(filename, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            
            print(f"Saved: {filename}")
        except requests.RequestException as e:
            print(f"Failed to download data for {year}: {e}")

if __name__ == "__main__":
    download_nasa_data()
