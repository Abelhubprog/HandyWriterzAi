class ActionPlanTemplateTool:
    """A tool for providing a template for an evidence-based action plan."""

    def get_template(self) -> str:
        """
        Returns a template for an evidence-based action plan.

        Returns:
            A string containing the template.
        """
        return """
# Evidence-Based Action Plan

## Learning Goal 1: ...
### Evidence:
...
### Action:
...

## Learning Goal 2: ...
### Evidence:
...
### Action:
...
"""