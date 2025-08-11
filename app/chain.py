import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv()

class Chain:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, model_name="llama-3.1-8b-instant",groq_api_key=os.getenv("GROQ_API_KEY"))

    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of a website.
            Your job is to extract the job postings and return them in JSON format containing the following keys: `role`, `experience`, `skills` and `description`.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res
    
    
    def write_mail(self, job, resume_context, links):
        prompt_coverletter = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}
            
            ### RESUME CONTEXT:
            {resume_context}
            
            ### INSTRUCTION:
            Write a professional cover letter tailored for the above job title and description.
            Match and highlight relevant experience and skills from the resume context.
            Keep the tone formal and enthusiastic.
            Avoid generic clichés. Focus on measurable impacts, technologies used, and specific experiences.
            Address it to "Hiring Manager".
            Sign off with "Sincerely, My name".

            ### COVER LETTER (NO PREAMBLE):
            """
        )
        chain_coverletter = prompt_coverletter | self.llm
        res = chain_coverletter.invoke({"job_description": str(job), "resume_context": str(resume_context), "link_list": links})
        return res.content

if __name__ == "__main__":
    print(os.getenv("GROQ_API_KEY"))