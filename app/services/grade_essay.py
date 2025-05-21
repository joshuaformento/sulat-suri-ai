from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, create_model
from core.config import settings
from typing import Dict, Any


class DynamicGrade(BaseModel):
    essay_title: str = Field(description="The title of the essay")
    explanation: str = Field(default="", description="Overall explanation of the grade")
    total_grade: int = Field(default=0, description="Total grade, which is the sum of all criterion scores")

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
            "total_grade": (int, Field(default=0, description="Total grade, which is the sum of all criterion scores"))
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

            - For each criterion, select ONLY from the provided rubric bands in the description (do not invent or use any other scores)
            - Do not provide a numeric score; only output the rubric band for each criterion
            - Cite specific examples from the essay to justify your band selection
            - Be objective, fair, and consistent
            - Include suggestions for how the student can improve

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
        
        # After you get the result from the chain
        grades = result['grade']
        # Exclude non-criterion fields
        criterion_keys = [k for k in grades.keys() if k not in ("essay_title", "explanation", "total_grade")]
        grades['total_grade'] = sum(grades[k] for k in criterion_keys)
        result['grade'] = grades
    
        return result
    
    except Exception as e:
        # Detailed error logging
        print(f"Data Extraction Error: {e}")
        raise ValueError(f"Failed to extract data: {str(e)}")