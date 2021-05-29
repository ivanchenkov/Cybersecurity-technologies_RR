from pynput.keyboard import Key, Listener
import time
import sqlite3
import numpy as np
import scipy.stats as sts
from math import sqrt

hold_arr = []
updown_arr = []

start = time.time()
end = time.time()


def on_press(key):
    if key == Key.enter:
        print()
        hold_arr.pop(0)
        updown_arr.pop(0)
        return False
    global start
    global end
    end = time.time()
    try:
        print(key.char, end='')
    except:
        pass
    updown_arr.append(end - start)
    start = time.time()


def on_release(key):
    global start
    global end
    end = time.time()
    hold_arr.append(end - start)
    start = time.time()


def except_errors():
    global hold_arr
    global updown_arr

    pop_arr = []
    tt = abs(sts.t.ppf(0.05, len(hold_arr) - 2))
    for i in range(len(hold_arr)):
        temp_arr = [hold_arr[i] for i in range(len(hold_arr))]
        yi = temp_arr.pop(i)
        Mi = np.sum(temp_arr) / (len(temp_arr))
        Si2 = 0
        for i in range(len(temp_arr)):
            Si2 += (temp_arr[i] - Mi) ** 2
        Si2 = Si2 / (len(temp_arr) - 1)
        Si = Si2 ** 0.5
        tp = abs((yi - Mi) / Si)
        if tp > tt:
            pop_arr.append(i)
    hold_arr = [i for j, i in enumerate(hold_arr) if j not in pop_arr]
    pop_arr = []
    tt = abs(sts.t.ppf(0.05, len(updown_arr) - 2))
    for i in range(len(updown_arr)):
        temp_arr = [updown_arr[i] for i in range(len(updown_arr))]
        yi = temp_arr.pop(i)
        Mi = np.sum(temp_arr) / (len(temp_arr))
        Si2 = 0
        for n in range(len(temp_arr)):
            Si2 += (temp_arr[n] - Mi) ** 2
        Si2 = Si2 / (len(temp_arr) - 1)
        Si = Si2 ** 0.5
        tp = abs((yi - Mi) / Si)
        if tp > tt:
            pop_arr.append(i)
    updown_arr = [i for j, i in enumerate(updown_arr) if j not in pop_arr]


def collect_biometrics():
    global hold_arr
    global updown_arr
    global start
    hold_arr = []
    updown_arr = []
    start = time.time()
    with Listener(on_press=on_press, on_release=on_release) as listener:listener.join()
    except_errors()


def log_in(usernames):
    global hold_arr
    global updown_arr
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('SELECT time from users_hold_time WHERE username = "{}"'.format(usernames))
    all_results = cur.fetchall()
    hold_original_arr = [all_results[i][0] for i in range(len(all_results))]
    cur.execute('SELECT time from users_updown_time WHERE username = "{}"'.format(usernames))
    all_results = cur.fetchall()
    updown_original_arr = [all_results[i][0] for i in range(len(all_results))]
    while True:
        print("Ввод:", end="")
        collect_biometrics()
        hold_check = sts.ttest_ind(hold_arr, hold_original_arr).pvalue
        updown_check = sts.ttest_ind(updown_arr, updown_original_arr).pvalue
        if hold_check > 0.01 and updown_check > 0.03:
            print("\nПОЛЬЗОВАТЕЛЬ РАСПОЗНАН!\n\n")
            time.sleep(1)
            break
        else:
            print("\nПодтвердить пользователя не удалось!\nПопробуй еще раз!")


def save_biometrics(username):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    for elem in hold_arr:
        cur.execute('INSERT INTO users_hold_time VALUES ("{}", {});'.format(username, elem))
    for elem in updown_arr:
        cur.execute('INSERT INTO users_updown_time VALUES ("{}", {});'.format(username, elem))
    conn.commit()


def sign_up(username):
    print("Пользователь отсутствует в системе, регистрация")
    print("Создай биометрическую подпись вводом любого текста\nНапример: The quick brown fox jumps over a lazy "
          "dog\nПо окончании набора, нажми Enter\nВвод:", end='')
    collect_biometrics()
    save_biometrics(username)
    print("\nПользователь создан!")
    time.sleep(1)


def base_check(username):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS "users_hold_time" ("username" TEXT, "time" REAL);')
    cur.execute('CREATE TABLE IF NOT EXISTS "users_updown_time" ("username" TEXT, "time" REAL);')
    conn.commit()
    cur.execute("SELECT username FROM users_hold_time WHERE username == '{}'".format(username))
    all_results = cur.fetchall()
    if len(all_results) != 0:
        log_in(username)
    else:
        sign_up(username)




if __name__ == "__main__":
    username = input("Имя пользователя: ")
    base_check(username)

