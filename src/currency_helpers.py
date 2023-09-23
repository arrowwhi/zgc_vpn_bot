import gspread


def check_phone_number(text):
    if type(text) != str or len(text) < 9:
        return ""
    text = text.replace("-", "")
    text = text.replace(" ", "")
    if text[0] != "+":
        return ""
    if not text[1:].isdigit():
        return ""
    return text


def get_rate(e_type=None, count=0):
    gc = gspread.service_account(filename='zgcexchange.json')
    sh = gc.open_by_key("1RBUiezSZDQ0PsKsalG_Susq2APUESeEScXEbQRXW5fA")
    if count == 0 and not e_type:
        q1 = float(sh.sheet1.get('C2')[0][0].replace(',', '.'))
        q2 = float(sh.sheet1.get('B2')[0][0].replace(',', '.'))
        return q1, q2
    t = 'B' if e_type == 'sell' else 'C'
    if count <= 0:
        return 0
    elif 0 < count <= 100:
        t += '4'
    elif 100 < count <= 500:
        t += '5'
    elif 500 < count <= 1000:
        t += '6'
    elif 1000 < count <= 5000:
        t += '7'
    elif 5000 < count < 20000:
        t += '8'
    else:
        t += '9'
    return sh.sheet1.get(t)[0][0].replace(',', '.')


if __name__ == '__main__':
    print(get_rate('sell', 777))
