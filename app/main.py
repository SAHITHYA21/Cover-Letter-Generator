import streamlit as st
from langchain_community.document_loaders import WebBaseLoader

from chain import Chain
from portfolio import Portfolio
from utils import clean_text


def create_streamlit_app(llm, portfolio, clean_text):
    st.title("📧 Cover Letter Generator")
    url_input = st.text_input("Enter a URL:", value="https://jobs.nike.com/job/R-33460")
    submit_button = st.button("Submit")

    if submit_button:
        try:
            loader = WebBaseLoader([url_input])
            data = clean_text(loader.load().pop().page_content)
            portfolio.load_portfolio()
            jobs = llm.extract_jobs(data)
            jobs = {
                'role': jobs[0]['role'],
                'experience': jobs[0]['experience'],
                'skills': jobs[0]['skills'],
                'description': jobs[0]['description']
            }
            print('\n Jobs outside:',jobs)
            print(type(jobs))
            skills = jobs.get('skills', [])
            print("\n Skills:",skills)
            results = portfolio.collection.query(query_texts=skills, n_results=6)
            relevant_info = [m['section'] + ": " + d for d, m in zip(results['documents'][0], results['metadatas'][0])]
            resume_context = "\n".join(relevant_info)
            links = portfolio.query_links(skills)
            email = llm.write_mail(jobs,resume_context, links)
            st.code(email, language='markdown')
        except Exception as e:
            st.error(f"An Error Occurred: {e}")


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(layout="wide", page_title="Cover Letter Generator", page_icon="📧")
    create_streamlit_app(chain, portfolio, clean_text)