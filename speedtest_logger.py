import os
import sys
import speedtest
import json
from typing import Optional, List, Dict, Tuple, Any
from oauth2client.service_account import ServiceAccountCredentials
from gspread import authorize
from gspread.client import Client
from gspread.cell import Cell
from gspread.worksheet import Worksheet, ValueInputOption

class SpeedTestLoggerSession():
    LAST_ROW_CELL: List[int] = [2, 12]

    def __init__(self, config_params: Dict[str, str], credentials: ServiceAccountCredentials):
        if config_params.get("sheet_name") is None:
            raise ValueError("Unable to define speed test logger session. Configuration parameter 'sheet_name' is required.")
        self.sheet_name: str = config_params["sheet_name"]
        self.creds: ServiceAccountCredentials = credentials
        # optional parameters
        str_sheet_index: str = config_params.get("sheet_index", "")
        str_threads: str = config_params.get("threads", "")
        self.sheet_index: int = int(str_sheet_index) if str_sheet_index.isdigit() else 0
        self.threads: int = int(str_threads) if str_threads.isdigit() else 1
        # class managed
        self._last_row: int = 1

    def get_gsheet_log(self) -> Worksheet:
        client: Client = authorize(self.creds)
        sheet = client.open(self.sheet_name).get_worksheet(self.sheet_index)
        last_row = sheet.cell(self.LAST_ROW_CELL[0], self.LAST_ROW_CELL[1]).value
        if last_row.isdigit() and int(last_row) > 0:
            self._last_row = int(last_row)
        return sheet
    
    def write_test_result(self, row: List[Any]) -> None:
        log = self.get_gsheet_log()
        next_entry: int = self._last_row + 1
        log.update_cell(self.LAST_ROW_CELL[0], self.LAST_ROW_CELL[1], next_entry)
        row_cells: List[Cell] = log.range(f'A{next_entry}:F{next_entry}')
        for i, cell in enumerate(row_cells): cell.value = row[i]
        log.update_cells(row_cells, ValueInputOption.user_entered)

    @staticmethod
    def Init(config_file: str, cred_file: str) -> 'SpeedTestLoggerSession':
        config = SpeedTestLoggerSession._unpack_config(config_file)
        creds = SpeedTestLoggerSession._build_credential(cred_file)
        return SpeedTestLoggerSession(config, creds)
    
    @staticmethod
    def _build_credential(cred_file: str) -> ServiceAccountCredentials:
        if not os.path.exists(cred_file):
            raise FileNotFoundError(f"Unable to find gsheets credential file at provided path:\n '{cred_file}'")
        return ServiceAccountCredentials.from_json_keyfile_name(cred_file)

    @staticmethod
    def _unpack_config(config_file: str) -> Dict[str, str]:
        if not os.path.exists(config_file):
            raise FileNotFoundError("Unable to find configuration file")
        config_lines: List[str] = []
        with open(config_file, "r") as file:
            config_lines = file.readlines()
        config: Dict[str, str] = {}
        for line in config_lines:
            split = line.split("=")
            if len(split) > 1:
                split[1] = split[1].strip().strip('\r\n').strip('"').strip("'")
                key_name: Optional[str] = None
                if "sheet_name" in split[0]: key_name = "sheet_name"
                if "sheet_index" in split[0] and split[1].isdigit(): key_name = "sheet_index"
                if "threads" in split[0] and split[1].isdigit(): key_name = "threads"
                if key_name: config.update({key_name: split[1]})
        return config

def _to_mbps(bps: str) -> float:
    return round(float(bps) / (10**6), 4)

def _format_timestamp(timestamp: str) -> Tuple[str, str]:
    components = timestamp.split("T")
    date = components[0].split("-")
    formatted_date = f"{date[1]}/{date[2]}/{date[0]}"
    precise_time = components[1].split(":")
    seconds = float(precise_time[2][:len(precise_time[2])-1])
    formatted_time = f"{int(precise_time[0])}:{int(precise_time[1])}:{seconds:.2f}"
    return (formatted_date, formatted_time)

def _run_speedtest(threads: int) -> Dict[str, Any]:
    s = speedtest.Speedtest()
    s.get_best_server()
    s.download(threads=threads)
    s.upload(threads=threads, pre_allocate=False)
    return s.results.dict()

def main(config: str, cred_file: str):
    session = SpeedTestLoggerSession.Init(config, cred_file)
    results = _run_speedtest(session.threads)
    formatted_date, formatted_time = _format_timestamp(results['timestamp'])
    formatted_row: List[Any] = [
        formatted_date, # date
        formatted_time, # time
        results['server']['name'], # server name
        _to_mbps(results['download']), # download
        _to_mbps(results['upload']), # upload
        float(results['ping']), # ping
    ]
    session.write_test_result(formatted_row)

# Execute the wrapper
if __name__ == "__main__":
    try:
        config = sys.argv[1] if len(sys.argv) > 1 else "logger.config"
        cred_file = sys.argv[2] if len(sys.argv) > 2 else "gsheet-creds.json"
        main(config, cred_file)
    except KeyboardInterrupt:
        print()
        print('Interrupted \_[o_0]_/')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)