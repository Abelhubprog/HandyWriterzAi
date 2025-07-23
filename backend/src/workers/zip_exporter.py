import zipfile
from io import BytesIO

def create_scorm_manifest(document_title: str) -> str:
    """Creates a basic SCORM 1.2 manifest file (imsmanifest.xml)."""
    return f"""
<manifest identifier="handywriterz-scorm-export" version="1.2"
    xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2"
    xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.imsproject.org/xsd/imscp_rootv1p1p2 imscp_rootv1p1p2.xsd http://www.imsglobal.org/xsd/imsmd_rootv1p2p1 imsmd_rootv1p2p1.xsd http://www.adlnet.org/xsd/adlcp_rootv1p2 adlcp_rootv1p2.xsd">
    <metadata>
        <schema>ADL SCORM</schema>
        <schemaversion>1.2</schemaversion>
    </metadata>
    <organizations default="handywriterz-org">
        <organization identifier="handywriterz-org">
            <title>{document_title}</title>
            <item identifier="item-1" identifierref="resource-1">
                <title>{document_title}</title>
            </item>
        </organization>
    </organizations>
    <resources>
        <resource identifier="resource-1" type="webcontent" adlcp:scormtype="sco" href="index.html">
            <file href="index.html"/>
            <file href="draft.html"/>
            <file href="turnitin_report.pdf"/>
            <file href="lo_report.json"/>
        </resource>
    </resources>
</manifest>
    """.strip()

def create_zip_export(
    document_title: str,
    draft_html: str,
    turnitin_pdf: bytes,
    lo_report_json: str
) -> bytes:
    """Creates a SCORM-compliant ZIP file in memory."""
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add the SCORM manifest
        zip_file.writestr("imsmanifest.xml", create_scorm_manifest(document_title))
        
        # Add a simple index.html to launch the content
        index_html = f'<html><head><title>{document_title}</title></head><body><iframe src="draft.html" width="100%" height="100%"></iframe></body></html>'
        zip_file.writestr("index.html", index_html)

        # Add the main content files
        zip_file.writestr("draft.html", draft_html)
        zip_file.writestr("turnitin_report.pdf", turnitin_pdf)
        zip_file.writestr("lo_report.json", lo_report_json)

    zip_buffer.seek(0)
    return zip_buffer.getvalue()

if __name__ == '__main__':
    # Example Usage
    zip_bytes = create_zip_export(
        document_title="My Awesome Essay",
        draft_html="<h1>Hello World</h1>",
        turnitin_pdf=b"%PDF-1.4...", # Dummy PDF content
        lo_report_json='{"outcome": "achieved"}'
    )
    
    with open("scorm_export.zip", "wb") as f:
        f.write(zip_bytes)
    print("SCORM package saved to scorm_export.zip")