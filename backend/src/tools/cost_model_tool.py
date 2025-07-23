class CostModelTool:
    """A tool for providing a template for a 3-year cost model."""

    def get_template(self) -> str:
        """
        Returns a template for a 3-year cost model.

        Returns:
            A string containing the template.
        """
        return """
# 3-Year Cost Model

## Year 1
### Upfront Costs:
...
### Recurring Costs:
...

## Year 2
### Recurring Costs:
...

## Year 3
### Recurring Costs:
...
"""