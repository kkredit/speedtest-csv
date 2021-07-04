import speedtest
import time


def epoch_ts() -> int:
    return int(time.time())


class SpeedTestRunner:
    def __init__(
        self, period=60, samples=0, outfile="speedtest_results.csv", threads=1
    ):
        self._period = period
        self._samples = samples
        self._outfile = outfile
        self._threads = threads
        self._tester = speedtest.Speedtest()
        self._tester.get_servers()
        self._tester.get_best_server()

    def run_continually(self) -> None:
        run = 0
        while self._samples <= 0 or run < self._samples:
            run += 1
            print(f"Performing run {run}...")
            duration = self.run_once()
            time.sleep(self._period - duration)

    def run_once(self) -> int:
        start_ts = epoch_ts()
        self._tester.download(threads=self._threads)
        self._tester.upload(threads=self._threads)
        # self._tester.results.share()
        print(self._tester.results)
        return epoch_ts() - start_ts


if __name__ == "__main__":
    print("Now collecting speedtest data!")
    SpeedTestRunner().run_continually()
