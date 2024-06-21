import time
import os
from flask import Flask, request, render_template, redirect, url_for, session, json
import speech_recognition as sr
from gtts import gTTS
import pyglet
import imaplib,email
from email.mime.multipart import MIMEMultipart
import re
from send_mail import send_email

file = "good"
i = "0"
addr = ""
password = ""
item =""
subject = ""
body = ""
msg = MIMEMultipart()
newtoaddr = list()
conn = None

#### Defining Flask App
app = Flask(__name__)

app.config['SECRET_KEY'] = '8IR4M7-R3c74GjTHhKzWODaYVHuPGqn4w92DHLqeYJA'

def texttospeech(text, filename):
    filename = filename + '.mp3'
    flag = True
    while flag:
        try:
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(filename)
            flag = False
        except:
            print('Trying again')
    music = pyglet.media.load(filename, streaming = False)
    music.play()
    time.sleep(music.duration)
    os.remove(filename)
    return

def speechtotext(duration):
    response = 'N'
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        music = pyglet.media.load('static/speak.mp3', streaming = False)
        music.play()
        audio = r.listen(source, phrase_time_limit=duration)
    try:
        response = r.recognize_google(audio)
        print("You said:", response)
    except sr.UnknownValueError:
        print("Sorry, could not understand audio.")
    return response

def convert_special_char(text):
    temp=text
    special_chars = ['attherate','dot','underscore','dollar','hash','star','plus','minus','space','dash']
    for character in special_chars:
        while(True):
            pos=temp.find(character)
            if pos == -1:
                break
            else :
                if character == 'attherate':
                    temp=temp.replace('attherate','@')
                elif character == 'dot':
                    temp=temp.replace('dot','.')
                elif character == 'underscore':
                    temp=temp.replace('underscore','_')
                elif character == 'dollar':
                    temp=temp.replace('dollar','$')
                elif character == 'hash':
                    temp=temp.replace('hash','#')
                elif character == 'star':
                    temp=temp.replace('star','*')
                elif character == 'plus':
                    temp=temp.replace('plus','+')
                elif character == 'minus':
                    temp=temp.replace('minus','-')
                elif character == 'space':
                    temp = temp.replace('space', '')
                elif character == 'dash':
                    temp=temp.replace('dash','-')
    return temp

def reply_mail(msg_id, message):
    global i, conn, addr, password
    TO_ADDRESS = message['From']
    flag = True
    while(flag):
        texttospeech("Enter body.", file + i)
        i = i + str(1)
        body = speechtotext(20)
        try:
            texttospeech("Your reply is sending please wait", file + i)
            i = i + str(1)
            send_email(message['Subject'], body, addr, [TO_ADDRESS], password, "reply", msg_id)
            texttospeech("Your reply has been sent successfully.", file + i)
            i = i + str(1)
            flag = False
        except:
            texttospeech("Your reply could not be sent. Do you want to try again? Say confirm or not confirm.", file + i)
            i = i + str(1)
            act = speechtotext(3)
            act = act.lower()
            if act != 'confirm':
                flag = False

def get_body(msg):
    if msg.is_multipart():
        return get_body(msg.get_payload(0))
    else:
        return msg.get_payload(None, True)

def read_mails(mail_list,folder):
    global s, i
    mail_list.reverse()
    mail_count = 0
    to_read_list = list()
    for item in mail_list:
        result, email_data = conn.fetch(item, '(RFC822)')
        raw_email = email_data[0][1].decode()
        message = email.message_from_string(raw_email)
        To = message['To']
        From = message['From']
        Subject = message['Subject']
        Msg_id = message['Message-ID']
        texttospeech("Email number " + str(mail_count + 1) + ".The mail is from " + From + " to " + To + ".The subject of the mail is " + Subject, file + i)
        i = i + str(1)
        Body = get_body(message)
        Body = Body.decode()
        Body = re.sub('<.*?>', '', Body)
        Body = os.linesep.join([s for s in Body.splitlines() if s])
        if Body != '':
            texttospeech("The Body of mail is "+Body, file + i)
            i = i + str(1)
        else:
            texttospeech("Body is empty.", file + i)
            i = i + str(1)
        to_read_list.append(Msg_id)
        mail_count = mail_count + 1
        if folder == 'inbox':
            texttospeech("Do you want to reply to this mail? Say reply or not reply. ", file + i)
            i = i + str(1)
            ans = speechtotext(3)
            ans = ans.lower()
            if ans == "reply":
                reply_mail(Msg_id, message)
    texttospeech("Email ends here.", file + i)
    i = i + str(1)
       
