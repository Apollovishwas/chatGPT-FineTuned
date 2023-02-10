import argparse
import os
import traceback
import json 

import openai
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, make_response
from flask_compress import Compress
from flask_restful import Api 
from flask_cors import CORS
import polymath

from polymath import (Library, get_completion_with_context, get_embedding,
                        get_max_tokens_for_completion_model)

DEFAULT_CONTEXT_TOKEN_COUNT = 1500
DEFAULT_TOKEN_COUNT = 1000

app = Flask(__name__)
cors = CORS(app)
api = Api(app)
Compress(app)

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
library_filename = os.getenv("LIBRARY_FILENAME")

library = polymath.load_libraries(library_filename, True)
config = polymath.host_config()


@app.route("/", methods=["POST"])
def index():
    print("The config")
    print(config)
    try:
        query = request.args.get('query')
        query_vector = Library.base64_from_vector(
        get_embedding(query))
        decoded = query_vector.decode("utf-8")
        query_embedding = decoded
        query_embedding_model = Library.EMBEDDINGS_MODEL_ID
        count = request.form.get(
            "count", DEFAULT_TOKEN_COUNT, type=int)
        count_type = request.form.get("count_type")
        version = request.form.get('version', -1, type=int)
        
        
        seed = request.form.get('seed')
        
        access_token = request.form.get('access_token', '')
        print("Query embedding model is")
        #print(type(decoded))
        result = library.query(version=1, query_embedding=query_embedding,
                               query_embedding_model=query_embedding_model, count=count)
        print(result.serializable())

        libra = Library(data=((result.serializable())))
        if libra.message:
            print(f'said: ' + library.message)
        else :
            print("no message")
        print(type(jsonify(result.serializable())))
        return (jsonify(result.serializable()))

    except Exception as e:
        return jsonify({
            "errorah": f"{e}\n{traceback.format_exc()}"
        })


@app.route("/", methods=["GET"])
def render_index():
    return render_template("query.html", config=config)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--port', help='Number of the port to run the server on (8080 by default).', default=8080, type=int)
    args = parser.parse_args()
    app.run(host='127.0.0.1', port=args.port, debug=True)




