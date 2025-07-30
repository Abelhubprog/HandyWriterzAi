class MermaidDiagramTool:
    """A tool for generating a PRISMA flow diagram in Mermaid syntax."""

    def generate_prisma_diagram(self, prisma_counts: dict) -> str:
        """
        Generates a PRISMA flow diagram in Mermaid syntax.

        Args:
            prisma_counts: A dictionary containing the counts for each stage of the PRISMA process.

        Returns:
            A string containing the Mermaid syntax for the PRISMA flow diagram.
        """
        return f"""
graph TD
    A[Identification] --> B(Records identified from databases<br/>(n = {prisma_counts.get('identified', 0)}))
    A --> C(Records identified from other sources<br/>(n = {prisma_counts.get('other_sources', 0)}))
    
    subgraph Screening
        D(Records screened<br/>(n = {prisma_counts.get('screened', 0)}))
        E(Records excluded<br/>(n = {prisma_counts.get('excluded', 0)}))
        F(Reports sought for retrieval<br/>(n = {prisma_counts.get('retrieval', 0)}))
        G(Reports not retrieved<br/>(n = {prisma_counts.get('not_retrieved', 0)}))
        H(Reports assessed for eligibility<br/>(n = {prisma_counts.get('assessed', 0)}))
        I(Reports excluded<br/>(n = {prisma_counts.get('reports_excluded', 0)}))
    end
    
    J[Included] --> K(Studies included in review<br/>(n = {prisma_counts.get('included', 0)}))
    
    B --> D
    C --> D
    D --> E
    D --> F
    F --> G
    F --> H
    H --> I
    H --> K
"""