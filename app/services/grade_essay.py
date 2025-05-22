from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, create_model
from core.config import settings
from typing import Dict, Any


class DynamicGrade(BaseModel):
    essay_title: str = Field(description="The title of the essay")
    explanation: str = Field(default="", description="Overall explanation of the grade")
    total_grade: int = Field(default=0, description="Total grade score over 100")

async def grade_essay(document_text: str, rubriks: Dict[str, str], reference: str) -> dict:
    """
    Grade the essay based on given dynamic criteria

    Args:
        document_text (str): Text of the document to be graded.
        rubriks (Dict[str, str]): Dictionary containing custom grading criteria and their explanations.
        reference (str): Reference text to compare against.

    Returns:
        dict: The grade of the essay based on the custom criteria.
    """
    try:
        # Create dynamic grade fields
        grade_fields = {
            key: (int, Field(default=0, description=f"Score for {key}"))
            for key in rubriks.keys()
        }
        grade_fields.update({
            "essay_title": (str, Field(description="The title of the essay")),
            "explanation": (str, Field(default="", description="Overall explanation of the grade")),
            "total_grade": (int, Field(default=0, description="Total grade score over 100"))
        })
        
        DynamicGradeModel = create_model("DynamicGradeModel", **grade_fields)
        
        # Create the student grades model dynamically
        DynamicStudentGrades = create_model(
            "DynamicStudentGrades",
            firstName=(str, Field(description="The first name of the student.")),
            lastName=(str, Field(description="The last name of the student.")),
            section=(str, Field(description="The section of the student.")),
            grade=(DynamicGradeModel, Field(description="The detailed grading breakdown."))
        )

        # Initialize the language model
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1, api_key=settings.OPENAI_API_KEY)
        
        parser = JsonOutputParser(pydantic_object=DynamicStudentGrades)

        # Create the criteria section of the prompt dynamically
        criteria_section = "\n".join([
            f"{i+1}. **{key}**: {value}"
            for i, (key, value) in enumerate(rubriks.items())
        ])

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

            Please evaluate the essay on the following dimensions. For each criterion, select ONLY from the grade bands explicitly mentioned in the rubric description for that criterion. Do not use any other scoring system. Justify your choice for each criterion.

            {criteria_section}

            ## 🧠 EVALUATION GUIDELINES

            - **Always highlight what the student did well before mentioning areas for improvement.**
            - **Be empathetic, supportive, and encouraging** in your evaluation. Recognize and praise the student's efforts and progress, even if the essay isn't perfect.
            - If the student's work shows **effort, intent, or partial understanding**, **assign the highest or second-highest band**. Default to higher bands unless the response is almost entirely missing or off-topic.
            - **Only give the lowest score if the response is almost completely missing, off-topic, or shows no understanding at all.** If there is any reasonable attempt, do not assign the lowest band.
            - If the essay is **understandable** and **attempts to answer the question**, **do not penalize minor mistakes** or imperfect organization. Focus on effort and content, not just perfection.
            - **Be generous when in doubt** and align your grading with supportive teacher expectations.
            - **When in doubt, choose the highest appropriate band.** If the work shows effort or partial understanding, do not hesitate to assign the top score.
            - **If you assign less than the highest band for any criterion, clearly explain why the highest band was not given, and ensure the reason is significant (e.g., major misunderstanding or missing content).**
            - For each criterion, **select ONLY from the provided rubric bands** (do not invent or use any other scores). Stick strictly to the rubric to ensure consistency.
            - Do **not provide a numeric score**; **only output the rubric band** for each criterion. Focus on qualitative assessment.
            - **Cite specific examples** from the essay to justify your band selection, but always frame feedback positively and constructively.
            - **If the overall work shows effort, even if imperfect, favor the higher bands.**
            - **Be fair and consistent** in applying the rubric, but always encourage growth and acknowledge progress.
            - **Frame all suggestions for improvement in a positive, growth-oriented way.** Avoid negative or discouraging language.

            ## 📤 OUTPUT FORMAT

            {format_instructions}
            """
        )

        # Create the processing chain   
        chain = prompt | llm | parser
        
        # Invoke the chain with the content
        result = await chain.ainvoke({
            "document_text": document_text,
            "reference": reference,
            "criteria_section": criteria_section,
            "format_instructions": parser.get_format_instructions()
        })
    
        return result
    
    except Exception as e:
        # Detailed error logging
        print(f"Data Extraction Error: {e}")
        raise ValueError(f"Failed to extract data: {str(e)}")