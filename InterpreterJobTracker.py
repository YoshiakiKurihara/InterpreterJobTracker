# --- 必要なモジュールのインポート ---
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import numpy as np

import sys
import os
from time import sleep
from datetime import datetime
from io import StringIO
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional
import math
from colorama import Fore, Style, init
import schedule
import atexit
import smtplib
from email.message import EmailMessage


# --- 設定データクラス ---
@dataclass
class Config:
    LOGIN_URL: str
    DEBUG_MODE: bool
    STUB_URL: str
    EMAIL: str
    IDENTIFIER: str
    PASSWORD: str
    EMAIL_ADDRESS_FROM: str
    EMAIL_PASSWORD: str
    EMAIL_ADDRESS_TO: str


# --- メインクラス ---
class InterpreterJobTracker:
    def __init__(self):
        # 設定の読み込みと初期化
        self.config = self._load_config()
        self.driver = self._initialize_driver()
        self.NO_JOB_DATES = ['07/01/2025', '08/01/2025', '09/01/2025']
        self.AFTER_HOUR = 14
        self.MAX_DISTANCE = 20
        self.MAX_RELOAD_ATTEMPTS = 8640

        init(autoreset=True)
        atexit.register(self.on_shutdown)

        script_path = os.path.abspath(__file__)
        print(f"スクリプトのパス: {script_path}")

    # --- 設定の読み込み ---
    def _load_config(self) -> Config:
        load_dotenv()
        return Config(
            LOGIN_URL=os.getenv("LOGIN_URL"),
            DEBUG_MODE=bool(os.getenv("DEBUG_MODE")),
            STUB_URL=os.getenv("STUB_URL"),
            EMAIL=os.getenv("EMAIL"),
            IDENTIFIER=os.getenv("IDENTIFIER"),
            PASSWORD=os.getenv("PASSWORD"),
            EMAIL_ADDRESS_FROM=os.getenv("EMAIL_ADDRESS_FROM"),
            EMAIL_PASSWORD=os.getenv("EMAIL_PASSWORD"),
            EMAIL_ADDRESS_TO=os.getenv("EMAIL_ADDRESS_TO")
        )

    # --- シャットダウン時の処理 ---
    def on_shutdown(self):
        self.send_email("SHUTDOWN")

    # --- WebDriverの初期化 ---
    def _initialize_driver(self) -> webdriver.Chrome:
        options = Options()
        options.add_argument("--headless")
        return webdriver.Chrome(options=options)

    # --- メール送信 ---
    def send_email(self, mode: str):
        msg = EmailMessage()
        msg['From'] = self.config.EMAIL_ADDRESS_FROM
        msg['To'] = self.config.EMAIL_ADDRESS_TO

        if mode == "START":
            msg['Subject'] = "Interpreter Job Tracker App : Start"
            msg.set_content("Start")
        elif mode == "MONITORING":
            msg['Subject'] = "Interpreter Job Tracker App : Monitoring"
            msg.set_content("Monitoring")
        elif mode == "SHUTDOWN":
            msg['Subject'] = "Interpreter Job Tracker : Shutdown"
            msg.set_content("Shutdown")
        else:
            msg['Subject'] = "Interpreter Job Tracker : Unknown"
            msg.set_content("Unknown Status")

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(self.config.EMAIL_ADDRESS_FROM, self.config.EMAIL_PASSWORD)
            smtp.send_message(msg)

    # --- ログイン処理 ---
    def login(self) -> None:
        if self.config.DEBUG_MODE:
            self.driver.get(self.config.STUB_URL)
            sleep(0.5)
        else:
            self.driver.get(self.config.LOGIN_URL)
            sleep(0.5)

            if not self._check_window_title('Login | TIS Online'):
                sys.exit(Fore.RED + "ログインページにアクセスできませんでした")

            try:
                self.driver.find_element(By.NAME, "EmailAddresss").send_keys(self.config.EMAIL)
                self.driver.find_element(By.NAME, "Identifier").send_keys(self.config.IDENTIFIER)
                self.driver.find_element(By.NAME, "Password").send_keys(self.config.PASSWORD)
                self.driver.find_element(By.CLASS_NAME, "primary-button").click()
                sleep(5)
            except NoSuchElementException:
                sys.exit(Fore.RED + "ログイン要素が見つかりませんでした")

            if not self._check_window_title('My jobs summary | TIS Online'):
                sys.exit(Fore.RED + "ログイン後のページ遷移に失敗しました")

    # --- ウィンドウタイトルの確認 ---
    def _check_window_title(self, expected_title: str) -> bool:
        return self.driver.title == expected_title

    # --- ジョブ数の取得 ---
    def get_job_count(self) -> int:
        try:
            num_jobs = self.driver.find_element(By.XPATH, '/html/body/div/div[2]/div[2]/div[4]/div[2]/div[2]/div[1]/span').text
            return int(num_jobs) if num_jobs.isdigit() else -1
        except NoSuchElementException:
            return -1

    # --- ジョブの処理 ---
    def process_jobs(self, df: pd.DataFrame, jobs_available: int) -> None:
        for i in range(jobs_available):
            job_time = df['Date/Time'][i]
            if not self._is_valid_job_date(str(job_time)):
                print(f"{datetime.now()} - ジョブ除外日: {job_time}")
                self._hide_job()
                continue

            timetojob = self._parse_time_to_job(df['Time to job'][i])
            distance = self._parse_distance(df['Distance'][i])

            if self._should_accept_job(timetojob, distance):
                self._accept_job()
                print(f"{datetime.now()} - ジョブを受諾: 時間 {timetojob}時間, 距離 {distance}km")
                break
            else:
                self._hide_job()
                print(f"{datetime.now()} - ジョブを非表示: 時間 {timetojob}時間, 距離 {distance}km")

    # --- 時間の解析 ---
    def _parse_time_to_job(self, timetojob: str) -> float:
        if 'day' in timetojob:
            return float(timetojob.replace('days', '').replace('day', '').replace(' ', '')) * 24
        elif 'hour' in timetojob:
            return float(timetojob.replace('hours', '').replace('hour', '').replace(' ', ''))
        return 0.0

    # --- 距離の解析 ---
    def _parse_distance(self, distance: str) -> Optional[float]:
        if isinstance(distance, str):
            if 'nan' in distance.lower():
                return 0.0
            elif 'Km' in distance or 'km' in distance:
                value = distance.replace('Km', '').replace('km', '').replace(' ', '')
                return float(value) if self._is_convertible_to_float(value) else None
        elif isinstance(distance, (float, np.float64)):
            if math.isnan(distance):
                return 0.0
            return float(distance)
        return None

    # --- ジョブ日付の検証 ---
    def _is_valid_job_date(self, date_time: str) -> bool:
        return all(no_date not in date_time for no_date in self.NO_JOB_DATES)

    # --- 数値変換可能性の確認 ---
    def _is_convertible_to_float(self, value: str) -> bool:
        try:
            float(value)
            return True
        except ValueError:
            return False

    # --- ジョブ受諾条件の確認 ---
    def _should_accept_job(self, timetojob: float, distance: Optional[float]) -> bool:
        if distance is None:
            return False
        if distance == 0.0 and timetojob >= self.AFTER_HOUR:
            return True
        if distance > 0.0 and distance <= self.MAX_DISTANCE and timetojob >= self.AFTER_HOUR:
            return True
        return False

    # --- ジョブの受諾 ---
    def _accept_job(self) -> None:
        try:
            if not self.config.DEBUG_MODE:
                self.driver.find_element(By.XPATH, '//*[@id="main"]/div[4]/div[2]/div[2]/div[3]/table/tbody/tr/td[8]/div/a[2]').click()
                sleep(0.5)
                self.driver.find_element(By.XPATH, '//*[@id="main"]/div[4]/div[2]/div[2]/div[3]/table/tbody/tr[2]/td/div/div[4]/div[3]/a[1]').click()
            print(Fore.CYAN + f"{datetime.now()} - ジョブを受諾しました")
        except NoSuchElementException:
            print(Fore.RED + f"{datetime.now()} - ジョブの受諾に失敗しました")

    # --- ジョブの非表示 ---
    def _hide_job(self) -> None:
        try:
            if not self.config.DEBUG_MODE:
                self.driver.find_element(By.XPATH, '//*[@id="main"]/div[4]/div[2]/div[2]/div[3]/table/tbody/tr/td[8]/div/a[3]').click()
                sleep(0.5)
                self.driver.find_element(By.XPATH, '//*[@id="main"]/div[4]/div[2]/div[2]/div[3]/table/tbody/tr[2]/td/div/div/a[1]').click()
            print(Fore.YELLOW + f"{datetime.now()} - ジョブを非表示にしました")
        except NoSuchElementException:
            print(Fore.RED + f"{datetime.now()} - ジョブの非表示に失敗しました")

    # --- メインループ ---
    def run(self) -> None:
        reload_attempts = 0

        while reload_attempts < self.MAX_RELOAD_ATTEMPTS:
            if not self._check_window_title('My jobs summary | TIS Online'):
                self.login()

            jobs_available = self.get_job_count()

            if jobs_available > 0:
                print(Fore.MAGENTA + f"{datetime.now()} - {jobs_available}件のジョブが受諾可能です")

                html = self.driver.page_source
                with open(f"./htmlcopy/page_copy{str(datetime.now()).replace('-','').replace(':','').replace(' ','').replace('.','')}.html", "w", encoding="utf-8") as file:
                    file.write(html)

                elem_table = self.driver.find_element(By.XPATH, '//*[@id="main"]/div[4]/div[2]/div[2]/div[3]/table')
                dfs = pd.read_html(StringIO(elem_table.get_attribute("outerHTML")))
                self.process_jobs(dfs[0], jobs_available)

            reload_attempts += 1

            if not self.config.DEBUG_MODE:
                self.driver.refresh()
                schedule.run_pending()
                sleep(5)


# --- エントリーポイント ---
def main():
    tracker = InterpreterJobTracker()

    tracker.send_email("START")
    schedule.every(1).hours.do(tracker.send_email, mode="MONITORING")

    tracker.run()


if __name__ == "__main__":
    main()