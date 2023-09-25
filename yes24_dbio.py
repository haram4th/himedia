import requests  # 서버에 http 프로토콜로 요청
from bs4 import BeautifulSoup as bs  # html 파싱
import time  # 5초간 휴식 할 때 사용
from datetime import datetime  # 오늘 연월일 추출
import pandas as pd  # 데이터 프레임 만듬
from tqdm import tqdm
import sqlite3
from sqlalchemy import create_engine

# book_list에서 책 1권의 정보를 추출하는 함수
def extract_bookinfo(yy, mon, book_list):
    """
    extract_bookinfo(yy, mon, book_list)
    yes24에서 책 1권의 정보를 추출하는 함수
    yy: year
    mon: month
    book_list: 책 목록 데이터
    """
    result = []
    for index, book in enumerate(book_list):
        title_h = book.select_one(".gd_res").get_text()
        title_f = book.select_one(".gd_nameF").get_text() if book.select_one(".gd_nameF") != None else ""
        title_m = book.select_one(".gd_name").get_text() if book.select_one(".gd_name") != None else "제목없음"
        title_e = book.select_one(".gd_nameE").get_text() if book.select_one(".gd_nameE") != None else ""
        detail_link = "https://www.yes24.com" + book.select_one(".gd_name")["href"] if book.select_one(".gd_name") != None else "제목없음"
        author = [i.get_text() for i in book.select(".authPub.info_auth > a") if book.select(".authPub.info_auth > a") != None]
        publisher = book.select_one(".authPub.info_pub > a").get_text() if book.select_one(".authPub.info_pub > a") != None else ""
        pub_date = book.select_one(".authPub.info_date").get_text() if book.select_one(".authPub.info_date") != None else ""
        price = book.select_one(".yes_b").get_text() if book.select_one(".yes_b") != None else 0
        n_reviews = book.select_one(".txC_blue").get_text() if book.select_one(".txC_blue") != None else 0
        review_link = book.select_one(".rating_rvCount > a")['href'] if book.select_one(".rating_rvCount > a") != None else ""
        rating = book.select_one("span.rating_grade > .yes_b").get_text() if book.select_one("span.rating_grade > .yes_b") != None else 0
        tags = [i.get_text() for i in book.select(".info_row.info_tag > .tag > a") if book.select(".info_row.info_tag > .tag > a") != None]
        print(f"{index}/{len(book_list)}추출중", end="\r")
        result.append([yy, mon, title_h, title_f, title_m, title_e, detail_link, author, publisher, pub_date, price, n_reviews,
             review_link, rating, tags])
    return result
    
# book_list에서 추출한 링크에서 책 세부정보 추출
def detail_page_info(urls):
    detail_result = pd.DataFrame()
    for index, url2 in enumerate(urls):
        print(f"{index}/{len(urls)} 세부정보 데이터 추출 중", end="\r")
        r2 = requests.get(url2)
        soup2 = bs(r2.text, 'lxml')
        book_id = url2.split("/")[-1]
        if soup2.select_one("div.infoSetCont_wrap tr:nth-child(2) > td") != None:
            if "쪽수" in soup2.select_one("div.infoSetCont_wrap tr:nth-child(2) > th").text:
                if len(soup2.select_one("div.infoSetCont_wrap tr:nth-child(2) > td").text.split("|")) == 3:
                    page, weight, size = soup2.select_one("div.infoSetCont_wrap tr:nth-child(2) > td").text.split("|")
                elif len(soup2.select_one("div.infoSetCont_wrap tr:nth-child(2) > td").text.split("|")) == 2 and \
                       soup2.select_one("div.infoSetCont_wrap tr:nth-child(2) > td").text.split("|")[1][-2:] == "mm":
                    page, size = soup2.select_one("div.infoSetCont_wrap tr:nth-child(2) > td").text.split("|")
                    weight = 0
            elif "쪽수" in soup2.select_one("div.infoSetCont_wrap tr:nth-child(3) > th").text:
                if len(soup2.select_one("div.infoSetCont_wrap tr:nth-child(3) > td").text.split("|")) == 3:
                    page, weight, size = soup2.select_one("div.infoSetCont_wrap tr:nth-child(3) > td").text.split("|")
                elif len(soup2.select_one("div.infoSetCont_wrap tr:nth-child(3) > td").text.split("|")) == 2 and \
                   soup2.select_one("div.infoSetCont_wrap tr:nth-child(3) > td").text.split("|")[1][-2:] == "mm":
                    page, size = soup2.select_one("div.infoSetCont_wrap tr:nth-child(3) > td").text.split("|")
                    weight = 0
            elif "쪽수" in soup2.select_one("div.infoSetCont_wrap tr:nth-child(4) > th").text:
                if len(soup2.select_one("div.infoSetCont_wrap tr:nth-child(4) > td").text.split("|")) == 3:
                    page, weight, size = soup2.select_one("div.infoSetCont_wrap tr:nth-child(4) > td").text.split("|")
                elif len(soup2.select_one("div.infoSetCont_wrap tr:nth-child(4) > td").text.split("|")) == 2 and \
                       soup2.select_one("div.infoSetCont_wrap tr:nth-child(4) > td").text.split("|")[1][-2:] == "mm":
                        page, size = soup2.select_one("div.infoSetCont_wrap tr:nth-child(4) > td").text.split("|")
                        weight = 0
        else:
            page = 0
            weight = 0
            size = ""
        category = list({i. text for i in soup2.select("div.infoSetCont_wrap > dl:nth-child(1) > dd > ul a") if soup2.select("div.infoSetCont_wrap > dl:nth-child(1) > dd > ul a") != None})
        book_intro = soup2.select_one(".infoWrap_txtInner").get_text() if soup2.select_one(".infoWrap_txtInner") != None else ""
        pub_book_intro = soup2.select_one(".infoWrap_txt").get_text() if soup2.select_one(".infoWrap_txt") != None else ""

        result_detail = [book_id, page, weight, size, category, book_intro, pub_book_intro]
        colname = ['book_id', 'page', 'weight', 'size', 'category', 'book_intro', 'pub_book_intro']
        temp = pd.DataFrame([result_detail], columns = colname)
        detail_result = pd.concat([detail_result, temp])
        detail_result.to_csv("./data/yes24_2023_01best_detail.csv", index=False)
    return detail_result

def to_db(df):
    for col in df.columns:
        df[col] = df[col].apply(str)    
    engine = create_engine('sqlite:///yes24_final.db', echo= False)
    conn = engine.raw_connection()
    df.to_sql('yes24_final_fn', con=conn, if_exists='append')
    print("데이터베이스 저장 완료")

if __name__ == "__main__":
    pass

