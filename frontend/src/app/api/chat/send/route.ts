import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  const body = await request.json();

  const backendPayload = {
    prompt: body.content,
    mode: body.writeupType || 'general',
    file_ids: body.attachments?.filter((a: any) => a.uploaded).map((a: any) => a.url) || [],
    user_params: {
      model: body.model || 'gpt-5',
      user_id: body.user_id || 'anonymous',
      writeupType: body.writeupType || 'general',
      field: body.field || 'general',
      ...body.user_params,
    }
  };

  try {
    const res = await fetch(`${BACKEND_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(backendPayload),
    });

    const text = await res.text();
    if (!res.ok) {
      return NextResponse.json(
        { error: text || 'Backend error' },
        { status: res.status }
      );
    }

    let data: any;
    try { data = JSON.parse(text); } catch { data = {}; }
    if (!data.trace_id) {
      return NextResponse.json(
        { error: 'No trace_id from backend' },
        { status: 502 }
      );
    }

    return NextResponse.json({
      trace_id: data.trace_id,
      status: data.status || 'accepted',
      message: data.message || 'Accepted',
    });
  } catch (e: any) {
    return NextResponse.json(
      { error: e?.message || 'Proxy error' },
      { status: 502 }
    );
  }
}

