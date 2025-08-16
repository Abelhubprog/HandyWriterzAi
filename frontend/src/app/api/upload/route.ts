import { NextRequest, NextResponse } from 'next/server';

// Resolve backend URL robustly with multiple fallbacks.
const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const authHeader = request.headers.get('authorization') || undefined;

    // Upload to backend files endpoint
    const res = await fetch(`${BACKEND_URL}/api/files/upload`, {
      method: 'POST',
      body: formData,
      headers: {
        // Don't set Content-Type for FormData - browser will set boundary
        ...(authHeader ? { 'Authorization': authHeader } : {}),
      },
    });

    if (!res.ok) {
      const errorText = await res.text();
      console.error(`Backend upload failed: ${res.status} ${res.statusText}`, errorText);
      throw new Error(`Backend upload failed: ${res.status} ${res.statusText}: ${errorText}`);
    }

    const data = await res.json();
    console.log('Backend upload successful:', data);
    return NextResponse.json(data);

  } catch (error) {
    console.error('File upload error:', error);
    
    // Return proper error - no mock fallbacks
    return NextResponse.json(
      { 
        error: error instanceof Error ? error.message : 'Unknown upload error',
        success: false 
      }, 
      { status: 500 }
    );
  }
}