def search_specific_mail(folder,key,value,foldername):
    global i, conn
    conn.select(folder)
    result, data = conn.search(None,key,'"{}"'.format(value))
    mail_list=data[0].split()
    if len(mail_list) != 0:
        texttospeech("There are " + str(len(mail_list)) + " emails with this email ID.", file + i)
        i = i + str(1)
        read_mails(mail_list,foldername)
    else:
        texttospeech("There are no emails with this email ID.", file + i)
        i = i + str(1)

################## ROUTING FUNCTIONS ##############################

@app.route('/')
def index():
    if session.get('std_logged_in'):
        return render_template('dashboard_student.html')
    return render_template('index.html')
    
@app.route('/speak_index', methods=['GET', 'POST'])
def speak_index():
    global i
    text1 = "Welcome to our Voice Based Email System. say login to continue"
    texttospeech(text1, file + i)
    i = i + str(1)
    say = speechtotext(5)
    data = {
        "say": say
    }
    return json.dumps(data)

@app.route('/login_student', methods=['GET', 'POST'])
def login_student():
    global i, addr, password, conn
    say = "failure"
    if request.method == 'POST':
        input = request.get_json()
        if "email" == input["param"]:
            text1 = "We are now on login page. Login with your email account in order to continue. "
            texttospeech(text1, file + i)
            i = i + str(1)
            flag = True
            while (flag):
                texttospeech("Enter your Email", file + i)
                i = i + str(1)
                addr = speechtotext(10)
                if addr != 'N':
                    texttospeech("You meant " + addr + " say confirm to continue or not confirm to enter again", file + i)
                    i = i + str(1)
                    say = speechtotext(3)
                    if say == 'confirm':
                        flag = False
                else:
                    texttospeech("could not understand what you meant:", file + i)
                    i = i + str(1)
            addr = addr.strip()
            addr = addr.replace(' ', '')
            addr = addr.lower()
            addr = convert_special_char(addr)
            data = {
                "say": "success",
                "email": addr
            }
            return json.dumps(data)
        if "password" == input["param"]:
            flag = True
            while (flag):
                texttospeech("Enter your password", file + i)
                i = i + str(1)
                password = speechtotext(10)
                if password != 'N':
                    texttospeech("You meant " + password + " say confirm to continue or not confirm to speak again", file + i)
                    i = i + str(1)
                    say = speechtotext(3)
                    if say == 'confirm':
                        flag = False
                else:
                    texttospeech("could not understand what you meant:", file + i)
                    i = i + str(1)
            password = password.strip()
            password = password.replace(' ', '')
            password = password.lower()
            password = convert_special_char(password)
            try:
                imap_url = 'imap.gmail.com'
                conn = imaplib.IMAP4_SSL(imap_url)
                conn.login(addr, password)
                texttospeech("You have logged in successfully. You will now be redirected to the dashboard page.", file + i)
                i = i + str(1)
                say = "success"
                session['std_logged_in'] = True
                session['email'] = addr
            except:
                texttospeech("Wrong Credentials. Please try again.", file + i)
                i = i + str(1)
                say = "failure"
            data = {
                "say": say,
                "password": password
            }
            return json.dumps(data)
    return render_template('login_student.html')

