import logging
import pprint
import time
from argparse import ArgumentParser
from datetime import datetime

import speedtest

try:
    from gooey import Gooey
except ImportError:

    def Gooey(func):
        return func


def epoch_ts() -> int:
    return int(time.time())


class SpeedTestRunner:
    def __init__(self, args):
        print("Initializing...")
        self._period = args.period
        self._samples = args.samples
        self._outfile = args.outfile
        self._threads = args.threads
        self._tester = speedtest.Speedtest()
        self._tester.get_servers(args.servers)
        self._tester.get_best_server()
        self._initialize_csv()
        print("Initialization complete")

    def run(self) -> None:
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


@Gooey
def main():
    parser = ArgumentParser(description="Monitor your internet speed.")
    parser.add_argument(
        "-p",
        "--period",
        action="store",
        type=int,
        default=60,
        help="How frequently to run the speedtest",
    )
    parser.add_argument(
        "-s",
        "--samples",
        action="store",
        type=int,
        default=0,
        help="How many samples to take (if <=0, run forever)",
    )
    parser.add_argument(
        "-o",
        "--outfile",
        action="store",
        type=str,
        default="speedtest_results.csv",
        help="Relative path to output CSV file",
    )
    parser.add_argument(
        "-t",
        "--threads",
        action="store",
        type=int,
        default=1,
        help="Number of threads to test with",
    )
    parser.add_argument(
        "-e",
        "--servers",
        action="store",
        type=int,
        nargs="+",
        default=[34750],
        help="Specific servers to test against (34750 is a server in Grand Rapids, MI)",
    )
    args = parser.parse_args()
    print("Now collecting speedtest data!")
    while True:
        try:
            SpeedTestRunner(args).run()
            break
        except Exception as err:
            logging.error("Error! %r\n Restarting...", err)


if __name__ == "__main__":
    main()
