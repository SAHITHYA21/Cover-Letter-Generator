import chromadb
import uuid
import pdfplumber
import os
import re
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv


class Portfolio:
    def __init__(self, file_path="app/resource/Sahithya_ArvetiNagaraju.pdf"):
        self.llm = ChatGroq(temperature=0, model_name="llama-3.1-8b-instant",groq_api_key=os.getenv("GROQ_API_KEY"))
        self.file_path = file_path
        self.resume_data = self.extract_resume_json(self.file_path)
        print(type(self.resume_data))
        self.chroma_client = chromadb.PersistentClient('vectorstore')
        self.collection = self.chroma_client.get_or_create_collection(name="portfolio")

    def extract_text_from_pdf(self, file_path):
        with pdfplumber.open(file_path) as pdf:
            return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
        
    def extract_resume_json(self, file_path):
        prompt_extract = PromptTemplate.from_template(
            """
            ### Resume Text:
            {resume_text}

            Extract the following details from the resume text below and format them as a JSON in this structure:

            resume_data = {{
                "name": "<Full Name in string>",
                "education": [<list of education entries in list of strings for each degree>],
                "experience": ["<For each job, provide a single descriptive string combining company, position, duration, location, and key responsibilities/accomplishments>"],
                "projects": [<For each project, provide a single descriptive string summarizing the project title, technologies used, duration, and outcome or objective>],
                "skills": [<list of skills in list of strings>]
            }}
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE): 
            """
        )
        resume_text = self.extract_text_from_pdf(self.file_path)
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"resume_text": resume_text})
        res = re.sub(r"^```(?:json)?", "", res.content)
        res = res.strip().strip("`")
        print(type(res))
        json_parser = JsonOutputParser()
        res = json_parser.parse(res)
        return res

    def load_portfolio(self):        
        if not self.collection.count():
            for section, items in self.resume_data.items():
                if isinstance(items, list):
                    for item in items:
                        self.collection.add(
                            documents=[item],
                            metadatas={"section": section},
                            ids=[str(uuid.uuid4())]
                        )
                else:
                    print(section, items)
                    self.collection.add(
                        documents=[items],
                        metadatas={"section": section},
                        ids=[str(uuid.uuid4())]
                    )

    def query_links(self, skills):
        return self.collection.query(query_texts=skills, n_results=2).get('metadatas', [])