@app.route('/compose', methods=['GET', 'POST'])
def compose():
    global i, addr, password, conn, item, subject, body, msg, newtoaddr
    if request.method == 'POST':
        input = request.get_json()
        if "email" == input["param"]:
            text1 = "You have reached the page where you can compose and send an email. "
            texttospeech(text1, file + i)
            i = i + str(1)
            flag = True
            flag1 = True
            toaddr = list()
            while flag1:
                while flag:
                    texttospeech("enter receiver's email address:", file + i)
                    i = i + str(1)
                    to = ""
                    to = speechtotext(15)
                    if to != 'N':
                        texttospeech("You meant " + to + " say confirm to continue or not confirm to speak again", file + i)
                        i = i + str(1)
                        say = speechtotext(5)
                        if say == 'confirm':
                            toaddr.append(to)
                            flag = False
                    else:
                        texttospeech("could not understand what you meant", file + i)
                        i = i + str(1)
                texttospeech("Do you want to enter more recipients ? say confirm to continue or not confirm", file + i)
                i = i + str(1)
                say1 = speechtotext(3)
                if say1 == 'not confirm':
                    flag1 = False
                flag = True
            for item in toaddr:
                item = item.strip()
                item = item.replace(' ', '')
                item = item.lower()
                item = convert_special_char(item)
                newtoaddr.append(item)
            return json.dumps({"data": newtoaddr})
        if "subject" == input["param"]:
            flag = True
            while (flag):
                texttospeech("enter subject", file + i)
                i = i + str(1)
                subject = speechtotext(10)
                if subject == 'N':
                    texttospeech("could not understand what you meant", file + i)
                    i = i + str(1)
                else:
                    flag = False
            return json.dumps({"data": subject})
        if "body" == input["param"]:
            flag = True
            while flag:
                texttospeech("enter body of the mail", file + i)
                i = i + str(1)
                body = speechtotext(20)
                if body == 'N':
                    texttospeech("could not understand what you meant", file + i)
                    i = i + str(1)
                else:
                    flag = False
            try:
                send_email(subject, body, addr, newtoaddr, password, "", "")
                texttospeech("Your email has been sent successfully. You will now be redirected to the dashboard page.", file + i)
                i = i + str(1)
            except:
                texttospeech("Sorry, your email failed to send. please try again. You will now be redirected to the the compose page again.", file + i)
                i = i + str(1)
                return json.dumps({"result": "failure", "data": ""})
            return json.dumps({'result' : 'success', "data": body})
    return render_template('compose.html')

@app.route('/inbox', methods=['GET', 'POST'])
def inbox():
    global i, addr, password, conn
    if request.method == 'POST':
        conn.select('"INBOX"')
        result, data = conn.search(None, '(UNSEEN)')
        unread_list = data[0].split()
        no = len(unread_list)
        result1, data1 = conn.search(None, "ALL")
        mail_list = data1[0].split()
        text = "You have reached your inbox. There are " + str(len(mail_list)) + " total mails in your inbox. You have " + str(no) + " unread emails" + ". To read unread emails say unread. To search a specific email say search. To go back to the dashboard page say dashboard. To logout say logout."
        texttospeech(text, file + i)
        i = i + str(1)
        flag = True
        while(flag):
            act = speechtotext(5)
            act = act.replace(' ', '')
            act = act.lower()
            if act == 'unread':
                flag = False
                if no!=0:
                    read_mails(unread_list, 'inbox')
                else:
                    texttospeech("You have no unread emails.", file + i)
                    i = i + str(1)
            elif act == 'search':
                flag = False
                emailid = ""
                while True:
                    texttospeech("Enter email ID of the person who's email you want to search.", file + i)
                    i = i + str(1)
                    emailid = speechtotext(15)
                    texttospeech("You meant " + emailid + " say confirm to continue or not confirm to speak again", file + i)
                    i = i + str(1)
                    yn = speechtotext(5)
                    yn = yn.lower()
                    if yn == 'confirm':
                        break
                emailid = emailid.strip()
                emailid = emailid.replace(' ', '')
                emailid = emailid.lower()
                emailid = convert_special_char(emailid)
                search_specific_mail('INBOX', 'FROM', emailid, 'inbox')

            elif act == 'dashboard':
                texttospeech("You will now be redirected to the dashboard page.", file + i)
                i = i + str(1)
                return json.dumps({'result': 'dashboard'})

            elif act == 'logout':
                texttospeech("You have been logged out of your account and now will be redirected back to the home page.", file + i)
                i = i + str(1)
                return json.dumps({'result': 'logout'})
            else:
                texttospeech("Invalid action. Please try again.", file + i)
                i = i + str(1)
            texttospeech("If you wish to do anything else in the inbox of your mail say confirm or else say not confirm.", file + i)
            i = i + str(1)
            ans = speechtotext(3)
            ans = ans.lower()
            if ans == 'confirm':
                flag = True
                texttospeech("Enter your desired action. Say unread, search, dashboard or logout. ", file + i)
                i = i + str(1)
        texttospeech("You will now be redirected to the dashboard page.", file + i)
        i = i + str(1)
        return json.dumps({'result': 'success'})
    elif request.method == 'GET':
        return render_template('inbox.html')

