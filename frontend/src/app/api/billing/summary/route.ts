import { NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET(request: Request) {
  try {
    // Extract authorization header
    const authHeader = request.headers.get('Authorization');
    
    if (!authHeader) {
      return NextResponse.json({ error: 'Authorization header required' }, { status: 401 });
    }

    // Forward request to backend
    const response = await fetch(`${BACKEND_URL}/billing/summary`, {
      method: 'GET',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      // If backend fails, return mock data for now
      console.warn('Backend billing/summary failed, returning mock data');
      
      return NextResponse.json({
        plan: 'free',
        renew_date: 'N/A',
        usage_usd: 0,
        credits_remaining: 3,
        max_words: 1000,
        features: ['3 documents', 'Basic templates', 'Community support']
      });
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('Billing summary error:', error);
    
    // Return mock data as fallback
    return NextResponse.json({
      plan: 'free',
      renew_date: 'N/A',
      usage_usd: 0,
      credits_remaining: 3,
      max_words: 1000,
      features: ['3 documents', 'Basic templates', 'Community support']
    });
  }
}