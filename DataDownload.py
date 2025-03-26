import os
import requests

def download_nasa_data(start_year=2015, end_year=2100, base_directory="/Users/vinayakbagdi/Downloads/"):
    save_directory = os.path.join(base_directory, "ssp126_hurs")
    base_url = ("https://ds.nccs.nasa.gov/thredds/ncss/grid/AMES/NEX/GDDP-CMIP6/"
                "HadGEM3-GC31-LL/ssp126/r1i1p1f3/hurs/"
                "hurs_day_HadGEM3-GC31-LL_ssp126_r1i1p1f3_gn_{year}_v1.1.nc"
                "?var=hurs&latitude=41.8838&longitude=-87.6321"
                "&time_start={year}-01-01T12:00:00Z&time_end={year}-12-30T12:00:00Z&&&accept=csv_file")
    
    os.makedirs(save_directory, exist_ok=True)
    
    for year in range(start_year, end_year + 1):
        url = base_url.format(year=year)
        filename = os.path.join(save_directory, f"hurs_data_{year}.csv")
        
        print(f"Downloading data for {year}...")
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(filename, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            
            print(f"Saved: {filename}")
        except requests.RequestException as e:
            print(f"Failed to download data for {year}: {e}")

if __name__ == "__main__":
    download_nasa_data()
