from os import environ
from requests import get
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile

def __get_content(base_url: str, api_key: str, series_id: str) -> str:
    content = ''
    data = get(f'{base_url}&api_key={api_key}&series_id={series_id}')
    zip_file = ZipFile(BytesIO(data.content))
    with zip_file.open(f'{series_id}_1.txt', mode='r') as fp:
        for line in fp.readlines():
            csv = line.decode('utf-8').split('\t')[0:2]
            content += '\n' + ','.join(csv)
    return 'DATE' + content[17:]

def __save_content(destination: str):
    Path(destination).parent.mkdir(parents=True, exist_ok=True)    
    with open(destination, mode='w') as fp:
        fp.write(content)

if __name__ == "__main__":
    content = __get_content(
        base_url  = 'https://api.stlouisfed.org/fred/series/observations?file_type=txt&observation_start=1998-01-01', 
        api_key   = environ.get('FRED_API_KEY'),     
        series_id = "PCREDIT8")
    
    __save_content('/temp-output-directory/alternative/interest-rate/usa/interest-rate.csv')

    print(content)