import requests
import sys
import psycopg2
from bs4 import BeautifulSoup
from psycopg2 import sql
import pytz, datetime


def insert():
    url = 'https://www.nebraska.gov/courts/calendar/index.cgi'
    myobj = {
        'court': 'C',
        'countyC': 'Douglas',
        'countyD': '',
        'selectRadio': 'date',
        'searchField': '12/14/2020',
        'submitButton': 'Submit'
    }

    # print('Number of arguments:', len(sys.argv), 'arguments.')
    # print('Argument List:', str(sys.argv))

    response = requests.post(url, data=myobj)
    content = str(response.content, "utf-8")
    # content = content.replace('\n', '')
    # content = content.replace('\b', '')
    #
    soup = BeautifulSoup(content, features="html.parser")
    table_rows = soup.find_all('tr')
    print(dir(table_rows))

    conn = psycopg2.connect(
        database="d38s99glk0d3ju",
        user='qyyfzmrmyrjuwn',
        password='d4d572dfbc214774fdf89fac428a4338330d71d072cf41f6e5236d1a8b0007d0',
        host='ec2-54-208-233-243.compute-1.amazonaws.com',
        port='5432'
    )

    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()

    for table_row in table_rows[3:]:
        print(table_row)
        cname, date, time, hearing_type, caption, case_id = [c.get_text() for c in table_row.find_all("td")]
        print(cname)

        local = pytz.timezone("America/Chicago")
        localdatetime = datetime.datetime.strptime(f"{date}T{time}", "%m/%d/%Y T%I:%M%p")
        local_dt = local.localize(localdatetime, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)

        person_insert = sql.SQL(
            "insert into court_cases.court_case ({fields}) values" + f"({cname}, {utc_dt}, {hearing_type}, {case_id}, {caption});").format(
            fields=sql.SQL(",").join([
                sql.Identifier("court_case", "person_id"),
                sql.Identifier("court_case", "court_date"),
                sql.Identifier("court_case", "hearing_type"),
                sql.Identifier("court_case", "case_id"),
                sql.Identifier("court_case", "caption")
            ]),
            field1=sql.Identifier("court_cases", "court_case"),
            # field2=sql.Identifier("court_cases", "person"),
        )

        cursor.execute(person_insert)

        # Preparing SQL queries to INSERT a record into the database.
        # cursor.execute('INSERT INTO court_cases.court_case(person_id, court_date, hearing_type, case_id, caption) VALUES (1, {cname}, {date} {time}, {hearing_type}, {case_id}, {caption})')

    conn.commit()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    insert()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
