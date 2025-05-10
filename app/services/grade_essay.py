from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from core.config import settings


class Grade(BaseModel):
    essay_title: str = Field(description="The title of the essay")
    grammar: int = Field(default=0, description="Grammar score")
    coherence: int = Field(default=0, description="Coherence score")
    relevance: int = Field(default=0, description="Relevance score")
    total_grade: int = Field(default=0, description="Total grade score over 100")
    explanation: str = Field(default="", description="Explanation of the grade")

class StudentGrades(BaseModel):
    firstName: str = Field(description="The first name of the student.")
    lastName: str = Field(description="The last name of the student.")
    section: str = Field(description="The section of the student.")
    grade: Grade = Field(
        description="The detailed grading breakdown.",
        default_factory=Grade
    )

async def grade_essay(document_text: str, coherence:str, grammar: str, relevance: str , reference:str) -> dict:
    """
    Grade the essay based on the given criteria

    Args:
        document_text(str) : Text of the document to be graded.
        criteria(dict): The criteria that the grade of the essay will be based on.

    Returns:
        dict: The grade of the essay based on the criterias.
    """
    try:
        # Initialize the language model with slightly more creativity to help parsing
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1, api_key=settings.OPENAI_API_KEY)
        
        parser = JsonOutputParser(pydantic_object=StudentGrades)

       
            
        from langchain.prompts import ChatPromptTemplate

        prompt = ChatPromptTemplate.from_template(
            """
            # 📝 ESSAY GRADING ASSISTANT

            You are an expert academic evaluator. Your role is to objectively and constructively assess a student's essay using the criteria below. Your feedback should be detailed, actionable, and backed by specific references to the essay and provided materials.

            ## 📄 ESSAY TO EVALUATE
            ```
            {document_text}
            ```

            ## 📚 REFERENCE MATERIAL
            Use the following reference to assess the essay's relevance:
            {reference}

            ## ✅ GRADING CRITERIA

            Please evaluate the essay on the following dimensions. Provide both a score and a brief justification for each:

            1. **Coherence** ({coherence}): Evaluate the clarity of ideas, organization, transitions between paragraphs, and the overall logical structure supporting the argument.
            
            2. **Grammar** ({grammar}): Analyze grammar usage, sentence construction, punctuation, spelling, and general technical correctness.
            
            3. **Relevance** ({relevance}): Assess how effectively the essay responds to the prompt and integrates key concepts or facts from the reference document.

            ## 🧠 EVALUATION GUIDELINES

            - Cite specific examples from the essay to justify your scores.
            - Be objective, fair, and consistent.
            - Include suggestions for how the student can improve.
            - Provide numerical scores based on the stated definitions and ranges.

            ## 📤 OUTPUT FORMAT

            {format_instructions}
            """
        )


        # Create the processing chain
        chain = prompt | llm | parser
        
        # Invoke the chain with the content
        result = await chain.ainvoke({"document_text": document_text, 
                                      "coherence": coherence ,
                                      "grammar": grammar,
                                      "relevance": relevance,
                                      "reference": reference,
                                      "format_instructions": parser.get_format_instructions()})
    
        return result
    
    except Exception as e:
        # Detailed error logging
        print(f"Data Extraction Error: {e}")
        raise ValueError(f"Failed to extract data: {str(e)}")