from waitress import serve
from flask import Flask, request
import solver
import util_log
from werkzeug.exceptions import InternalServerError
import traceback

app = Flask(__name__)
# app.debug = True


model = None


@app.before_first_request
def loadModel():
    global model
    model = solver.loadModel()


@app.route('/get_language', methods=['POST'])
def get_language():
    text = request.json["text"]
    global model
    return solver.predictLanguage(text, model)


@app.route('/get_language_lst', methods=['POST'])
def get_language_lst():
    texts = request.json["texts"]
    global model
    return solver.predictLanguages(texts, model)


@app.route('/test')
def test():
    global model
    return solver.test(model)


@app.errorhandler(InternalServerError)
def handle_500(e):
    """output the internal error stack in case of unhandled exception"""
    try:
        raise e
    except:
        return traceback.format_exc(), 500


@app.route('/')
def hello():
    return 'languageprediction.svc'


if __name__ == '__main__':
    util_log.init('LanguagePrediction.log')
    # app.run(port=5004)
    serve(app, port=5004)
