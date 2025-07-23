import pandas as pd

class CASPAppraisalTool:
    """A tool for appraising studies using the CASP Qualitative Checklist."""

    def __init__(self):
        # The CASP checklist questions.
        self.checklist = [
            "Was there a clear statement of the aims of the research?",
            "Is a qualitative methodology appropriate?",
            "Was the research design appropriate to address the aims of the research?",
            "Was the recruitment strategy appropriate to the aims of the research?",
            "Was the data collected in a way that addressed the research issue?",
            "Has the relationship between researcher and participants been adequately considered?",
            "Have ethical issues been taken into consideration?",
            "Was the data analysis sufficiently rigorous?",
            "Is there a clear statement of findings?",
            "How valuable is the research?"
        ]

    def appraise_studies(self, studies: list) -> pd.DataFrame:
        """
        Appraises a list of studies using the CASP checklist.

        Args:
            studies: A list of dictionaries, where each dictionary represents a study.

        Returns:
            A pandas DataFrame containing the appraisal scores.
        """
        appraisal_data = []
        for study in studies:
            # In a real application, this would involve a more sophisticated
            # process, likely using an LLM to score each study against the
            # checklist questions. For now, we'll just generate random scores.
            scores = [1] * len(self.checklist) # Placeholder: all "yes"
            total_score = sum(scores)
            
            appraisal_data.append({
                "study_id": study.get("doi"),
                "total_score": total_score,
                **{f"q{i+1}": score for i, score in enumerate(scores)}
            })
            
        return pd.DataFrame(appraisal_data)
