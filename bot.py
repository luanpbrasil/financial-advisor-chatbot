from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_community.callbacks import get_openai_callback

class FinancialChatbot:
    def __init__(self, df_alloc, df_financial, api_key) -> None:
        self.df_alloc = df_alloc
        self.df_financial = df_financial

        self.prompt_template = PromptTemplate.from_template("""
        You are a financial advisor assistant. Here is the data of the client's portfolios and target allocations.

        Client Portfolio Data:
        {portfolio_data}

        Client Target Allocations:
        {target_allocations}

        Based on the above data, answer the following question:
        {question}
                                                    
        Think as you want, but provide only the final answer
        """)

        self.llm = ChatOpenAI(model='gpt-4o-mini', temperature=0.0, api_key=api_key)
        self.llm_chain = self.prompt_template | self.llm

    def generate_response(self, question):
        # Prepare context
        context = {
            "portfolio_data": self.df_financial.to_string(),
            "target_allocations": self.df_financial.to_string(),
            "question": question
        }

        # Generate the response using LangChain
        with get_openai_callback() as cb:
            response = self.llm_chain.invoke(context)
            total_tokens = cb.total_tokens
            total_cost = cb.total_cost
        
        return response.content, total_tokens, total_cost