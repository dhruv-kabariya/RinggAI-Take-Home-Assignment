from openai import OpenAI

from config import OPENAI_API_KEY

class QueryEnhancer:
    _instance = None
    
    def __new__(cls,):
        """
        Create a singleton instance of the class.
        """
        if cls._instance is None:
            cls._instance = super(QueryEnhancer, cls).__new__(cls)
            cls._instance._initialize()  # Initialize the OpenAI client
        return cls._instance
    
    def _initialize(self,):
        """
        Initialize the OpenAI client with the provided API key.
        """
        self.client = OpenAI(api_key=OPENAI_API_KEY)  #

    def enhance_query(self, user_query):
        """
        Enhance the user query by adding more details and generating multiple related questions.
        
        Args:
            user_query (str): The original user query.
        
        Returns:
            str: The enhanced query with additional details and questions.
        """
        # Define the prompt for OpenAI
        system_prompt = """
        Your task is to:
        1. Expand the query with more details to make it more specific and informative.
        2. Generate 3 related questions that could help explore the topic further.
        
        Return the enhanced query followed by the related questions.
        """

        # Call the OpenAI API
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",  # Use the GPT-3.5 model
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f'This is user Query : {user_query}'
                }
            ]
            )

        # Extract the enhanced query and questions from the response
        enhanced_query = response.choices[0].message.content
        # print(enhanced_query)
        return enhanced_query