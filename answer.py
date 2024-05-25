# from langchain_cohere import ChatCohere
# from langchain_core.messages import HumanMessage
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_community.vectorstores import Chroma
# from langchain_text_splitters import CharacterTextSplitter
# from langchain_community.document_loaders import TextLoader
# from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings


# def answer(question , context_path = 'temp.txt') : 

#     llm = ChatCohere(cohere_api_key="yEknIO6c0in2vwLIkh6JJ9x1WKLke7LPGbfbaiwi")
#     loader = TextLoader('temp.txt')
#     documents = loader.load()
#     text_splitter = CharacterTextSplitter(chunk_size = 1000 , chunk_overlap = 0)

#     embedding_function = SentenceTransformerEmbeddings(model_name = 'all-MiniLM-L6-v2')
#     db = Chroma.from_documents(
#         text_splitter.split_documents(documents) ,
#         embedding_function ,
#         persist_directory = 'chroma_db'
#     )
    

#     # vc = FAISS.from_texts(chunks , embedding = embeddings)
#     similar_docs = db.similarity_search(question)

#     context = ' '.join([
#         element.page_content
#         for element 
#         in similar_docs
#     ])

#     prompt = '''
#     Answer the following question solely based on the context provided

#     Context : {} 

#     Question : {}

#     '''

#     message = [
#         HumanMessage(
#             content = prompt.format(context , question)
#         )
#     ]

#     return llm.invoke(message).content


from langchain_cohere import ChatCohere
from langchain_core.messages import HumanMessage
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import pickle

class VectorNode :

    def __init__(self , page_content , embedding) :

        self.page_content = page_content
        self.embedding = embedding


def create_vectors_from_text(chunks , save = True) :

    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    vc = [
        VectorNode(
            chunk ,
            model.encode(chunk)
        )

        for chunk
        in tqdm(chunks , total = len(chunks))
    ]

    with open('vc.pkl' , 'wb') as out :

        for vec in vc : pickle.dump(
            vec ,
            out ,
            pickle.HIGHEST_PROTOCOL
        )

    return vc

def ret_same_size(vec , query) :

    if vec.shape[0] == query.shape[0] : return (vec , query)
    elif vec.shape[0] > query.shape[0] : return (
        vec ,
        np.hstack([
            query ,
            np.zeros(vec.shape[0] - query.shape[0])
        ])
    )

    else : return (
        np.hstack([
            vec ,
            np.zeros(query.shape[0] - vec.shape[0])
        ]) ,
        query
    )

def similarity_search(query , vc) :

    scores = []

    query = create_vectors_from_text([query] , save = False)[0].embedding
    for vec in vc :

        vec , query = ret_same_size(np.array(vec.embedding) , query)

        score = 1 / (1 + euc_dist(vec , query))

        scores.append(score)

    return scores


def answer(question , context_path = 'temp.txt') : 

    context = open(context_path).read()

    llm = ChatCohere(cohere_api_key="yEknIO6c0in2vwLIkh6JJ9x1WKLke7LPGbfbaiwi")
    
    chunks = [
        context[index : index + 1024]
        for index
        in range(0 , len(context) , 1024)
    ]
    vc = create_vectors_from_text(chunks , save = False)
    scores = similarity_search(query , vc)


    final_context = ''

    for vec , score in zip(vc , scores) :

        if score > 0.45 : final_context += vec.page_content

    prompt = '''
    Answer the following question solely based on the context provided

    Context : {} 

    Question : {}

    '''

    message = [
        HumanMessage(
            content = prompt.format(final_context , question)
        )
    ]

    return llm.invoke(message).content