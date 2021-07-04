import logging
import pprint
import time
from datetime import datetime

import speedtest


def epoch_ts() -> int:
    return int(time.time())


class SpeedTestRunner:
    def __init__(
        self,
        period=60,
        samples=0,
        outfile="speedtest_results.csv",
        threads=1,
        servers=None,
    ):
        print("Initializing...")
        self._period = period
        self._samples = samples
        self._outfile = outfile
        self._threads = threads
        self._tester = speedtest.Speedtest()
        self._tester.get_servers(servers)
        self._tester.get_best_server()
        self._initialize_csv()
        print("Initialization complete")

    def run_continually(self) -> None:
        run = 0
        while self._samples <= 0 or run < self._samples:
            run += 1
            print(f"\nPerforming run {run}...")
            duration = self.run_once()
            time.sleep(self._period - duration)

    def run_once(self) -> int:
        start_ts = epoch_ts()
        self._reset_result_timestamp()
        self._tester.download(threads=self._threads)
        self._tester.upload(threads=self._threads)
        self._print_results()
        self._append_csv()
        return epoch_ts() - start_ts

    def _initialize_csv(self) -> None:
        try:
            with open(self._outfile, "x") as outfile:
                outfile.write(speedtest.SpeedtestResults.csv_header() + "\n")
        except FileExistsError:
            pass

    def _append_csv(self) -> None:
        with open(self._outfile, "a") as outfile:
            outfile.write(self._tester.results.csv() + "\n")

    def _reset_result_timestamp(self) -> None:
        self._tester.results.timestamp = datetime.now().isoformat()

    def _print_results(self) -> None:
        print("Results: ")
        results = self._tester.results.dict()
        filtered = {
            k: v for k, v in results.items() if k not in ["client", "server", "share"]
        }
        filtered.update({"isp": results.get("client", {}).get("isp")})
        pprint.pprint(filtered)


if __name__ == "__main__":
    print("Now collecting speedtest data!")
    grand_rapids_mi = 34750
    while True:
        try:
            SpeedTestRunner(servers=[grand_rapids_mi]).run_continually()
            break
        except Exception as err:
            logging.error("Error! %r\n Restarting...", err)
