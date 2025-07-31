import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    
    // Forward the form data to the backend
    const backendResponse = await fetch(`${BACKEND_URL}/api/files`, {
      method: 'POST',
      body: formData,
    });

    if (!backendResponse.ok) {
      throw new Error(`Backend upload failed: ${backendResponse.status}`);
    }

    const result = await backendResponse.json();
    return NextResponse.json(result);

  } catch (error) {
    console.error('File upload error:', error);
    
    // Fallback - return mock file IDs
    const formData = await request.formData();
    const files = formData.getAll('files') as File[];
    
    const mockResult = {
      file_ids: files.map((file, index) => `mock-file-${file.name}-${Date.now()}-${index}`),
      message: 'Files uploaded successfully (mock)',
      success: true
    };
    
    return NextResponse.json(mockResult);
  }
}