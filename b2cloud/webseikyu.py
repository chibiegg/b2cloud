import datetime
import requests
import datetime
import csv


def _month_date_str_to_date(md_str: str) -> datetime.date:
    # 今日の日付を取得
    today = datetime.date.today()

    # "MM/DD" を month, day に分解
    month_str, day_str = md_str.split("/")
    month = int(month_str)
    day = int(day_str)

    # 今年のその日付を生成
    this_year_date = datetime.date(today.year, month, day)

    # 差分を計算
    diff_this_year = abs((this_year_date - today).days)

    # 来年のその日付
    next_year_date = datetime.date(today.year + 1, month, day)
    diff_next_year = abs((next_year_date - today).days)

    # 昨年のその日付（過去日も検討したい場合）
    last_year_date = datetime.date(today.year - 1, month, day)
    diff_last_year = abs((last_year_date - today).days)

    # もっとも近いものを選ぶ
    candidates = [(this_year_date, diff_this_year), (next_year_date, diff_next_year), (last_year_date, diff_last_year)]

    # 差分が最も小さい日付を返す
    candidates.sort(key=lambda x: x[1])
    return candidates[0][0]


def get_seikyu_csv(session: requests.Session, customer: str):

    url = "https://webseikyu.kuronekoyamato.co.jp/seikyu/service"
    data = {
        "_T": "ua01",
        "_P": "ua01",
        "_A": "DETAIL_OUTPUT",
    }
    resp = session.post(url, data=data)
    resp.raise_for_status()

    today = datetime.date.today()
    from_date = today - datetime.timedelta(days=31)
    url = "https://webseikyu.kuronekoyamato.co.jp/seikyu/service"
    data = {
        "_T": "fi01",
        "_P": "fi01",
        "_A": "CSV",
        "_PNO": "",
        "_BILL_DETAIL_KEY": "",
        "_NEW_OLD_SYUKAN_SEARCH_CLS": "3",
        "_PD_CSTMR": customer,
        "_RB_SEARCH_CONDITION": "1",
        "_TX_ACCEPT_DATE_FROM": from_date.strftime("%Y%m%d"),
        "_TX_ACCEPT_DATE_TO": today.strftime("%Y%m%d"),
        "_PD_PRODUCT_KB": "",
        "_PD_OTHER_SEARCH_CONDITION": "0",
        "_TX_SEARCH_STR": "",
        "_PD_SEARCH_CSTMR_CLS": "",
        "_PD_LIST_DISP_COUNT": "10",
        "_TX_INPUT_PNO": "",
    }

    response = session.post(url, data=data)
    response.raise_for_status()
    reader = csv.reader(response.content.decode("shift-jis").splitlines())
    header = []
    data = []
    for index, rows in enumerate(reader):
        if index == 0:
            header = rows
        else:
            raw = dict(zip(header, rows))
            data.append(
                {
                    "raw": raw,
                    "reception_date": _month_date_str_to_date(raw["受付日"]),
                    "denpyo_no": raw["原票No."].replace("-", ""),
                    "fare_without_tax": int(raw["運賃等合計(税別)"].replace(",", "")),
                }
            )

    return data
