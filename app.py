from flask import Flask, request, jsonify ,session
import os
import pandas as pd
from werkzeug.utils import secure_filename
from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
import chromadb
from helper import parse_docs,build_prompt
import os
import uuid
from dotenv import load_dotenv



app = Flask(__name__)

load_dotenv()

os.environ["OPENAI_API_KEY"]=os.getenv('openai_key')
app.secret_key = 'hello'  # Required for session management


UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory user data store
user_data_store = {}

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    print("data: ",data)
    user_id = data.get("user_id")
    password=data.get("password")
    
    print(f"user_id,password: {user_id},{password}")
    if user_id!=123 and password!=123:
        return jsonify({"error": "Username required"}), 400

    # session["session_id"]=uuid.uuid4()
    session["user_id"]=user_id
    # session['username'] = username

    user_data_store[user_id] = {"username": user_id, "data": []}

    return jsonify({"message": "Logged in", "user_id": user_id})

@app.route('/upload_excel', methods=['POST'])
def upload_excel():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request. Use 'file' as form-data key."}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    
    print("Filename: ",file)
    # Check for Excel file format
    if not (file.filename.endswith('.xls') or file.filename.endswith('.xlsx')):
        return jsonify({"error": "File should be in Excel format (.xls or .xlsx)."}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    try:
        xls = pd.ExcelFile(file_path)
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)

            if df.empty:
                return jsonify({"error": f"Malformed Excel: Sheet '{sheet_name}' is empty."}), 400

            empty_cols = [col for col in df.columns if df[col].isna().all()]
            if empty_cols:
                return jsonify({
                    "error": f"Malformed Excel: Sheet '{sheet_name}' contains empty columns: {empty_cols}"
                }), 400

        # Load the file with UnstructuredExcelLoader
        loader = UnstructuredExcelLoader(file_path=file_path)
        documents = loader.load()

        # Split documents into chunks
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        split_docs = splitter.split_documents(documents)

        # Add user_id to metadata
        for doc in split_docs:
            doc.metadata['user_id'] = session.get("user_id")

        # Embed and store in Chroma vector store
        embeddings = OpenAIEmbeddings()
        vectorstore = Chroma.from_documents(
            documents=split_docs,
            embedding=embeddings,
            collection_name="langchain",
            persist_directory="chroma_excel_store"
        )
        vectorstore.persist()

        return jsonify({"message": "File successfully processed and stored in ChromaDB."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
# @app.route('/upload_excel', methods=['POST'])
# def upload_excel():
#     if 'file' not in request.files:
#         return jsonify({"error": "No file part in the request. Use 'file' as form-data key."}), 400

#     file = request.files['file']

#     if file.filename == '':
#         return jsonify({"error": "No selected file"}), 400

#     filename = secure_filename(file.filename)
#     file_path = os.path.join(UPLOAD_FOLDER, filename)
#     file.save(file_path)

#     try:
#         xls = pd.ExcelFile(file_path)
#         for sheet_name in xls.sheet_names:
#             df = pd.read_excel(xls, sheet_name=sheet_name)

#             # 1. Check if the sheet is entirely empty
#             if df.empty:
#                 return jsonify({"error": f"Malformed Excel: Sheet '{sheet_name}' is empty."}), 400

#             # 2. Check for any completely empty columns (all NaNs)
#             empty_cols = [col for col in df.columns if df[col].isna().all()]
#             if empty_cols:
#                 return jsonify({
#                     "error": f"Malformed Excel: Sheet '{sheet_name}' contains empty columns: {empty_cols}"
#                 }), 400

#         # Step 1: Load with UnstructuredExcelLoader
#         loader = UnstructuredExcelLoader(file_path=file_path)
#         documents = loader.load()

#         # Step 2: Contextual chunking
#         splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#         split_docs = splitter.split_documents(documents)

#         ### Add user id 
#         for i in range(len(split_docs)):
#             split_docs[i].metadata['user_id'] = session["user_id"]
#         # Step 3: Embedding model
#         embeddings = OpenAIEmbeddings()

#         # Step 4: Store in Chroma vector DB
#         vectorstore = Chroma.from_documents(
#             collection_name="langchain",
#             documents=split_docs,
#             embedding=OpenAIEmbeddings(),
#             persist_directory="chroma_excel_store"
#         )
#         vectorstore.persist()

#         return jsonify({"message": "File successfully processed and stored in ChromaDB."}), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "running", "message": "Excel upload and ChromaDB service is active."}), 200

### page embedded collection
vectorstore_page = Chroma(collection_name="langchain",embedding_function=OpenAIEmbeddings(), persist_directory=r'chroma_excel_store')
vectorstore_retreiver_page = vectorstore_page.as_retriever(search_kwargs={"k": 10})

@app.route('/query',methods=['POST'])
def get_answer():
    # Get JSON data from the request
    data = request.get_json()
    if data:
        chain = (
            {
                "context": vectorstore_retreiver_page | RunnableLambda(parse_docs),
                "question": RunnablePassthrough(),
            }
            | RunnableLambda(build_prompt)
            | ChatOpenAI(model="gpt-4o-mini")
            | StrOutputParser()
        )
        # data=eval(data)
        # print(type(data))
        resp = chain.invoke(data["message"])  # Replace with your RAG function
        return jsonify({"answer": resp}), 200
    else:
        return jsonify({"error": "No data provided"}), 400

@app.route('/reset',methods=['POST'])
def reset():
    client = chromadb.PersistentClient(path=r'chroma_excel_store')
    collection = client.get_collection(name="langchain")
    # collection = client.get_collection(name="multi_modal_test")
    user_id = session.get('user_id')
    results = collection.get(where={"user_id": int(user_id)})
    ids_to_delete = results["ids"]
    collection.delete(ids_to_delete)
    print(f"Data with {user_id} deleted")
    return {"message":f"Data with userid {user_id} deleted"}

if __name__ == '__main__':
    app.run(debug=True)
