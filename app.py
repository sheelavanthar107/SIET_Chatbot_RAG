import faiss
import numpy as np
from groq import Groq
import pypdf import pdfReader
from sentence_transformers import SentenceTransformer

#load pdfs
def load_pdf (pdf_path):
reader = pdfReader(str(path_path))
mypages = [i.extract_text() or "" for i in reader.pages]
full_text= "\n",join(mypages).strip()
if not full_text:
  raise ValueError("No readable Text Found")
return full_text

#Chunking
def create_chunks(full_text,chunksize=500,overlap=100):
  chunks = []
  start = 0
  while start<len(full_text): #0<1000  400<1000   800<100
    end = start + chunksize   #500  400+500=900
    chunk = full_text[start:end]  #[0:500]  [400:900]  [800:1300]
    if chunk.strip():
      chunks.append(chunk)
    start = end - overlap   #500-100=400   900-100=800   1300-100=1200
  return chunks
#Embeddding:
def build_vectors (chunks,model_name="all-MiniLM-L6-v2"):
  if not chunks:
    raise ValueError("Cannot apply embedding  without chunks")
  embd_model = SentenceTransformer(model_name)
  embd_vectors = embed_model.encode(chunks,convert_to_numpy = True)
  faiss.normalize_L2(embed_vectors)
  index = faiss.IndexFlatIP(embed_vectors.shape[1])
  return index,embed_model

#call loadpdf,chunk,embedding
def load_base (pdf_path= "01_College_Information.pdf"):
  full_text = load_pdf(pdf_path)
  chunks = create_chunks(full_text)
  index,model = build_vector(chunks)
  return ,index,chunks,embed_model

#retrieve
def retrieve_content (question,embed_model,chunks,index,num_chunks=3):
  if not question.strip():
   raise ValueError("Question cannot be blank")
  if num_chunks < 1:
    raise ValueError("Request atleast one or more chunks")

  query_embed = embed_model.encode([question],convert_to_numpy=True)
  faiss.normalize_L2(query_embed)
  sim_scores,vec_indices = index.search(query_embed,min(num_chunks,len(chunks)))
  background = ""
  for i in vec_indices[0]:
    if i !=-1:
    background += chunks[i] + "\n\n"
  return background

  #Ask:
  def ask_rag (question, embed_model,chunks,index,api_key,num_chunks,model_name = "openai/gpt-oss-120b"):
     key = api_key
     if not key:
       raise ValueError("API Key Missing")
      background =  retrieve_content (question, embed_model,chunks,index,num_chunks=3):
      prompt = """You are an professional AI Assitant.
      Answer user question using ONLY document background below.
      Do not invent or assume facts.
      If information not available , simply say Information Missing.
      Document Background :""" + background + "User Question" + question + "Aswer:"
      client = Groq(api_key = key)
      response = client.chat.completions.create(
         model = model_name,
         messages = [ {"role" :"user",
                        "content" : prompt}],
                         temperature = 0.3,
      )
    return response.choices[0].message.content
