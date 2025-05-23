from flask import Flask, render_template, request, redirect, url_for
from zeep import Client

app = Flask(__name__)
WSDL_URL = 'http://componentb:8000/?wsdl'

@app.route('/', methods=['GET', 'POST'])
def index():
    client = Client(WSDL_URL)
    if request.method == 'POST':
        name = request.form['name']
        dob  = request.form['dob']
        client.service.add_person(name, dob)
        return redirect(url_for('index'))

    raw = client.service.get_persons()
    persons = []
    
    if not raw[0] == 'No records found':
        for entry in raw:
            _id, nm, db = entry.split('|')
            persons.append(dict(id=_id, name=nm, dob=db))
    else:
        persons.append(dict(id=0, name='No records found', dob=''))

    return render_template('index.html', persons=persons)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
