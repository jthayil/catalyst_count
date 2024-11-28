import asyncio
import csv
import logging
import time
import threading
from queue import Queue
from asgiref.sync import sync_to_async, async_to_sync
import psycopg2
from psycopg2.extras import execute_values
from accounts.models import Company
from django.conf import settings

batch_q = Queue()


def validate_char(char):
    try:
        return char.encode("utf-8")
    except UnicodeEncodeError:
        return False


def validate_str(input_string):
    return "".join(char for char in input_string if validate_char(char))


def process_cleaned_data():
    db = PG14(settings.DATABASES["default"])
    db.open()

    batch_size = batch_q.qsize()
    new_batch = []
    for i in range(batch_size):
        if not batch_q.empty():
            new_batch.append(batch_q.get())
    
    print(batch_q.qsize())
    
    if len(new_batch) > 0:
        db.execute(
            "INSERT INTO public.accounts_company (name, domain, year_founded, industry, size_range, city, state, country, linkedin_url, current_employee_estimate, total_employee_estimate) VALUES %s",
            new_batch,
        )


async def process_csv_files(fp):
    records = 0
    csv_file = open(fp, "r", encoding="utf-8")
    csv2dict = csv.DictReader(csv_file)

    db = PG14(settings.DATABASES["default"])
    db.open()

    loop = asyncio.get_running_loop()
    asyncio.set_event_loop(loop)

    for row in csv2dict:
        loop.call_soon(process_row_cleaning, row, db)
        records += 1

        if records > 1000:
            loop.call_soon(process_cleaned_data)
            records = 0

    csv_file.close()
    loop.call_soon(process_cleaned_data)


def process_row_cleaning(row, db):
    try:
        name = validate_str(row["name"])
        domain = validate_str(row["domain"])
        domain = None if domain == "" else domain
        year_founded = (
            int(float(row["year founded"])) if row["year founded"] != "" else None
        )
        industry = validate_str(row["industry"])
        size_range = validate_str(row["size range"])

        seg_locality = ["", "", ""]
        if row["locality"] != "":
            seg_locality = row["locality"].split(",")
        city, state, country = (
            validate_str(seg_locality[0]),
            validate_str(seg_locality[1]),
            validate_str(seg_locality[2]) or validate_str(row["country"]),
        )
        linkedin_url = validate_str(row["linkedin url"])
        if row["current employee estimate"]:
            cee = int(row["current employee estimate"])
        else:
            cee = None
        if row["total employee estimate"]:
            tee = int(row["total employee estimate"])
        else:
            tee = None

        batch_q.put(
            (
                name,
                domain,
                year_founded,
                industry,
                size_range,
                city,
                state,
                country,
                linkedin_url,
                cee,
                tee,
            )
        )
        print(batch_q.qsize())

    except Exception as err:
        print(err)


def process_csv_file(fp):
    batch_q = Queue()
    t = threading.Thread(target=save_batches, args=[batch_q], daemon=True)
    t.start()
    async_to_sync(background_upload)(fp, batch_q)


def save_batches(q):
    time.sleep(5)
    while not q.empty():
        batch = q.get()
        Company.objects.bulk_create(batch)
        if q.qsize() > 5:
            t = threading.Thread(target=save_batches, args=[q], daemon=True)
            t.start()


async def background_upload(fp, q):
    with open(fp, "r", encoding="utf-8") as file:
        batch = []
        reader = csv.DictReader(file)

        for row in reader:
            batch.append(
                Company(
                    cid=row[""],
                    name=row["name"],
                    domain=row["domain"],
                    year_founded=row["year founded"] or None,
                    industry=row["industry"],
                    size_range=row["size range"],
                    locality=row["locality"],
                    country=row["country"],
                    linkedin_url=row["linkedin url"],
                    current_employee_estimate=row["current employee estimate"],
                    total_employee_estimate=row["total employee estimate"],
                )
            )

            if len(batch) > 10000:
                q.put(batch)
                batch = []

        q.put(batch)


class PG14:
    """
    Database Class
    """

    connection = None

    def __init__(self, cfg):
        """
        DB Initialization
        """
        self.__server = cfg["HOST"]
        self.__database = cfg["NAME"]
        self.__username = cfg["USER"]
        self.__password = cfg["PASSWORD"]
        self.__port = cfg["PORT"]

    @staticmethod
    def check(cfg):
        if not cfg["host"]:
            raise ValueError("DB Server IP Missing")
        if not cfg["username"]:
            raise ValueError("DB Username Missing")
        if not cfg["password"]:
            raise ValueError("DB Password Missing")
        if not cfg["schema"]:
            raise ValueError("DB Schema Missing")

        return True

    def open(self):
        """Open a database connection"""
        if PG14.connection is None:
            PG14.connection = psycopg2.connect(
                host=self.__server,
                database=self.__database,
                user=self.__username,
                password=self.__password,
                port=self.__port,
                # cursor_factory=RealDictCursor,
            )

    def close(self):
        """Close existing database connection"""
        PG14.connection.close()

    def run_query(self, query):
        data, status = None, False
        try:
            cursor = PG14.connection.cursor()
            cursor.execute(query)
            data = cursor.fetchone()
            cursor.close()
            status = True
        except Exception as err:
            cursor.close()
            logging.error(
                "Err in query: "
                + query
                + ", PG Err code: "
                + str(err.pgcode)
                + ", PG Err msg: "
                + str(err.pgerror)
            )

        return status, data

    def run_query_all(self, query):
        data, status = None, False
        try:
            cursor = PG14.connection.cursor()
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()
            status = True
        except Exception as err:
            cursor.close()
            logging.error(str(err.pgcode) + " : " + str(err.pgerror))

        return status, data

    def execute(self, query, argslist):
        data, status = None, False
        try:
            cursor = PG14.connection.cursor()
            execute_values(cursor, query, argslist)
            PG14.connection.commit()
            cursor.close()
            status = True
        except Exception as err:
            cursor.close()
            print(err)

        return status, data
