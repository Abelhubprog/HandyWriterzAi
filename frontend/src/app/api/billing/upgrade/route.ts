import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function POST(request: Request) {
  try {
    const requestBody = await request.json();
    const authHeader = request.headers.get('Authorization');
    
    if (!authHeader) {
      return NextResponse.json({ error: 'Authorization header required' }, { status: 401 });
    }

    const { tier, provider, metadata } = requestBody;

    // Validate required fields
    if (!tier || !provider) {
      return NextResponse.json({ 
        error: 'tier and provider are required' 
      }, { status: 400 });
    }

    // Forward request to backend
    const response = await fetch(`${BACKEND_URL}/billing/upgrade`, {
      method: 'POST',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        tier,
        provider,
        metadata: {
          frontend_version: '1.0.0',
          ...metadata
        }
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return NextResponse.json(
        { 
          success: false,
          error: errorData.detail || errorData.message || 'Upgrade request failed' 
        },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json({
      success: true,
      payment_data: data
    });

  } catch (error) {
    console.error('Billing upgrade error:', error);
    return NextResponse.json(
      { 
        success: false,
        error: 'Internal server error' 
      },
      { status: 500 }
    );
  }
}