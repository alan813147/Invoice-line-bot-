from flask import Flask
app = Flask(__name__)

from flask import Flask, request, abort
from linebot import  LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextSendMessage, TextMessage

import requests
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


line_bot_api = LineBotApi('S3a477MSb0Fgat/WNpeHyU0dk4Li8vcW4qgPsgn5jZuii86MxvZFucemCR3ILUM+U3+oPxojr+RYyjfeFX7d93njvnhAp4yMf19zV/ZhMkJoLMok0ZWHedvqApoAAl9iQC2guPuc/t6NBDOkS3h5yQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('af3f8e809001e3ce9910e592f5f55efd')

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    mtext = event.message.text
    if (mtext == '@本期中獎號碼'):
        try:
            message = TextSendMessage( 
                monoNum(0)
            )
            line_bot_api.reply_message(event.reply_token,message)
            
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='讀取發票號碼發生錯誤！'))

    elif (mtext == '@前期中獎號碼'):
        try:
            message = TextSendMessage( 
                monoNum(1)+'\n\n'+monoNum(2)
            )
            line_bot_api.reply_message(event.reply_token,message)
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='讀取發票號碼發生錯誤！'))

    elif (mtext == '@輸入發票最後三碼'):
        try:
            message = TextSendMessage(text='請輸入發票最後三碼進行對獎！!')
            line_bot_api.reply_message(event.reply_token,message)
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='讀取發票號碼發生錯誤'))
            
    elif (len(mtext) == 3 and mtext.isdigit()):
        try:
            message = TextSendMessage( 
                comparison(mtext)
            )

            line_bot_api.reply_message(event.reply_token,message)
        except:

            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='讀取發票號碼發生錯誤！'))
    else:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='請輸入3個數字進行對獎！！'))

def monoNum(n):
    content = requests.get('http://invoice.etax.nat.gov.tw/invoice.xml')
    tree = ET.fromstring(content.text)  
    items = list(tree.iter(tag='item')) 
    title = items[n][0].text  
    ptext = items[n][3].text 

    ptext = ptext.replace('<p>','').replace('</p>','\n')
    return title + '\n' + ptext[:-1]  
def comparison(mtext):
    content = requests.get('http://invoice.etax.nat.gov.tw/invoice.xml')
    tree = ET.fromstring(content.text)
    items = list(tree.iter(tag='item'))
    ptext = items[0][3].text
    ptext = ptext.replace('<p>','').replace('</p>','')  
    temlist = ptext.split('：')           
    prizelist.append(temlist[1][5:8])
    prizelist.append(temlist[2][5:8])
    for i in range (3):
        prizelist.append(temlist[3][9*i+5:9*i+8])

    if mtext in prizelist:
        message = '恭喜中獎$200,自行核對前五碼有機會中更多\n\n'
        message += monoNum(0)
    else:
        message = '未中獎,輸入下一張發票後三碼'
    return message


if __name__ == '__main__':
    app.run()