import { NextResponse } from 'next/server';

// Resolve backend URL robustly from env, with sensible fallbacks.
// Prefer server-side BACKEND_URL, then public vars, then localhost.
const BACKEND_URL =
  process.env.BACKEND_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  'http://localhost:8000';

export async function POST(request: Request) {
  try {
    const requestBody = await request.json();

    // Validate required fields
    if (!requestBody.prompt || typeof requestBody.prompt !== 'string') {
      return NextResponse.json(
        { error: 'prompt is required and must be a string' },
        { status: 400 }
      );
    }

    // Extract and validate request data
    const {
      prompt,
      mode = 'general',
      file_ids = [],
      user_params = {}
    } = requestBody;

    // Prepare payload for backend - matching the ChatRequest schema
    const backendPayload = {
      prompt,
      mode,
      file_ids: Array.isArray(file_ids) ? file_ids : [],
      user_params: {
        citationStyle: user_params.citationStyle || 'Harvard',
        wordCount: user_params.wordCount || 3000,
        model: user_params.model || 'gemini-2.0-flash-exp',
        user_id: user_params.user_id || 'anonymous',
        writeupType: mode,
        field: user_params.field || 'general',
        ...user_params
      }
    };

    console.log('Sending to backend:', backendPayload);
    console.log('Resolved BACKEND_URL:', BACKEND_URL);

    // Forward request to backend chat service
    const authHeader = request.headers.get('authorization') || undefined;
    const backendResponse = await fetch(`${BACKEND_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...(authHeader ? { 'Authorization': authHeader } : {}),
        // Lightweight identification for optional auth paths
        ...(backendPayload?.user_params?.user_id ? { 'X-User-Id': String(backendPayload.user_params.user_id) } : {})
      },
      body: JSON.stringify(backendPayload),
    });

    const responseText = await backendResponse.text();
    console.log('Backend response:', backendResponse.status, responseText);

    if (!backendResponse.ok) {
      let errorMessage = `Backend error: ${backendResponse.status} ${backendResponse.statusText}`;

      try {
        const errorData = JSON.parse(responseText);
        errorMessage = errorData.detail || errorData.message || errorData.error || errorMessage;
      } catch {
        errorMessage = responseText || errorMessage;
      }

      return NextResponse.json(
        { error: errorMessage },
        { status: backendResponse.status }
      );
    }

    let result;
    try {
      result = JSON.parse(responseText);
    } catch (e) {
      console.error('Failed to parse backend response:', e);
      return NextResponse.json(
        { error: 'Invalid response from backend' },
        { status: 500 }
      );
    }

    // The backend returns trace_id in the response
    // Make sure we have it for streaming
    const trace_id = result.trace_id || result.conversation_id;

    if (!trace_id) {
      console.error('No trace_id in response:', result);
      return NextResponse.json(
        { error: 'Backend did not return a trace_id' },
        { status: 500 }
      );
    }

    // Return the expected format for the frontend
    return NextResponse.json({
      trace_id: trace_id,
      status: result.status || 'accepted',
      message: result.message || 'Request accepted, streaming will begin shortly',
      success: result.success !== false
    });

  } catch (error) {
    console.error('Chat API error:', error);

    if (error instanceof Error) {
      // Handle network errors
      if (error.message.includes('fetch')) {
        return NextResponse.json(
          { error: 'Unable to connect to backend service. Please ensure the backend is running on port 8000.' },
          { status: 503 }
        );
      }

      return NextResponse.json(
        { error: error.message },
        { status: 500 }
      );
    }

    return NextResponse.json(
      { error: 'An unexpected error occurred' },
      { status: 500 }
    );
  }
}