@app.route('/sentbox', methods=['GET', 'POST'])
def sentbox():
    global i, addr, password, conn
    if request.method == 'POST':
        conn.select('"[Gmail]/Sent Mail"')
        result1, data1 = conn.search(None, "ALL")
        mail_list = data1[0].split()
        text = "You have reached your sent mails folder. You have " + str(len(mail_list)) + " mails in your sent mails folder. To search a specific email say search. To go back to the dashboard page say dashboard. To logout say logout."
        texttospeech(text, file + i)
        i = i + str(1)
        flag = True
        while (flag):
            act = speechtotext(5)
            act = act.replace(' ', '')
            act = act.lower()
            if act == 'search':
                flag = False
                emailid = ""
                while True:
                    texttospeech("Enter email ID of receiver.", file + i)
                    i = i + str(1)
                    emailid = speechtotext(15)
                    texttospeech("You meant " + emailid + " say confirm to continue or not confirm to speak again", file + i)
                    i = i + str(1)
                    yn = speechtotext(5)
                    yn = yn.lower()
                    if yn == 'confirm':
                        break
                emailid = emailid.strip()
                emailid = emailid.replace(' ', '')
                emailid = emailid.lower()
                emailid = convert_special_char(emailid)
                search_specific_mail('"[Gmail]/Sent Mail"', 'TO', emailid,'sent')

            elif act == 'dashboard':
                texttospeech("You will now be redirected to the dashboard page.", file + i)
                i = i + str(1)
                return json.dumps({'result': 'dashboard'})

            elif act == 'logout':
                addr = ""
                password = ""
                texttospeech("You have been logged out of your account and now will be redirected back to the home page.", file + i)
                i = i + str(1)
                return json.dumps({'result': 'logout'})

            else:
                texttospeech("Invalid action. Please try again.", file + i)
                i = i + str(1)

            texttospeech("If you wish to do anything else in the sent mails folder or logout of your mail say confirm or else say not confirm.", file + i)
            i = i + str(1)
            ans = speechtotext(3)
            ans = ans.lower()
            if ans == 'confirm':
                flag = True
                texttospeech("Enter your desired action. Say search, dashboard or logout. ", file + i)
                i = i + str(1)
        texttospeech("You will now be redirected to the dashboard page.", file + i)
        i = i + str(1)
        return json.dumps({'result': 'success'})

    elif request.method == 'GET':
        return render_template('sentbox.html')

@app.route('/student', methods=['POST'])
def student():
    global i
    flag = True
    text1 = "You are on dashboard page now. What would you like to do ?"
    texttospeech(text1, file + i)
    i = i + str(1)
    while(flag):
        texttospeech("To compose an email say compose. To open Inbox folder say inbox. To open Sent folder say sent. To Logout say Logout.", file + i)
        i = i + str(1)
        say = speechtotext(3)
        say = say.replace(' ', '')
        say = say.lower()
        if say == 'compose':
            return json.dumps({'result' : 'compose'})
        elif say == 'inbox':
            return json.dumps({'result' : 'inbox'})
        elif say == 'sent' or say == 'send':
            return json.dumps({'result' : 'sent'})
        elif say == 'logout':
            texttospeech("You have been logged out of your account and now will be redirected back to the home page.", file + i)
            i = i + str(1)
            return json.dumps({'result' : 'logout'})

@app.route("/logout")
def logout():
    global addr, password, conn
    addr = ""
    password = ""
    if conn:
        conn.logout()
    session.pop('std_logged_in', None)
    session.pop('email', None)
    return redirect(url_for('index'))

#### Our main function which runs the Flask App
app.run(debug=True,port=1000)
if __name__ == '__main__':
    pass
