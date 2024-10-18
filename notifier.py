import http.client
import json

conn = http.client.HTTPSConnection("6994xz.api.infobip.com")
payload = json.dumps({
    "messages": [
        {
            "from": "447860099299",
            "to": "916289646928",
            "messageId": "0c427490-a211-4eca-9654-7e65abf71d6d",
            "content": {
                "templateName": "message_test",
                "templateData": {
                    "body": {
                        "placeholders": ["Sayan"],
                        "text": "hello world!"
                    }
                },
                "language": "en"
            }
        }
    ]
})
headers = {
    'Authorization': 'App d9d52f0500e10e958ea9f5af1b245715-3b1ae2ef-00da-4c85-9143-dc58d57cf841',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
conn.request("POST", "/whatsapp/1/message/template", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))