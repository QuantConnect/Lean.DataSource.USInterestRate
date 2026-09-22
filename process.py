from os import environ
from json import load
from requests import get
from pathlib import Path

def __get_config() -> dict:
    # The job writes its Job Configuration entries into a config.json next to this file
    path = Path(__file__).parent / 'config.json'
    if not path.exists():
        return {}
    with open(path) as fp:
        return load(fp)

def __get_content(base_url: str, api_key: str, series_id: str) -> str:
    if not api_key:
        raise ValueError('Set fred-api-key in config.json or the FRED_API_KEY environment variable')
    response = get(base_url, params={'file_type': 'json', 'api_key': api_key, 'series_id': series_id}, timeout=60)
    # Don't raise_for_status: its message has the request URL, which carries the api key
    if not response.ok:
        raise RuntimeError(f'FRED returned {response.status_code}: {response.text}')
    # FRED marks missing observations with '.'
    rows = [f"{x['date']},{x['value']}" for x in response.json()['observations'] if x['value'] != '.']
    if not rows:
        raise ValueError(f'No observations returned for {series_id}')
    return '\n'.join([f'DATE,{series_id}'] + rows) + '\n'

def __save_content(destination: str, content: str):
    Path(destination).parent.mkdir(parents=True, exist_ok=True)
    with open(destination, mode='w', newline='\n') as fp:
        fp.write(content)

if __name__ == "__main__":
    config = __get_config()
    content = __get_content(
        base_url  = 'https://api.stlouisfed.org/fred/series/observations?observation_start=1998-01-01',
        api_key   = config.get('fred-api-key') or environ.get('FRED_API_KEY'),
        series_id = "PCREDIT8")

    output_directory = config.get('temp-output-directory', '/temp-output-directory')
    __save_content(f'{output_directory}/alternative/interest-rate/usa/interest-rate.csv', content)

    print(content)
